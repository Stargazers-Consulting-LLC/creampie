import asyncio
from collections.abc import AsyncGenerator
from datetime import datetime

import aiohttp
import pytest
import pytest_asyncio
from aiohttp import ClientSession

from cream_api.common.rate_limiter import RateLimiter

pytest_plugins = ("pytest_asyncio",)

BASE_URL = "http://localhost:8000"  # FastAPI default port
HTTP_OK = 200

ROOT_RESPONSE = {"app": "root"}


@pytest_asyncio.fixture(scope="function")  # type: ignore[misc]
async def http_session() -> AsyncGenerator[ClientSession, None]:
    async with aiohttp.ClientSession() as session:
        yield session


@pytest.mark.asyncio
async def test_rate_limiter(http_session: ClientSession) -> None:
    limiter = RateLimiter(max_requests=2, time_window=1, session=http_session)

    # Should allow first two requests immediately
    start_time = datetime.now()
    await limiter.acquire(BASE_URL)
    await limiter.acquire(BASE_URL)

    # Third request should wait
    await limiter.acquire(BASE_URL)
    end_time = datetime.now()

    # Should have waited at least 1 second
    assert (end_time - start_time).total_seconds() >= limiter.time_window


@pytest.mark.asyncio
async def test_rate_limiter_window(http_session: ClientSession) -> None:
    limiter = RateLimiter(max_requests=2, time_window=1, session=http_session)

    # Make two requests
    await limiter.acquire(BASE_URL)
    await limiter.acquire(BASE_URL)

    # Wait for window to expire
    await asyncio.sleep(1.1)

    # Should allow new requests immediately
    start_time = datetime.now()
    await limiter.acquire(BASE_URL)
    await limiter.acquire(BASE_URL)
    end_time = datetime.now()

    # Should not have waited
    assert (end_time - start_time).total_seconds() < limiter.time_window


@pytest.mark.asyncio
async def test_rate_limited_request(http_session: ClientSession) -> None:
    limiter = RateLimiter(max_requests=2, time_window=1, session=http_session)

    # Make two requests
    async with limiter.get(f"{BASE_URL}/", BASE_URL) as response:
        assert response.status == HTTP_OK
        data = await response.json()
        assert data == ROOT_RESPONSE

    async with limiter.get(f"{BASE_URL}/", BASE_URL) as response:
        assert response.status == HTTP_OK
        data = await response.json()
        assert data == ROOT_RESPONSE

    # Third request should wait but complete
    start_time = datetime.now()
    async with limiter.get(f"{BASE_URL}/", BASE_URL) as response:
        assert response.status == HTTP_OK
        data = await response.json()
        assert data == ROOT_RESPONSE
    end_time = datetime.now()

    # Should have waited at least 1 second
    assert (end_time - start_time).total_seconds() >= limiter.time_window
