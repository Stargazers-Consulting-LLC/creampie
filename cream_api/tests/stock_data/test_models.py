"""Tests for stock data models.

This module contains tests for the stock data models, including:
- StockData model validation and relationships
- TrackedStock model validation and relationships
- Model creation and updates
"""

import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from cream_api.stock_data.models import StockData, TrackedStock
from cream_api.tests.stock_data.stock_data_test_constants import DEFAULT_TEST_SYMBOL, TEST_VOLUME


@pytest.fixture
def sample_stock_data() -> dict:
    """Create sample stock data for testing."""
    return {
        "symbol": DEFAULT_TEST_SYMBOL,
        "date": datetime(2024, 1, 1, tzinfo=UTC),
        "open": 150.0,
        "high": 155.0,
        "low": 148.0,
        "close": 153.0,
        "adj_close": 153.0,
        "volume": TEST_VOLUME,
    }


@pytest.fixture
def sample_tracked_stock() -> dict:
    """Create sample tracked stock data for testing."""
    return {
        "symbol": DEFAULT_TEST_SYMBOL,
        "last_pull_date": datetime(2024, 1, 1, tzinfo=UTC),
        "last_pull_status": "success",
        "error_message": None,
        "is_active": True,
    }


@pytest.mark.asyncio
async def test_create_stock_data(async_test_db: AsyncSession, sample_stock_data: dict) -> None:
    """Test creating a StockData record."""
    # Create and add the record
    stock_data = StockData(**sample_stock_data)
    async_test_db.add(stock_data)
    await async_test_db.commit()

    # Query the record
    result = await async_test_db.execute(select(StockData).where(StockData.symbol == sample_stock_data["symbol"]))
    saved_data = result.scalar_one()

    # Verify all fields
    assert isinstance(saved_data.id, uuid.UUID)
    assert saved_data.symbol == sample_stock_data["symbol"]
    assert saved_data.date == sample_stock_data["date"]
    assert saved_data.open == sample_stock_data["open"]
    assert saved_data.high == sample_stock_data["high"]
    assert saved_data.low == sample_stock_data["low"]
    assert saved_data.close == sample_stock_data["close"]
    assert saved_data.adj_close == sample_stock_data["adj_close"]
    assert saved_data.volume == sample_stock_data["volume"]


@pytest.mark.asyncio
async def test_stock_data_unique_constraint(async_test_db: AsyncSession, sample_stock_data: dict) -> None:
    """Test that duplicate symbol+date combinations are not allowed."""
    # Create first record
    stock_data1 = StockData(**sample_stock_data)
    async_test_db.add(stock_data1)
    await async_test_db.commit()

    # Try to create duplicate record
    stock_data2 = StockData(**sample_stock_data)
    async_test_db.add(stock_data2)

    # Should raise IntegrityError
    with pytest.raises(IntegrityError):
        await async_test_db.commit()


@pytest.mark.asyncio
async def test_create_tracked_stock(async_test_db: AsyncSession, sample_tracked_stock: dict) -> None:
    """Test creating a TrackedStock record."""
    # Create and add the record
    tracked_stock = TrackedStock(**sample_tracked_stock)
    async_test_db.add(tracked_stock)
    await async_test_db.commit()

    # Query the record
    result = await async_test_db.execute(
        select(TrackedStock).where(TrackedStock.symbol == sample_tracked_stock["symbol"])
    )
    saved_data = result.scalar_one()

    # Verify all fields
    assert saved_data.symbol == sample_tracked_stock["symbol"]
    assert saved_data.last_pull_date == sample_tracked_stock["last_pull_date"]
    assert saved_data.last_pull_status == sample_tracked_stock["last_pull_status"]
    assert saved_data.error_message == sample_tracked_stock["error_message"]
    assert saved_data.is_active == sample_tracked_stock["is_active"]
    assert isinstance(saved_data.id, uuid.UUID)


@pytest.mark.asyncio
async def test_tracked_stock_unique_constraint(async_test_db: AsyncSession, sample_tracked_stock: dict) -> None:
    """Test that duplicate symbols are not allowed."""
    # Create first record
    tracked_stock1 = TrackedStock(**sample_tracked_stock)
    async_test_db.add(tracked_stock1)
    await async_test_db.commit()

    # Try to create duplicate record
    tracked_stock2 = TrackedStock(**sample_tracked_stock)
    async_test_db.add(tracked_stock2)

    # Should raise IntegrityError
    with pytest.raises(IntegrityError):
        await async_test_db.commit()


@pytest.mark.asyncio
async def test_tracked_stock_default_values(async_test_db: AsyncSession) -> None:
    """Test that TrackedStock default values are set correctly."""
    # Create record with minimal data
    tracked_stock = TrackedStock(symbol=DEFAULT_TEST_SYMBOL)
    async_test_db.add(tracked_stock)
    await async_test_db.commit()

    # Query the record
    result = await async_test_db.execute(select(TrackedStock).where(TrackedStock.symbol == DEFAULT_TEST_SYMBOL))
    saved_data = result.scalar_one()

    # Verify default values
    assert saved_data.last_pull_status == "pending"
    assert saved_data.is_active is True
    assert saved_data.error_message is None


@pytest.mark.asyncio
async def test_stock_data_nullable_fields(async_test_db: AsyncSession) -> None:
    """Test that required fields cannot be null in StockData."""
    # Try to create record with missing required fields
    stock_data = StockData(symbol=DEFAULT_TEST_SYMBOL)  # Missing other required fields
    async_test_db.add(stock_data)

    # Should raise IntegrityError
    with pytest.raises(IntegrityError):
        await async_test_db.commit()


@pytest.mark.asyncio
async def test_tracked_stock_nullable_fields(async_test_db: AsyncSession) -> None:
    """Test that required fields cannot be null in TrackedStock."""
    # Try to create record with missing required fields
    tracked_stock = TrackedStock(
        # Missing symbol
        last_pull_status="pending",
        is_active=True,
    )
    async_test_db.add(tracked_stock)

    # Should raise IntegrityError
    with pytest.raises(IntegrityError):
        await async_test_db.commit()
