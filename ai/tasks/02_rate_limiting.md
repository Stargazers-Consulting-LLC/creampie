# Step 3: Rate Limiting Implementation

## Overview

This document outlines the requirements and implementation details for a generic rate limiter that can be used with any HTTP API or service. The rate limiter will help prevent API abuse and ensure fair usage by enforcing request limits per domain.

## Tasks

### 1. Create Rate Limiter

In `cream_api/common/rate_limiter.py`:

```python
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from aiohttp import ClientSession, ClientResponse
from contextlib import asynccontextmanager

class RateLimiter:
    def __init__(self, max_requests: int = 100, time_window: int = 60):
        """
        Initialize rate limiter.

        Args:
            max_requests (int): Maximum number of requests allowed in the time window
            time_window (int): Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: Dict[str, list] = {}
        self._session: Optional[ClientSession] = None

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
        Acquire permission to make a request.

        Args:
            domain (str): Domain to rate limit (e.g., 'api.example.com')

        Raises:
            RateLimitError: If rate limit is exceeded
        """
        now = datetime.now()

        # Clean up old requests
        if domain in self.requests:
            self.requests[domain] = [
                req_time for req_time in self.requests[domain]
                if now - req_time < timedelta(seconds=self.time_window)
            ]
        else:
            self.requests[domain] = []

        # Check if rate limit is exceeded
        if len(self.requests[domain]) >= self.max_requests:
            oldest_request = self.requests[domain][0]
            retry_after = int((oldest_request + timedelta(seconds=self.time_window) - now).total_seconds())
            raise RateLimitError(retry_after)

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
            RateLimitError: If rate limit is exceeded
            RuntimeError: If no session is set
        """
        await self.acquire(domain)
        return await self.session.request(method, url, **kwargs)

    @asynccontextmanager
    async def get(self, url: str, domain: str, **kwargs: Any):
        """Rate-limited GET request context manager."""
        response = await self.request('GET', url, domain, **kwargs)
        try:
            yield response
        finally:
            response.close()

    @asynccontextmanager
    async def post(self, url: str, domain: str, **kwargs: Any):
        """Rate-limited POST request context manager."""
        response = await self.request('POST', url, domain, **kwargs)
        try:
            yield response
        finally:
            response.close()
```

### 2. Add Rate Limit Exception

In `cream_api/common/exceptions.py`:

```python
class RateLimitError(Exception):
    """Exception raised when rate limit is exceeded."""
    def __init__(self, retry_after: int):
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded. Retry after {retry_after} seconds")
```

### 3. Create Tests

In `cream_api/tests/common/test_rate_limiting.py`:

```python
import pytest
import aiohttp
from datetime import datetime, timedelta
from cream_api.common.exceptions import RateLimitError
from cream_api.common.rate_limiter import RateLimiter

@pytest.fixture
async def http_session():
    async with aiohttp.ClientSession() as session:
        yield session

@pytest.mark.asyncio
async def test_rate_limiter(http_session):
    limiter = RateLimiter(max_requests=2, time_window=1)
    limiter.set_session(http_session)

    # Should allow first two requests
    await limiter.acquire('example.com')
    await limiter.acquire('example.com')

    # Third request should fail
    with pytest.raises(RateLimitError) as exc_info:
        await limiter.acquire('example.com')
    assert exc_info.value.retry_after > 0

@pytest.mark.asyncio
async def test_rate_limiter_per_domain(http_session):
    limiter = RateLimiter(max_requests=2, time_window=1)
    limiter.set_session(http_session)

    # Should allow requests for different domains
    await limiter.acquire('api1.example.com')
    await limiter.acquire('api2.example.com')
    await limiter.acquire('api1.example.com')
    await limiter.acquire('api2.example.com')

    # Third request for either domain should fail
    with pytest.raises(RateLimitError):
        await limiter.acquire('api1.example.com')
    with pytest.raises(RateLimitError):
        await limiter.acquire('api2.example.com')

@pytest.mark.asyncio
async def test_rate_limiter_window(http_session):
    limiter = RateLimiter(max_requests=2, time_window=1)
    limiter.set_session(http_session)

    # Make two requests
    await limiter.acquire('example.com')
    await limiter.acquire('example.com')

    # Wait for window to expire
    await asyncio.sleep(1.1)

    # Should allow new requests after window expires
    await limiter.acquire('example.com')
    await limiter.acquire('example.com')

@pytest.mark.asyncio
async def test_rate_limited_request(http_session):
    limiter = RateLimiter(max_requests=2, time_window=1)
    limiter.set_session(http_session)

    # Make two requests
    async with limiter.get('https://example.com', 'example.com') as response:
        assert response.status == 200
    async with limiter.get('https://example.com', 'example.com') as response:
        assert response.status == 200

    # Third request should fail
    with pytest.raises(RateLimitError):
        async with limiter.get('https://example.com', 'example.com') as response:
            pass
```

### 4. Testing the Implementation

1. Run the test suite:

   ```bash
   pytest cream_api/tests/common/test_rate_limiting.py -v
   ```

2. Example usage:

   ```python
   import asyncio
   import aiohttp
   from cream_api.common.rate_limiter import RateLimiter
   from cream_api.common.exceptions import RateLimitError

   async def main():
       async with aiohttp.ClientSession() as session:
           limiter = RateLimiter(max_requests=100, time_window=60)
           limiter.set_session(session)

           try:
               # Make rate-limited requests to any API
               async with limiter.get('https://api.example.com/data', 'api.example.com') as response:
                   data = await response.json()
                   print(f"Got data: {data}")

               # Make another request to the same domain
               async with limiter.get('https://api.example.com/other', 'api.example.com') as response:
                   data = await response.json()
                   print(f"Got other data: {data}")

           except RateLimitError as e:
               print(f"Rate limit hit: {str(e)}")

   asyncio.run(main())
   ```

### 5. Usage Examples

#### Basic Usage

```python
async with aiohttp.ClientSession() as session:
    limiter = RateLimiter(max_requests=100, time_window=60)
    limiter.set_session(session)

    # Make a rate-limited request
    async with limiter.get('https://api.example.com/data', 'api.example.com') as response:
        data = await response.json()
```

#### Multiple Domains

```python
async with aiohttp.ClientSession() as session:
    limiter = RateLimiter(max_requests=100, time_window=60)
    limiter.set_session(session)

    # Make requests to different domains
    async with limiter.get('https://api1.example.com/data', 'api1.example.com') as response:
        data1 = await response.json()

    async with limiter.get('https://api2.example.com/data', 'api2.example.com') as response:
        data2 = await response.json()
```

#### Custom HTTP Methods

```python
async with aiohttp.ClientSession() as session:
    limiter = RateLimiter(max_requests=100, time_window=60)
    limiter.set_session(session)

    # Make a POST request
    async with limiter.post('https://api.example.com/data', 'api.example.com',
                           json={'key': 'value'}) as response:
        result = await response.json()
```

#### Error Handling

```python
async with aiohttp.ClientSession() as session:
    limiter = RateLimiter(max_requests=2, time_window=60)
    limiter.set_session(session)

    try:
        # Make multiple requests
        for _ in range(3):
            async with limiter.get('https://api.example.com/data', 'api.example.com') as response:
                data = await response.json()
    except RateLimitError as e:
        print(f"Rate limit exceeded. Retry after {e.retry_after} seconds")
```
