"""Tests for stock data manager."""

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from cream_api.stock_data.loader import StockDataLoader
from cream_api.stock_data.models import StockData
from cream_api.tests.stock_data.test_constants import (
    TEST_ADJ_CLOSE_PRICE,
    TEST_CLOSE_PRICE,
    TEST_HIGH_PRICE,
    TEST_LOW_PRICE,
    TEST_OPEN_PRICE,
    TEST_RECORDS_COUNT,
    TEST_SYMBOL,
    TEST_VOLUME,
)


@pytest_asyncio.fixture
async def session(async_test_db: AsyncSession) -> AsyncSession:
    """Create a database session for testing."""
    return async_test_db


@pytest_asyncio.fixture
async def data_loader(async_test_db: AsyncSession) -> AsyncGenerator[StockDataLoader, None]:
    """Create a test data loader instance."""
    loader = StockDataLoader(async_test_db)
    yield loader


@pytest.mark.asyncio
async def test_validate_data_success(data_loader: StockDataLoader) -> None:
    """Test successful data validation."""
    sample_data: dict[str, list[dict[str, str | float | int]]] = {
        "prices": [
            {
                "date": "2024-01-01",
                "open": TEST_OPEN_PRICE,
                "high": TEST_HIGH_PRICE,
                "low": TEST_LOW_PRICE,
                "close": TEST_CLOSE_PRICE,
                "adj_close": TEST_ADJ_CLOSE_PRICE,
                "volume": TEST_VOLUME,
            }
        ]
    }
    await data_loader.validate_data(sample_data)


@pytest.mark.asyncio
async def test_validate_data_missing_fields(data_loader: StockDataLoader) -> None:
    """Test validation with missing required fields."""
    sample_data: dict[str, list[dict[str, str | float | int]]] = {
        "prices": [
            {
                "date": "2024-01-01",
                "open": TEST_OPEN_PRICE,
                "high": TEST_HIGH_PRICE,
                "low": TEST_LOW_PRICE,
                "close": TEST_CLOSE_PRICE,
                "adj_close": TEST_ADJ_CLOSE_PRICE,
            }
        ]
    }
    with pytest.raises(ValueError) as exc_info:
        await data_loader.validate_data(sample_data)
    assert "Missing required fields" in str(exc_info.value)


@pytest.mark.asyncio
async def test_validate_data_empty_prices(data_loader: StockDataLoader) -> None:
    """Test validation with empty prices list."""
    sample_data: dict[str, list[dict[str, str | float | int]]] = {"prices": []}
    with pytest.raises(ValueError) as exc_info:
        await data_loader.validate_data(sample_data)
    assert "Prices list cannot be empty" in str(exc_info.value)


@pytest.mark.asyncio
async def test_transform_data_success(data_loader: StockDataLoader) -> None:
    """Test successful data transformation."""
    sample_data: dict[str, list[dict[str, str | float | int]]] = {
        "prices": [
            {
                "date": "2024-01-01",
                "open": TEST_OPEN_PRICE,
                "high": TEST_HIGH_PRICE,
                "low": TEST_LOW_PRICE,
                "close": TEST_CLOSE_PRICE,
                "adj_close": TEST_ADJ_CLOSE_PRICE,
                "volume": TEST_VOLUME,
            }
        ]
    }
    stock_data_list = await data_loader.transform_data(sample_data)
    assert len(stock_data_list) == TEST_RECORDS_COUNT
    assert all(isinstance(data, StockData) for data in stock_data_list)
    first_record = stock_data_list[0]
    assert first_record.date.strftime("%Y-%m-%d") == "2024-01-01"
    assert first_record.open == TEST_OPEN_PRICE
    assert first_record.high == TEST_HIGH_PRICE
    assert first_record.low == TEST_LOW_PRICE
    assert first_record.close == TEST_CLOSE_PRICE
    assert first_record.adj_close == TEST_ADJ_CLOSE_PRICE
    assert first_record.volume == TEST_VOLUME


@pytest.mark.asyncio
async def test_transform_data_invalid_format(data_loader: StockDataLoader) -> None:
    """Test transformation with invalid data format."""
    sample_data: dict[str, list[dict[str, str | float | int]]] = {
        "prices": [
            {
                "date": "2024-01-01",
                "open": "invalid",
                "high": TEST_HIGH_PRICE,
                "low": TEST_LOW_PRICE,
                "close": TEST_CLOSE_PRICE,
                "adj_close": TEST_ADJ_CLOSE_PRICE,
                "volume": TEST_VOLUME,
            }
        ]
    }
    with pytest.raises(ValueError) as exc_info:
        await data_loader.transform_data(sample_data)
    assert "could not convert string to float: 'invalid'" in str(exc_info.value)


@pytest.mark.asyncio
async def test_store_data_success(data_loader: StockDataLoader, session: AsyncSession) -> None:
    """Test successful data storage."""
    sample_data: dict[str, list[dict[str, str | float | int]]] = {
        "prices": [
            {
                "date": "2024-01-01",
                "open": TEST_OPEN_PRICE,
                "high": TEST_HIGH_PRICE,
                "low": TEST_LOW_PRICE,
                "close": TEST_CLOSE_PRICE,
                "adj_close": TEST_ADJ_CLOSE_PRICE,
                "volume": TEST_VOLUME,
            }
        ]
    }
    stock_data_list = await data_loader.transform_data(sample_data)
    await data_loader.store_data(TEST_SYMBOL, stock_data_list)
    result = await session.execute(text("SELECT * FROM stock_data"))
    stored_data = result.fetchall()
    assert len(stored_data) == TEST_RECORDS_COUNT


@pytest.mark.asyncio
async def test_store_data_duplicate(data_loader: StockDataLoader, session: AsyncSession) -> None:
    """Test handling of duplicate data storage."""
    sample_data: dict[str, list[dict[str, str | float | int]]] = {
        "prices": [
            {
                "date": "2024-01-01",
                "open": TEST_OPEN_PRICE,
                "high": TEST_HIGH_PRICE,
                "low": TEST_LOW_PRICE,
                "close": TEST_CLOSE_PRICE,
                "adj_close": TEST_ADJ_CLOSE_PRICE,
                "volume": TEST_VOLUME,
            }
        ]
    }
    stock_data_list = await data_loader.transform_data(sample_data)
    await data_loader.store_data(TEST_SYMBOL, stock_data_list)
    await data_loader.store_data(TEST_SYMBOL, stock_data_list)
    result = await session.execute(text("SELECT * FROM stock_data"))
    stored_data = result.fetchall()
    assert len(stored_data) == TEST_RECORDS_COUNT


@pytest.mark.asyncio
async def test_process_data_end_to_end(data_loader: StockDataLoader, session: AsyncSession) -> None:
    """Test end-to-end data processing."""
    sample_data: dict[str, list[dict[str, str | float | int]]] = {
        "prices": [
            {
                "date": "2024-01-01",
                "open": TEST_OPEN_PRICE,
                "high": TEST_HIGH_PRICE,
                "low": TEST_LOW_PRICE,
                "close": TEST_CLOSE_PRICE,
                "adj_close": TEST_ADJ_CLOSE_PRICE,
                "volume": TEST_VOLUME,
            }
        ]
    }
    await data_loader.process_data(TEST_SYMBOL, sample_data)
    result = await session.execute(text("SELECT * FROM stock_data"))
    stored_data = result.fetchall()
    assert len(stored_data) == TEST_RECORDS_COUNT
