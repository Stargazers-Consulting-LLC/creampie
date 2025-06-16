"""Tests for rate limiting functionality."""

import asyncio
from collections.abc import AsyncGenerator, Generator
from datetime import datetime

import pytest
import pytest_asyncio
from aiohttp import ClientError, ClientSession
from aioresponses import aioresponses
from fastapi import status

from cream_api.common.rate_limiter import RateLimiter
from cream_api.tests.stock_data.test_constants import (
    RATE_LIMITER_REQUESTS,
    RATE_LIMITER_WINDOW,
    TEST_SERVER_BASE_URL,
    TIMING_TOLERANCE,
)

# Test constants
TEST_MAX_REQUESTS = 10
TEST_TIME_WINDOW = 30

pytest_plugins = ("pytest_asyncio",)


@pytest_asyncio.fixture(scope="function")
async def http_session() -> AsyncGenerator[ClientSession, None]:
    """Create an aiohttp session for testing."""
    async with ClientSession() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def rate_limiter(http_session: ClientSession) -> AsyncGenerator[RateLimiter, None]:
    """Create a rate limiter instance for testing."""
    limiter = RateLimiter(max_requests=RATE_LIMITER_REQUESTS, time_window=RATE_LIMITER_WINDOW)
    limiter.set_session(http_session)
    yield limiter


@pytest.fixture
def mock_responses() -> Generator[aioresponses, None, None]:
    """Create a mock response handler."""
    with aioresponses() as m:
        yield m


def test_rate_limiter_initialization() -> None:
    """Test rate limiter initialization with valid parameters."""
    limiter = RateLimiter(max_requests=TEST_MAX_REQUESTS, time_window=TEST_TIME_WINDOW)
    assert limiter.max_requests == TEST_MAX_REQUESTS
    assert limiter.time_window == float(TEST_TIME_WINDOW)


def test_rate_limiter_invalid_parameters() -> None:
    """Test rate limiter initialization with invalid parameters."""
    with pytest.raises(ValueError, match="max_requests must be at least 1"):
        RateLimiter(max_requests=0, time_window=30)

    with pytest.raises(ValueError, match="time_window must be positive"):
        RateLimiter(max_requests=10, time_window=0)


def test_session_property_without_session() -> None:
    """Test accessing session property without setting a session."""
    limiter = RateLimiter()
    with pytest.raises(RuntimeError, match="No aiohttp session set"):
        _ = limiter.session


@pytest.mark.asyncio
async def test_rate_limiting_basic(rate_limiter: RateLimiter) -> None:
    """Test basic rate limiting functionality."""
    domain = "test.com"
    datetime.now()

    # Make requests up to the limit
    for _ in range(RATE_LIMITER_REQUESTS):
        await rate_limiter.acquire(domain)

    # The next request should be delayed
    next_request_start = datetime.now()
    await rate_limiter.acquire(domain)
    end_time = datetime.now()

    # Verify that the delay was approximately the time window
    delay = (end_time - next_request_start).total_seconds()
    assert abs(delay - RATE_LIMITER_WINDOW) <= TIMING_TOLERANCE


@pytest.mark.asyncio
async def test_get_request(rate_limiter: RateLimiter, mock_responses: aioresponses) -> None:
    """Test GET request with rate limiting."""
    url = f"{TEST_SERVER_BASE_URL}/test"
    domain = "test.com"

    # Mock the GET request
    mock_responses.get(url, status=status.HTTP_200_OK, payload={"message": "success"})

    async with rate_limiter.get(url, domain) as response:
        assert response.status == status.HTTP_200_OK
        data = await response.json()
        assert data == {"message": "success"}


@pytest.mark.asyncio
async def test_post_request(rate_limiter: RateLimiter, mock_responses: aioresponses) -> None:
    """Test POST request with rate limiting."""
    url = f"{TEST_SERVER_BASE_URL}/test"
    domain = "test.com"
    data = {"test": "data"}

    # Mock the POST request
    mock_responses.post(url, status=status.HTTP_200_OK, payload={"received": data})

    async with rate_limiter.post(url, domain, json=data) as response:
        assert response.status == status.HTTP_200_OK
        result = await response.json()
        assert result == {"received": data}


@pytest.mark.asyncio
async def test_concurrent_requests(rate_limiter: RateLimiter) -> None:
    """Test handling of concurrent requests."""
    domain = "test.com"
    num_requests = RATE_LIMITER_REQUESTS * 2

    async def make_request() -> None:
        await rate_limiter.acquire(domain)

    # Make concurrent requests
    start_time = datetime.now()
    await asyncio.gather(*[make_request() for _ in range(num_requests)])
    end_time = datetime.now()

    # Verify that the total time is at least (num_requests / max_requests - 1) * time_window
    expected_min_time = (num_requests / RATE_LIMITER_REQUESTS - 1) * RATE_LIMITER_WINDOW
    actual_time = (end_time - start_time).total_seconds()
    assert actual_time >= expected_min_time - TIMING_TOLERANCE


@pytest.mark.asyncio
async def test_request_without_session() -> None:
    """Test making a request without setting a session."""
    limiter = RateLimiter()
    with pytest.raises(RuntimeError, match="No aiohttp session set"):
        await limiter.request("GET", "http://test.com", "test.com")


@pytest.mark.asyncio
async def test_request_error_handling(
    rate_limiter: RateLimiter, mock_responses: aioresponses
) -> None:
    """Test error handling during requests."""
    url = "http://test.com/error"
    domain = "test.com"

    # Mock a failed request
    mock_responses.get(url, exception=ClientError())

    with pytest.raises(ClientError):
        async with rate_limiter.get(url, domain) as response:
            await response.json()


@pytest.mark.asyncio
async def test_rate_limited_requests(
    rate_limiter: RateLimiter, mock_responses: aioresponses
) -> None:
    """Test multiple requests with rate limiting."""
    url = f"{TEST_SERVER_BASE_URL}/test"
    domain = "test.com"

    # Mock multiple successful requests
    for _ in range(RATE_LIMITER_REQUESTS + 1):
        mock_responses.get(url, status=status.HTTP_200_OK, payload={"count": _})

    # Make requests that should be rate limited
    start_time = datetime.now()
    for i in range(RATE_LIMITER_REQUESTS + 1):
        async with rate_limiter.get(url, domain) as response:
            assert response.status == status.HTTP_200_OK
            data = await response.json()
            assert data == {"count": i}
    end_time = datetime.now()

    # Verify that the requests took at least the time window
    total_time = (end_time - start_time).total_seconds()
    assert total_time >= RATE_LIMITER_WINDOW - TIMING_TOLERANCE
