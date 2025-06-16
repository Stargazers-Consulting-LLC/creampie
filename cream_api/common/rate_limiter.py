import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Any

from aiohttp import ClientResponse, ClientSession


class RateLimiter:
    def __init__(
        self,
        max_requests: int = 10,
        time_window: float | int = 30,
        session: ClientSession | None = None,
    ) -> None:
        """
        Initialize rate limiter.

        Args:
            max_requests (int): Maximum number of requests allowed in the time window
            time_window (int): Time window in seconds
            session (ClientSession | None): Optional aiohttp session to use
        """
        self.max_requests: int = max_requests
        self.time_window: float = float(time_window)
        self.requests: dict[str, list[datetime]] = {}
        self._session: ClientSession | None = session

    @property
    def session(self) -> ClientSession:
        """Get the current aiohttp session."""
        if self._session is None:
            raise RuntimeError("No aiohttp session set. Use set_session() first.")
        return self._session

    def set_session(self, session: ClientSession) -> None:
        """Set the aiohttp session to use for requests."""
        self._session = session

    async def acquire(self, domain: str) -> None:
        """
        Acquire permission to make a request. If rate limit is exceeded,
        wait until the next request slot becomes available.

        Args:
            domain (str): Domain to rate limit (e.g., 'api.example.com')
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
        """
        Make a rate-limited HTTP request.

        Args:
            method (str): HTTP method (GET, POST, etc.)
            url (str): URL to request
            domain (str): Domain to rate limit
            **kwargs: Additional arguments to pass to aiohttp.ClientSession.request

        Returns:
            ClientResponse: The response from the request

        Raises:
            RuntimeError: If no session is set
        """
        await self.acquire(domain)
        return await self.session.request(method, url, **kwargs)

    @asynccontextmanager
    async def get(
        self, url: str, domain: str, **kwargs: Any
    ) -> AsyncGenerator[ClientResponse, None]:
        """Rate-limited GET request context manager."""
        response = await self.request("GET", url, domain, **kwargs)
        try:
            yield response
        finally:
            response.close()

    @asynccontextmanager
    async def post(
        self, url: str, domain: str, **kwargs: Any
    ) -> AsyncGenerator[ClientResponse, None]:
        """Rate-limited POST request context manager."""
        response = await self.request("POST", url, domain, **kwargs)
        try:
            yield response
        finally:
            response.close()
