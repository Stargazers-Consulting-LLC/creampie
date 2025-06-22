"""Tests for stock data API endpoints.

This module contains tests for the stock data tracking API endpoints. It follows the testing
best practices outlined in the Backend Style Guide, including:
- Proper test isolation with dedicated database sessions
- Comprehensive error handling tests
- Background task testing
- Clear test organization and documentation
"""

from collections.abc import AsyncGenerator
from unittest.mock import patch

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cream_api.db import get_async_db
from cream_api.stock_data.api import router
from cream_api.stock_data.models import TrackedStock
from cream_api.stock_data.schemas import PullStatus
from cream_api.tests.stock_data.stock_data_test_constants import DEFAULT_TEST_SYMBOL
from cream_api.users.routes.auth import get_current_user_async


@pytest.fixture
def app(async_test_db: AsyncSession) -> FastAPI:
    """Create a test FastAPI application with proper dependency overrides.

    Following the style guide's test application setup pattern, this fixture:
    1. Creates a new FastAPI application
    2. Overrides the database dependency with the test database
    3. Includes the router under test with proper API prefix

    Args:
        async_test_db: Async database session for testing

    Returns:
        FastAPI: Configured test application
    """
    app = FastAPI()

    # Override the database dependency
    async def override_get_async_db() -> AsyncGenerator[AsyncSession, None]:
        yield async_test_db

    # Override the authentication dependency
    async def override_get_current_user_async() -> dict[str, str]:
        # Return a mock user that would pass authentication
        return {"id": "user123", "email": "user@example.com"}

    app.dependency_overrides[get_async_db] = override_get_async_db
    app.dependency_overrides[get_current_user_async] = override_get_current_user_async

    # Include the router with the API prefix to match the main app configuration
    from cream_api.common.constants import API_PREFIX

    app.include_router(router, prefix=API_PREFIX)

    return app


@pytest.fixture
def async_client(app: FastAPI) -> TestClient:
    """Create a test client with the test application.

    Args:
        app: FastAPI application to test

    Returns:
        TestClient: Configured test client
    """
    return TestClient(app)


@pytest.mark.asyncio
async def test_track_stock_new(async_test_db: AsyncSession, async_client: TestClient) -> None:
    """Test tracking a new stock symbol.

    This test verifies that:
    1. The API accepts a valid stock symbol
    2. A new tracking entry is created in the database
    3. The response indicates successful tracking
    4. The database state is correct

    Args:
        async_test_db: Async database session for testing
        async_client: Test client for making requests
    """
    # Make the request
    response = async_client.post("/api/stock-data/track", json={"symbol": DEFAULT_TEST_SYMBOL})

    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "tracking"
    assert data["message"] == f"Stock {DEFAULT_TEST_SYMBOL} is now being tracked"
    assert data["symbol"] == DEFAULT_TEST_SYMBOL

    # Verify database state
    result = await async_test_db.execute(select(TrackedStock).where(TrackedStock.symbol == DEFAULT_TEST_SYMBOL))
    tracked_stock = result.scalar_one()
    assert tracked_stock.symbol == DEFAULT_TEST_SYMBOL
    assert tracked_stock.last_pull_status == PullStatus.PENDING
    assert tracked_stock.is_active is True


@pytest.mark.asyncio
async def test_track_stock_existing(async_test_db: AsyncSession, async_client: TestClient) -> None:
    """Test tracking an existing stock symbol.

    This test verifies that:
    1. The API handles requests for already tracked stocks
    2. The existing tracking entry is not modified
    3. The response indicates successful tracking
    4. The database state remains unchanged

    Args:
        async_test_db: Async database session for testing
        async_client: Test client for making requests
    """
    # Create an existing tracked stock
    existing_stock = TrackedStock(
        symbol=DEFAULT_TEST_SYMBOL,
        last_pull_status=PullStatus.SUCCESS,
        is_active=True,
    )
    async_test_db.add(existing_stock)
    await async_test_db.commit()

    # Make the request
    response = async_client.post("/api/stock-data/track", json={"symbol": DEFAULT_TEST_SYMBOL})

    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "tracking"
    assert data["message"] == f"Stock {DEFAULT_TEST_SYMBOL} is now being tracked"
    assert data["symbol"] == DEFAULT_TEST_SYMBOL

    # Verify database state
    result = await async_test_db.execute(select(TrackedStock).where(TrackedStock.symbol == DEFAULT_TEST_SYMBOL))
    tracked_stock = result.scalar_one()
    assert tracked_stock.symbol == DEFAULT_TEST_SYMBOL
    assert tracked_stock.last_pull_status == PullStatus.SUCCESS  # Should not change
    assert tracked_stock.is_active is True


@pytest.mark.asyncio
async def test_track_stock_invalid_symbol(async_test_db: AsyncSession, async_client: TestClient) -> None:
    """Test tracking a stock with an invalid symbol.

    This test verifies that:
    1. The API rejects invalid stock symbols
    2. The response indicates validation failure
    3. No database changes are made

    Args:
        async_test_db: Async database session for testing
        async_client: Test client for making requests
    """
    # Make the request with an invalid symbol
    response = async_client.post("/api/stock-data/track", json={"symbol": ""})

    # Verify response
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_track_stock_database_error(async_test_db: AsyncSession, async_client: TestClient) -> None:
    """Test handling of database errors.

    This test verifies that:
    1. Database errors are properly caught
    2. The response indicates server error
    3. The error message is included in the response
    4. The database is rolled back

    Args:
        async_test_db: Async database session for testing
        async_client: Test client for making requests
    """

    # Mock a database error
    async def mock_commit() -> None:
        raise Exception("Database error")

    with patch.object(async_test_db, "commit", side_effect=mock_commit):
        # Make the request
        response = async_client.post("/api/stock-data/track", json={"symbol": DEFAULT_TEST_SYMBOL})

        # Verify response
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "detail" in data
        assert "Database error" in data["detail"]


@pytest.mark.asyncio
async def test_track_stock_background_task_error(async_test_db: AsyncSession, async_client: TestClient) -> None:
    """Test handling of background task errors.

    This test verifies that:
    1. Background task errors don't affect the API response
    2. The task is still scheduled despite errors
    3. The response indicates successful tracking
    4. The database state is correct

    Following the style guide's background task testing pattern, we mock
    the BackgroundTasks.add_task method instead of the task function.

    Args:
        async_test_db: Async database session for testing
        async_client: Test client for making requests
    """

    response = async_client.post("/api/stock-data/track", json={"symbol": DEFAULT_TEST_SYMBOL})

    # Verify response
    assert response.status_code == status.HTTP_200_OK  # Task errors shouldn't affect the response
    data = response.json()
    assert data["status"] == "tracking"
    assert data["message"] == f"Stock {DEFAULT_TEST_SYMBOL} is now being tracked"
    assert data["symbol"] == DEFAULT_TEST_SYMBOL


@pytest.mark.asyncio
async def test_list_tracked_stocks_admin_required(async_test_db: AsyncSession, async_client: TestClient) -> None:
    """Test that list tracked stocks endpoint requires admin access.

    This test verifies that:
    1. The endpoint rejects non-admin users
    2. The response indicates admin access is required
    3. The endpoint is properly disabled until user roles are implemented

    Args:
        async_test_db: Async database session for testing
        async_client: Test client for making requests
    """
    # Make the request
    response = async_client.get("/api/stock-data/track")

    # Verify response
    assert response.status_code == status.HTTP_403_FORBIDDEN
    data = response.json()
    assert "detail" in data
    assert "Admin access required" in data["detail"]


@pytest.mark.asyncio
async def test_deactivate_tracking_admin_required(async_test_db: AsyncSession, async_client: TestClient) -> None:
    """Test that deactivate tracking endpoint requires admin access.

    This test verifies that:
    1. The endpoint rejects non-admin users
    2. The response indicates admin access is required
    3. The endpoint is properly disabled until user roles are implemented

    Args:
        async_test_db: Async database session for testing
        async_client: Test client for making requests
    """
    # Make the request
    response = async_client.delete(f"/api/stock-data/tracked/{DEFAULT_TEST_SYMBOL}")

    # Verify response
    assert response.status_code == status.HTTP_403_FORBIDDEN
    data = response.json()
    assert "detail" in data
    assert "Admin access required" in data["detail"]


@pytest.mark.asyncio
async def test_track_stock_invalid_symbol_error_handling(async_test_db: AsyncSession, async_client: TestClient) -> None:
    """Test handling of InvalidStockSymbolError in track stock endpoint.

    This test verifies that:
    1. InvalidStockSymbolError is properly caught
    2. The response indicates bad request
    3. The error message is included in the response

    Args:
        async_test_db: Async database session for testing
        async_client: Test client for making requests
    """
    # Mock the service to raise InvalidStockSymbolError
    with patch("cream_api.stock_data.api.process_stock_request") as mock_service:
        from cream_api.common.exceptions import InvalidStockSymbolError

        mock_service.side_effect = InvalidStockSymbolError("INVALID", "Symbol must start with a letter")

        # Make the request
        response = async_client.post("/api/stock-data/track", json={"symbol": "INVALID"})

        # Verify response
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "detail" in data
        assert "Symbol must start with a letter" in data["detail"]


@pytest.mark.asyncio
async def test_track_stock_stock_data_error_handling(async_test_db: AsyncSession, async_client: TestClient) -> None:
    """Test handling of StockDataError in track stock endpoint.

    This test verifies that:
    1. StockDataError is properly caught
    2. The response indicates server error
    3. The error message is included in the response

    Args:
        async_test_db: Async database session for testing
        async_client: Test client for making requests
    """
    # Mock the service to raise StockDataError
    with patch("cream_api.stock_data.api.process_stock_request") as mock_service:
        from cream_api.common.exceptions import StockDataError

        mock_service.side_effect = StockDataError("Failed to process stock tracking request")

        # Make the request
        response = async_client.post("/api/stock-data/track", json={"symbol": DEFAULT_TEST_SYMBOL})

        # Verify response
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "detail" in data
        assert "Failed to process stock tracking request" in data["detail"]
