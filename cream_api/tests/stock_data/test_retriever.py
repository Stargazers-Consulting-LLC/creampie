"""Tests for stock data retrieval functionality."""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cream_api.stock_data.exceptions import APIError
from cream_api.stock_data.models import StockData
from cream_api.stock_data.retriever import StockDataRetriever


@pytest.fixture
async def retriever(session: AsyncSession) -> StockDataRetriever:
    """Create a retriever instance for testing."""
    return StockDataRetriever(session)


@pytest.mark.asyncio
async def test_get_historical_data(retriever: StockDataRetriever, session: AsyncSession) -> None:
    """Test retrieving historical stock data."""
    # Test data
    symbol = "AAPL"
    start_date = "2024-01-01"
    end_date = "2024-01-02"

    # Get data
    await retriever.get_historical_data(symbol, start_date, end_date)

    # Verify data was stored
    result = await session.execute(select(StockData).where(StockData.symbol == symbol))
    data = result.scalars().all()
    assert len(data) > 0
    assert all(d.symbol == symbol for d in data)


@pytest.mark.asyncio
async def test_invalid_date_range(retriever: StockDataRetriever) -> None:
    """Test handling of invalid date range."""
    with pytest.raises(ValueError):
        await retriever.get_historical_data("AAPL", "2024-01-02", "2024-01-01")


@pytest.mark.asyncio
async def test_invalid_symbol(session: AsyncSession) -> None:
    """Test retrieving data for an invalid stock symbol."""
    retriever = StockDataRetriever(session)

    # Test with an invalid symbol
    with pytest.raises(APIError) as exc_info:
        await retriever.get_historical_data("INVALID_SYMBOL", "2023-01-01")
    assert "INVALID_SYMBOL" in str(exc_info.value)
