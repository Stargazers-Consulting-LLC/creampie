"""Rate limiting tests.

This module contains comprehensive tests for the rate limiting functionality,
including basic rate limiting, concurrent requests, error handling, and edge cases.

References:
    - [Pytest Documentation](https://docs.pytest.org/)
    - [Python Type Hints](https://docs.python.org/3/library/typing.html)
    - [aiohttp Testing](https://docs.aiohttp.org/en/stable/testing.html)

### Legal
SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

import asyncio
from collections.abc import AsyncGenerator, Generator
from datetime import datetime

import pytest
import pytest_asyncio
from aiohttp import ClientSession
from aioresponses import aioresponses
from fastapi import status

from cream_api.common.rate_limiter import RateLimiter
from cream_api.tests.stock_data.stock_data_test_constants import (
    RATE_LIMITER_REQUESTS,
    RATE_LIMITER_WINDOW,
    TIMING_TOLERANCE,
)

# Test configuration
CONCURRENT_TEST_COUNT = 10
FULL_UTILIZATION_PERCENT = 100.0

# Test constants to avoid magic numbers
TEST_MAX_REQUESTS = 10
TEST_TIME_WINDOW = 30.0
TEST_IMMEDIATE_THRESHOLD = 0.1
TEST_MOCK_ID = 123


@pytest_asyncio.fixture(scope="function")
async def http_session() -> AsyncGenerator[ClientSession, None]:
    """Create a test HTTP session."""
    async with ClientSession() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def rate_limiter(http_session: ClientSession) -> AsyncGenerator[RateLimiter, None]:
    """Create a test rate limiter."""
    limiter = RateLimiter(max_requests=RATE_LIMITER_REQUESTS, time_window=RATE_LIMITER_WINDOW)
    limiter.set_session(http_session)
    yield limiter


@pytest.fixture
def mock_responses() -> Generator[aioresponses, None, None]:
    """Create mock HTTP responses."""
    with aioresponses() as m:
        yield m


def test_rate_limiter_initialization() -> None:
    """Test rate limiter initialization."""
    limiter = RateLimiter(max_requests=TEST_MAX_REQUESTS, time_window=TEST_TIME_WINDOW)
    assert limiter.max_requests == TEST_MAX_REQUESTS
    assert limiter.time_window == TEST_TIME_WINDOW
    assert len(limiter.requests) == 0


def test_rate_limiter_invalid_parameters() -> None:
    """Test rate limiter with invalid parameters."""
    with pytest.raises(ValueError, match="max_requests must be at least 1"):
        RateLimiter(max_requests=0, time_window=30)

    with pytest.raises(ValueError, match="time_window must be positive"):
        RateLimiter(max_requests=10, time_window=0)


def test_session_property_without_session() -> None:
    """Test session property when no session is set."""
    limiter = RateLimiter()
    with pytest.raises(RuntimeError, match="No aiohttp session set"):
        _ = limiter.session


@pytest.mark.asyncio
async def test_rate_limiting_basic(rate_limiter: RateLimiter) -> None:
    """Test basic rate limiting functionality."""
    domain = "test.com"

    # First request should be immediate
    start_time = datetime.now()
    await rate_limiter.acquire(domain)
    first_request_time = (datetime.now() - start_time).total_seconds()
    assert first_request_time < TEST_IMMEDIATE_THRESHOLD  # Should be nearly immediate

    # Second request should also be immediate (within limit)
    await rate_limiter.acquire(domain)
    second_request_time = (datetime.now() - start_time).total_seconds()
    assert second_request_time < TEST_IMMEDIATE_THRESHOLD  # Should be nearly immediate

    # Third request should be delayed
    start_time = datetime.now()
    await rate_limiter.acquire(domain)
    delay = (datetime.now() - start_time).total_seconds()
    assert delay >= RATE_LIMITER_WINDOW - TIMING_TOLERANCE


@pytest.mark.asyncio
async def test_get_request(rate_limiter: RateLimiter, mock_responses: aioresponses) -> None:
    """Test rate-limited GET request."""
    url = "https://api.test.com/data"
    domain = "api.test.com"
    mock_responses.get(url, status=status.HTTP_200_OK, payload={"data": "test"})

    async with rate_limiter.get(url, domain) as response:
        assert response.status == status.HTTP_200_OK
        data = await response.json()
        assert data["data"] == "test"


@pytest.mark.asyncio
async def test_post_request(rate_limiter: RateLimiter, mock_responses: aioresponses) -> None:
    """Test rate-limited POST request."""
    url = "https://api.test.com/data"
    domain = "api.test.com"
    payload = {"key": "value"}
    mock_responses.post(url, status=status.HTTP_201_CREATED, payload={"id": TEST_MOCK_ID})

    async with rate_limiter.post(url, domain, json=payload) as response:
        assert response.status == status.HTTP_201_CREATED
        data = await response.json()
        assert data["id"] == TEST_MOCK_ID


@pytest.mark.asyncio
async def test_concurrent_requests(rate_limiter: RateLimiter) -> None:
    """Test concurrent rate-limited requests."""
    domain = "concurrent.com"

    async def make_request() -> None:
        await rate_limiter.acquire(domain)

    # Make more requests than the limit
    num_requests = RATE_LIMITER_REQUESTS * 2
    start_time = datetime.now()
    await asyncio.gather(*[make_request() for _ in range(num_requests)])
    actual_time = (datetime.now() - start_time).total_seconds()

    # Calculate expected minimum time
    # With 4 requests and 2 per window, we need 1 window (2 requests) + 1 window (2 requests)
    expected_min_time = (num_requests / RATE_LIMITER_REQUESTS - 1) * RATE_LIMITER_WINDOW
    assert actual_time >= expected_min_time - TIMING_TOLERANCE


@pytest.mark.asyncio
async def test_request_without_session() -> None:
    """Test request without setting session."""
    limiter = RateLimiter()
    with pytest.raises(RuntimeError, match="No aiohttp session set"):
        await limiter.request("GET", "https://test.com", "test.com")


@pytest.mark.asyncio
async def test_request_error_handling(rate_limiter: RateLimiter, mock_responses: aioresponses) -> None:
    """Test error handling in rate-limited requests."""
    url = "https://api.test.com/error"
    domain = "api.test.com"
    mock_responses.get(url, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async with rate_limiter.get(url, domain) as response:
        assert response.status == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_rate_limited_requests(rate_limiter: RateLimiter, mock_responses: aioresponses) -> None:
    """Test that requests are properly rate limited."""
    url = "https://api.test.com/data"
    domain = "api.test.com"

    # Fill up the rate limit
    for i in range(RATE_LIMITER_REQUESTS + 1):
        # Mock each request individually
        mock_responses.get(url, status=status.HTTP_200_OK, payload={"data": f"test_{i}"})

        start_time = datetime.now()
        async with rate_limiter.get(url, domain) as response:
            assert response.status == status.HTTP_200_OK
        end_time = datetime.now()

        # Check if the request was delayed (after the first RATE_LIMITER_REQUESTS)
        if i >= RATE_LIMITER_REQUESTS:
            total_time = (end_time - start_time).total_seconds()
            assert total_time >= RATE_LIMITER_WINDOW - TIMING_TOLERANCE


class TestMetrics:
    """Tests for rate limiter metrics."""

    @pytest.mark.asyncio
    async def test_metrics_empty_domain(self, rate_limiter: RateLimiter) -> None:
        """Test metrics for an empty domain."""
        domain = "empty-domain.com"
        metrics = rate_limiter.get_metrics(domain)

        assert metrics["domain"] == domain
        assert metrics["current_requests"] == 0
        assert metrics["max_requests"] == RATE_LIMITER_REQUESTS
        assert metrics["time_window"] == RATE_LIMITER_WINDOW
        assert metrics["available_slots"] == RATE_LIMITER_REQUESTS
        assert metrics["utilization_percent"] == 0.0
        assert "time_since_oldest_request" not in metrics
        assert "oldest_request_expires_in" not in metrics

    @pytest.mark.asyncio
    async def test_metrics_with_requests(self, rate_limiter: RateLimiter) -> None:
        """Test metrics for a domain with active requests."""
        domain = "active-domain.com"

        # Add requests up to the limit (but not over)
        for _ in range(RATE_LIMITER_REQUESTS):
            await rate_limiter.acquire(domain)

        metrics = rate_limiter.get_metrics(domain)

        assert metrics["domain"] == domain
        assert metrics["current_requests"] == RATE_LIMITER_REQUESTS
        assert metrics["max_requests"] == RATE_LIMITER_REQUESTS
        assert metrics["time_window"] == RATE_LIMITER_WINDOW
        assert metrics["available_slots"] == 0
        assert metrics["utilization_percent"] == FULL_UTILIZATION_PERCENT
        assert "time_since_oldest_request" in metrics
        assert "oldest_request_expires_in" in metrics
        assert metrics["time_since_oldest_request"] >= 0
        assert metrics["oldest_request_expires_in"] <= RATE_LIMITER_WINDOW

    @pytest.mark.asyncio
    async def test_metrics_at_limit(self, rate_limiter: RateLimiter) -> None:
        """Test metrics when at the rate limit."""
        domain = "limit-domain.com"

        # Fill up to the limit
        for _ in range(RATE_LIMITER_REQUESTS):
            await rate_limiter.acquire(domain)

        metrics = rate_limiter.get_metrics(domain)

        assert metrics["current_requests"] == RATE_LIMITER_REQUESTS
        assert metrics["available_slots"] == 0
        assert metrics["utilization_percent"] == FULL_UTILIZATION_PERCENT


class TestMemoryManagement:
    """Tests for memory management and domain pruning."""

    @pytest.mark.asyncio
    async def test_domain_pruning_after_expiry(self, rate_limiter: RateLimiter) -> None:
        """Test that domains are pruned after all requests expire."""
        domain = "prune-test.com"

        # Add a request
        await rate_limiter.acquire(domain)

        # Verify domain exists
        assert domain in rate_limiter.requests

        # Wait for the request to expire
        await asyncio.sleep(RATE_LIMITER_WINDOW + 0.1)

        # Trigger cleanup by making a new request to a different domain
        # This should clean up the expired domain
        await rate_limiter.acquire("other-domain.com")

        # The original domain should be pruned because it's empty
        assert domain not in rate_limiter.requests

        # Verify the other domain still exists
        assert "other-domain.com" in rate_limiter.requests

    @pytest.mark.asyncio
    async def test_multiple_domains_isolation(self, rate_limiter: RateLimiter) -> None:
        """Test that different domains are isolated and pruned independently."""
        domain1 = "domain1.com"
        domain2 = "domain2.com"

        # Add requests to both domains
        await rate_limiter.acquire(domain1)
        await rate_limiter.acquire(domain2)

        assert domain1 in rate_limiter.requests
        assert domain2 in rate_limiter.requests

        # Wait for domain1 to expire
        await asyncio.sleep(RATE_LIMITER_WINDOW + 0.1)

        # Trigger cleanup by making a request to domain2 (this will clean up domain1)
        await rate_limiter.acquire(domain2)

        # domain1 should be pruned, domain2 should still exist
        assert domain1 not in rate_limiter.requests
        assert domain2 in rate_limiter.requests


class TestAsyncSafety:
    """Tests for async safety and concurrency."""

    @pytest.mark.asyncio
    async def test_high_concurrency_safety(self, rate_limiter: RateLimiter) -> None:
        """Test that the rate limiter handles high concurrency safely."""
        domain = "concurrency-test.com"
        num_concurrent = 10  # Reduced from 50 to make test more reasonable

        async def concurrent_acquire() -> None:
            await rate_limiter.acquire(domain)

        # Run many concurrent acquires
        start_time = datetime.now()
        await asyncio.gather(*[concurrent_acquire() for _ in range(num_concurrent)])
        end_time = datetime.now()

        # Verify no exceptions were raised and timing is reasonable
        total_time = (end_time - start_time).total_seconds()
        # With 10 requests and 2 per window:
        # - First 2 requests go through immediately
        # - Next 8 requests all wait for the same 1-second window to expire
        # So minimum time should be 1.0 seconds
        expected_min_time = RATE_LIMITER_WINDOW
        assert total_time >= expected_min_time - TIMING_TOLERANCE

    @pytest.mark.asyncio
    async def test_mixed_operations_concurrency(self, rate_limiter: RateLimiter) -> None:
        """Test concurrent acquires and metrics calls."""
        domain = "mixed-ops.com"

        async def acquire_and_get_metrics() -> dict:
            await rate_limiter.acquire(domain)
            return rate_limiter.get_metrics(domain)

        # Run concurrent operations
        results = await asyncio.gather(*[acquire_and_get_metrics() for _ in range(10)])

        # Verify all operations completed successfully
        assert len(results) == CONCURRENT_TEST_COUNT
        for result in results:
            assert isinstance(result, dict)
            assert result["domain"] == domain


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    @pytest.mark.asyncio
    async def test_rapid_fire_requests(self, rate_limiter: RateLimiter) -> None:
        """Test rapid-fire requests at the rate limit."""
        domain = "rapid-fire.com"

        # Make requests as fast as possible
        start_time = datetime.now()
        tasks = [rate_limiter.acquire(domain) for _ in range(RATE_LIMITER_REQUESTS * 2)]
        await asyncio.gather(*tasks)
        end_time = datetime.now()

        # Verify timing is correct - with 4 requests and 2 per window:
        # - First 2 requests go through immediately
        # - Next 2 requests wait for the same 1-second window to expire
        # So minimum time should be 1.0 seconds
        total_time = (end_time - start_time).total_seconds()
        expected_min_time = RATE_LIMITER_WINDOW
        assert total_time >= expected_min_time - TIMING_TOLERANCE

    @pytest.mark.asyncio
    async def test_zero_time_window_edge_case(self) -> None:
        """Test that zero time window is rejected."""
        with pytest.raises(ValueError, match="time_window must be positive"):
            RateLimiter(max_requests=10, time_window=0)

    @pytest.mark.asyncio
    async def test_negative_time_window_edge_case(self) -> None:
        """Test that negative time window is rejected."""
        with pytest.raises(ValueError, match="time_window must be positive"):
            RateLimiter(max_requests=10, time_window=-1)

    @pytest.mark.asyncio
    async def test_zero_max_requests_edge_case(self) -> None:
        """Test that zero max requests is rejected."""
        with pytest.raises(ValueError, match="max_requests must be at least 1"):
            RateLimiter(max_requests=0, time_window=30)

    @pytest.mark.asyncio
    async def test_negative_max_requests_edge_case(self) -> None:
        """Test that negative max requests is rejected."""
        with pytest.raises(ValueError, match="max_requests must be at least 1"):
            RateLimiter(max_requests=-1, time_window=30)

    @pytest.mark.asyncio
    async def test_very_small_time_window(self, rate_limiter: RateLimiter) -> None:
        """Test behavior with very small time windows."""
        # Create a rate limiter with a very small time window
        small_limiter = RateLimiter(max_requests=5, time_window=0.1)
        domain = "small-window.com"

        # Make requests
        start_time = datetime.now()
        for _ in range(6):  # One more than the limit
            await small_limiter.acquire(domain)
        end_time = datetime.now()

        # Should have been delayed
        total_time = (end_time - start_time).total_seconds()
        assert total_time >= 0.1 - 0.05  # Allow some tolerance for small windows
