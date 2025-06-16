"""Rate limiting functionality for HTTP requests.

This module provides a rate limiter class that can be used to limit the number of requests
made to a specific domain within a given time window. It supports both synchronous and
asynchronous usage patterns.
"""

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Any

from aiohttp import ClientResponse, ClientSession


class RateLimiter:
    """Rate limiter for HTTP requests.

    This class implements a token bucket algorithm to rate limit HTTP requests to specific
    domains. It maintains a sliding window of requests and ensures that the number of
    requests does not exceed the specified limit within the time window.

    Example:
        ```python
        async with aiohttp.ClientSession() as session:
            limiter = RateLimiter(max_requests=10, time_window=30)
            limiter.set_session(session)

            async with limiter.get("https://api.example.com", "api.example.com") as response:
                data = await response.json()
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
        self.requests: dict[str, list[datetime]] = {}
        self._session: ClientSession | None = session

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

    async def acquire(self, domain: str) -> None:
        """Acquire permission to make a request.

        If rate limit is exceeded, wait until the next request slot becomes available.
        This method implements a sliding window rate limiting algorithm.

        Args:
            domain: Domain to rate limit (e.g., 'api.example.com')
        """
        now = datetime.now()

        # Clean up old requests
        if domain in self.requests:
            self.requests[domain] = [
                req_time
                for req_time in self.requests[domain]
                if now - req_time < timedelta(seconds=self.time_window)
            ]
        else:
            self.requests[domain] = []

        # If rate limit is exceeded, wait until the oldest request expires
        if len(self.requests[domain]) >= self.max_requests:
            oldest_request = self.requests[domain][0]
            wait_time = (oldest_request + timedelta(seconds=self.time_window) - now).total_seconds()
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            # Clean up again after waiting
            now = datetime.now()
            self.requests[domain] = [
                req_time
                for req_time in self.requests[domain]
                if now - req_time < timedelta(seconds=self.time_window)
            ]

        # Add current request
        self.requests[domain].append(now)

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
    async def get(
        self, url: str, domain: str, **kwargs: Any
    ) -> AsyncGenerator[ClientResponse, None]:
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
    async def post(
        self, url: str, domain: str, **kwargs: Any
    ) -> AsyncGenerator[ClientResponse, None]:
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
