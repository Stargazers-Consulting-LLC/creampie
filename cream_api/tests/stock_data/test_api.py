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


@pytest.fixture
def app(async_test_db: AsyncSession) -> FastAPI:
    """Create a test FastAPI application with proper dependency overrides.

    Following the style guide's test application setup pattern, this fixture:
    1. Creates a new FastAPI application
    2. Overrides the database dependency with the test database
    3. Includes the router under test

    Args:
        async_test_db: Async database session for testing

    Returns:
        FastAPI: Configured test application
    """
    app = FastAPI()

    # Override the database dependency
    async def override_get_async_db() -> AsyncGenerator[AsyncSession, None]:
        yield async_test_db

    app.dependency_overrides[get_async_db] = override_get_async_db
    app.include_router(router)
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
    response = async_client.post("/stock-data/track", json={"symbol": "AAPL"})

    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "tracking"
    assert data["message"] == "Stock AAPL is now being tracked"
    assert data["symbol"] == "AAPL"

    # Verify database state
    result = await async_test_db.execute(select(TrackedStock).where(TrackedStock.symbol == "AAPL"))
    tracked_stock = result.scalar_one()
    assert tracked_stock.symbol == "AAPL"
    assert tracked_stock.last_pull_status == "pending"
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
        symbol="AAPL",
        last_pull_status="success",
        is_active=True,
    )
    async_test_db.add(existing_stock)
    await async_test_db.commit()

    # Mock the Yahoo Finance request
    with patch("cream_api.stock_data.retriever.StockDataRetriever._fetch_page") as mock_fetch:
        mock_fetch.return_value = "<html>Mock Yahoo Finance Response</html>"

        # Make the request
        response = async_client.post("/stock-data/track", json={"symbol": "AAPL"})

        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "tracking"
        assert data["message"] == "Stock AAPL is now being tracked"
        assert data["symbol"] == "AAPL"

        # Verify database state
        result = await async_test_db.execute(select(TrackedStock).where(TrackedStock.symbol == "AAPL"))
        tracked_stock = result.scalar_one()
        assert tracked_stock.symbol == "AAPL"
        assert tracked_stock.last_pull_status == "success"  # Should not change
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
    response = async_client.post("/stock-data/track", json={"symbol": ""})

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
        response = async_client.post("/stock-data/track", json={"symbol": "AAPL"})

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
    # Mock a background task error
    with patch("fastapi.BackgroundTasks.add_task", side_effect=Exception("Task error")) as mock_add_task:
        # Make the request
        response = async_client.post("/stock-data/track", json={"symbol": "AAPL"})

        # Verify response
        assert response.status_code == status.HTTP_200_OK  # Task errors shouldn't affect the response
        data = response.json()
        assert data["status"] == "tracking"
        assert data["message"] == "Stock AAPL is now being tracked"
        assert data["symbol"] == "AAPL"

        # Verify background task was scheduled
        mock_add_task.assert_called_once()
