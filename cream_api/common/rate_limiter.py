"""Rate limiting functionality for HTTP requests.

This module provides a rate limiter class that can be used to limit the number of requests
made to a specific domain within a given time window. It supports both synchronous and
asynchronous usage patterns.
"""

import asyncio
import logging
from collections import defaultdict, deque
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Any

from aiohttp import ClientResponse, ClientSession

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter for HTTP requests.

    This class implements a sliding window rate limiting algorithm to rate limit HTTP
    requests to specific domains. It maintains a sliding window of requests and ensures
    that the number of requests does not exceed the specified limit within the time window.

    The rate limiter is async-safe and can be used concurrently by multiple async tasks.

    Example:
        ```python
        async with aiohttp.ClientSession() as session:
            limiter = RateLimiter(max_requests=10, time_window=30)
            limiter.set_session(session)

            async with limiter.get("https://api.example.com", "api.example.com") as response:
                data = await response.json()
        ```

    Example with error handling:
        ```python
        try:
            async with limiter.get(url, domain) as response:
                if response.status == 200:
                    data = await response.json()
                else:
                    logger.warning(f"Request failed with status {response.status}")
        except Exception as e:
            logger.error(f"Rate-limited request failed: {e}")
        ```
    """

    def __init__(
        self,
        max_requests: int = 10,
        time_window: float | int = 30,
        session: ClientSession | None = None,
    ) -> None:
        """Initialize rate limiter.

        Args:
            max_requests: Maximum number of requests allowed in the time window
            time_window: Time window in seconds
            session: Optional aiohttp session to use

        Raises:
            ValueError: If max_requests is less than 1 or time_window is less than 0
        """
        if max_requests < 1:
            raise ValueError("max_requests must be at least 1")
        if time_window <= 0:
            raise ValueError("time_window must be positive")

        self.max_requests: int = max_requests
        self.time_window: float = float(time_window)
        self.requests: defaultdict[str, deque[datetime]] = defaultdict(deque)
        self._session: ClientSession | None = session
        # Async lock to protect access to the requests dictionary
        self._lock = asyncio.Lock()

    @property
    def session(self) -> ClientSession:
        """Get the current aiohttp session.

        Returns:
            The current aiohttp ClientSession

        Raises:
            RuntimeError: If no session has been set
        """
        if self._session is None:
            raise RuntimeError("No aiohttp session set. Use set_session() first.")
        return self._session

    def set_session(self, session: ClientSession) -> None:
        """Set the aiohttp session to use for requests.

        Args:
            session: The aiohttp ClientSession to use
        """
        self._session = session

    def _get_oldest_request_for(self, domain: str) -> datetime | None:
        """Get the oldest request timestamp for a domain.

        Args:
            domain: Domain to check

        Returns:
            The oldest request timestamp, or None if no requests exist
        """
        return self.requests[domain][0] if self.requests[domain] else None

    def _remove_expired_requests(self, domain: str, now: datetime) -> None:
        """Remove expired requests for a domain based on the current time."""
        initial_count = len(self.requests[domain])
        while True:
            oldest_request = self._get_oldest_request_for(domain)
            if oldest_request is None or now - oldest_request < timedelta(seconds=self.time_window):
                break
            self.requests[domain].popleft()

        # Prune empty domains to prevent memory bloat
        if not self.requests[domain]:
            del self.requests[domain]
            if initial_count > 0:
                logger.debug(f"Pruned empty domain: {domain}")

    def _cleanup_all_expired_domains(self, now: datetime) -> None:
        """Clean up all expired domains to prevent memory bloat."""
        domains_to_remove = []
        for domain in list(self.requests.keys()):
            self._remove_expired_requests(domain, now)
            # Check if domain was pruned
            if domain not in self.requests:
                domains_to_remove.append(domain)

        # Log cleanup summary
        if domains_to_remove:
            logger.debug(f"Cleaned up {len(domains_to_remove)} expired domains: {domains_to_remove}")

    def get_metrics(self, domain: str) -> dict[str, Any]:
        """Get current metrics for a domain.

        Args:
            domain: Domain to get metrics for

        Returns:
            Dictionary containing current metrics
        """
        now = datetime.now()
        current_requests = len(self.requests.get(domain, deque()))

        metrics = {
            "domain": domain,
            "current_requests": current_requests,
            "max_requests": self.max_requests,
            "time_window": self.time_window,
            "available_slots": max(0, self.max_requests - current_requests),
            "utilization_percent": (current_requests / self.max_requests) * 100 if self.max_requests > 0 else 0,
        }

        if current_requests > 0:
            oldest_request = self._get_oldest_request_for(domain)
            if oldest_request is not None:
                time_since_oldest = (now - oldest_request).total_seconds()
                metrics["time_since_oldest_request"] = time_since_oldest
                metrics["oldest_request_expires_in"] = max(0, self.time_window - time_since_oldest)

        return metrics

    async def acquire(self, domain: str) -> None:
        """Acquire permission to make a request.

        If rate limit is exceeded, wait until the next request slot becomes available.
        This method implements a sliding window rate limiting algorithm.

        Args:
            domain: Domain to rate limit (e.g., 'api.example.com')
        """
        now = datetime.now()

        # Use async lock to protect access to the shared requests dictionary
        async with self._lock:
            # Clean up all expired domains first
            self._cleanup_all_expired_domains(now)

            # Then handle the specific domain
            self._remove_expired_requests(domain, now)

            # Calculate wait time if rate limit is exceeded
            wait_time = 0.0
            if len(self.requests[domain]) >= self.max_requests:
                oldest_request = self._get_oldest_request_for(domain)
                if oldest_request is not None:
                    wait_time = max(0.0, (oldest_request + timedelta(seconds=self.time_window) - now).total_seconds())
                    logger.info(f"Rate limit exceeded for {domain}, waiting {wait_time:.2f}s")

            # Add current request
            self.requests[domain].append(now)

            current_count = len(self.requests[domain])
            logger.debug(f"Request added for {domain}, current count: {current_count}/{self.max_requests}")

        # Sleep outside the lock to avoid blocking other tasks
        if wait_time > 0:
            await asyncio.sleep(wait_time)
            # Re-acquire lock to clean up expired requests after waiting
            async with self._lock:
                now = datetime.now()
                self._cleanup_all_expired_domains(now)

    async def request(self, method: str, url: str, domain: str, **kwargs: Any) -> ClientResponse:
        """Make a rate-limited HTTP request.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: URL to request
            domain: Domain to rate limit
            **kwargs: Additional arguments to pass to aiohttp.ClientSession.request

        Returns:
            The response from the request

        Raises:
            RuntimeError: If no session is set
            aiohttp.ClientError: If the request fails
        """
        await self.acquire(domain)
        return await self.session.request(method, url, **kwargs)

    @asynccontextmanager
    async def get(self, url: str, domain: str, **kwargs: Any) -> AsyncGenerator[ClientResponse, None]:
        """Rate-limited GET request context manager.

        Args:
            url: URL to request
            domain: Domain to rate limit
            **kwargs: Additional arguments to pass to aiohttp.ClientSession.request

        Yields:
            The response from the request

        Example:
            ```python
            async with limiter.get("https://api.example.com", "api.example.com") as response:
                data = await response.json()
            ```
        """
        response = await self.request("GET", url, domain, **kwargs)
        try:
            yield response
        finally:
            response.close()

    @asynccontextmanager
    async def post(self, url: str, domain: str, **kwargs: Any) -> AsyncGenerator[ClientResponse, None]:
        """Rate-limited POST request context manager.

        Args:
            url: URL to request
            domain: Domain to rate limit
            **kwargs: Additional arguments to pass to aiohttp.ClientSession.request

        Yields:
            The response from the request

        Example:
            ```python
            url = "https://api.example.com"
            domain = "api.example.com"
            async with limiter.post(url, domain, json=data) as response:
                result = await response.json()
            ```
        """
        response = await self.request("POST", url, domain, **kwargs)
        try:
            yield response
        finally:
            response.close()
