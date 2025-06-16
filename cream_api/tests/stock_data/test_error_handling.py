"""Tests for error handling in stock data retrieval."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from cream_api.stock_data.exceptions import APIError, ValidationError
from cream_api.stock_data.retriever import StockDataRetriever


@pytest.fixture
async def retriever(session: AsyncSession) -> StockDataRetriever:
    """Create a retriever instance for testing."""
    return StockDataRetriever(session)


@pytest.mark.asyncio
async def test_invalid_symbol(retriever: StockDataRetriever) -> None:
    """Test handling of invalid stock symbol."""
    with pytest.raises(APIError) as exc_info:
        await retriever.get_historical_data("INVALID_SYMBOL", "2024-01-01")
    assert "INVALID_SYMBOL" in str(exc_info.value)


@pytest.mark.asyncio
async def test_invalid_date_format(retriever: StockDataRetriever) -> None:
    """Test handling of invalid date format."""
    with pytest.raises(ValidationError) as exc_info:
        await retriever.get_historical_data("AAPL", "invalid-date")
    assert "Invalid date format" in str(exc_info.value)
