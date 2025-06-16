"""Tests for stock data processor."""

from datetime import datetime
from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cream_api.stock_data.exceptions import ValidationError
from cream_api.stock_data.models import StockData
from cream_api.stock_data.processor import DataProcessor
from cream_api.tests.stock_data.test_constants import (
    TEST_ADJ_CLOSE_PRICE,
    TEST_CLOSE_PRICE,
    TEST_HIGH_PRICE,
    TEST_LOW_PRICE,
    TEST_OPEN_PRICE,
    TEST_RECORDS_COUNT,
    TEST_UPDATED_OPEN_PRICE,
    TEST_VOLUME,
)


@pytest.fixture
def sample_data() -> dict[str, Any]:
    """Get sample stock data for testing."""
    return {
        "symbol": "AAPL",
        "currency": "USD",
        "prices": [
            {
                "date": "2024-01-01",
                "open": "100.00",
                "high": "101.00",
                "low": "99.00",
                "close": "100.50",
                "adj_close": "100.50",
                "volume": "1000000",
            },
            {
                "date": "2024-01-02",
                "open": "100.50",
                "high": "102.00",
                "low": "100.00",
                "close": "101.50",
                "adj_close": "101.50",
                "volume": "1200000",
            },
        ],
    }


@pytest.fixture
async def processor(session: AsyncSession) -> DataProcessor:
    """Create a data processor instance."""
    return DataProcessor(session)


@pytest.mark.asyncio
async def test_validate_data_success(processor: DataProcessor, sample_data: dict[str, Any]) -> None:
    """Test successful data validation."""
    errors = processor.validate_data(sample_data, "AAPL")
    assert not errors


@pytest.mark.asyncio
async def test_validate_data_missing_fields(processor: DataProcessor) -> None:
    """Test validation with missing required fields."""
    invalid_data = {
        "symbol": "AAPL",
        "prices": [],  # Missing currency
    }

    with pytest.raises(ValidationError) as exc_info:
        processor.validate_data(invalid_data, "AAPL")

    assert "Missing required field" in str(exc_info.value)
    assert "currency" in str(exc_info.value)


@pytest.mark.asyncio
async def test_validate_data_empty_prices(processor: DataProcessor) -> None:
    """Test validation with empty prices list."""
    invalid_data = {"symbol": "AAPL", "currency": "USD", "prices": []}

    with pytest.raises(ValidationError) as exc_info:
        processor.validate_data(invalid_data, "AAPL")

    assert "No price data found" in str(exc_info.value)


@pytest.mark.asyncio
async def test_transform_data_success(
    processor: DataProcessor, sample_data: dict[str, Any]
) -> None:
    """Test successful data transformation."""
    stock_data_list = processor.transform_data(sample_data)

    assert len(stock_data_list) == TEST_RECORDS_COUNT
    assert all(isinstance(data, StockData) for data in stock_data_list)

    # Check first record
    first_record = stock_data_list[0]
    assert first_record.symbol == "AAPL"
    assert first_record.date == datetime(2024, 1, 1)
    assert first_record.open == TEST_OPEN_PRICE
    assert first_record.high == TEST_HIGH_PRICE
    assert first_record.low == TEST_LOW_PRICE
    assert first_record.close == TEST_CLOSE_PRICE
    assert first_record.adj_close == TEST_ADJ_CLOSE_PRICE
    assert first_record.volume == TEST_VOLUME


@pytest.mark.asyncio
async def test_transform_data_invalid_format(processor: DataProcessor) -> None:
    """Test transformation with invalid data format."""
    invalid_data = {
        "symbol": "AAPL",
        "currency": "USD",
        "prices": [
            {
                "date": "invalid-date",
                "open": "100.00",
                "high": "101.00",
                "low": "99.00",
                "close": "100.50",
                "adj_close": "100.50",
                "volume": "1000000",
            }
        ],
    }

    with pytest.raises(ValidationError) as exc_info:
        processor.transform_data(invalid_data)

    assert "Data transformation error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_store_data_success(
    processor: DataProcessor, sample_data: dict[str, Any], session: AsyncSession
) -> None:
    """Test successful data storage."""
    # Transform data first
    stock_data_list = processor.transform_data(sample_data)

    # Store data
    await processor.store_data(stock_data_list)

    # Verify data was stored
    query = select(StockData).where(StockData.symbol == "AAPL")
    result = await session.execute(query)
    stored_data = result.scalars().all()

    assert len(stored_data) == TEST_RECORDS_COUNT
    assert all(data.symbol == "AAPL" for data in stored_data)


@pytest.mark.asyncio
async def test_store_data_duplicate(
    processor: DataProcessor, sample_data: dict[str, Any], session: AsyncSession
) -> None:
    """Test storing duplicate data."""
    # Transform and store data first time
    stock_data_list = processor.transform_data(sample_data)
    await processor.store_data(stock_data_list)

    # Modify some values
    for data in stock_data_list:
        data.open += 1.0
        data.high += 1.0
        data.low += 1.0
        data.close += 1.0
        data.adj_close += 1.0

    # Store modified data
    await processor.store_data(stock_data_list)

    # Verify data was updated
    query = select(StockData).where(StockData.symbol == "AAPL")
    result = await session.execute(query)
    stored_data = result.scalars().all()

    assert len(stored_data) == TEST_RECORDS_COUNT
    assert all(data.open == TEST_UPDATED_OPEN_PRICE for data in stored_data)


@pytest.mark.asyncio
async def test_process_data_end_to_end(
    processor: DataProcessor, sample_data: dict[str, Any], session: AsyncSession
) -> None:
    """Test end-to-end data processing."""
    await processor.process_data(sample_data, "AAPL")

    # Verify data was processed and stored
    query = select(StockData).where(StockData.symbol == "AAPL")
    result = await session.execute(query)
    stored_data = result.scalars().all()

    assert len(stored_data) == TEST_RECORDS_COUNT
    assert all(isinstance(data, StockData) for data in stored_data)
    assert all(data.symbol == "AAPL" for data in stored_data)
