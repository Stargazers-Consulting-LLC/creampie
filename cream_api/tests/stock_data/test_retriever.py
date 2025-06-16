"""Tests for stock data retriever."""

import os
from datetime import datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from cream_api.settings import get_app_settings
from cream_api.stock_data.exceptions import APIError, ValidationError
from cream_api.stock_data.models import StockData
from cream_api.stock_data.retriever import StockDataRetriever
from cream_api.tests.stock_data.test_constants import (
    TEST_ADJ_CLOSE_PRICE,
    TEST_CLOSE_PRICE,
    TEST_HIGH_PRICE,
    TEST_LOW_PRICE,
    TEST_OPEN_PRICE,
    TEST_RECORDS_COUNT,
    TEST_VOLUME,
)

settings = get_app_settings()


@pytest.fixture
def sample_html() -> str:
    """Get sample HTML for testing."""
    return """
    <table data-test="historical-prices">
        <tr>
            <th>Date</th>
            <th>Open</th>
            <th>High</th>
            <th>Low</th>
            <th>Close</th>
            <th>Adj Close</th>
            <th>Volume</th>
        </tr>
        <tr>
            <td>Jan 01, 2024</td>
            <td>100.00</td>
            <td>101.00</td>
            <td>99.00</td>
            <td>100.50</td>
            <td>100.50</td>
            <td>1,000,000</td>
        </tr>
        <tr>
            <td>Jan 02, 2024</td>
            <td>100.50</td>
            <td>102.00</td>
            <td>100.00</td>
            <td>101.50</td>
            <td>101.50</td>
            <td>1,200,000</td>
        </tr>
    </table>
    """


@pytest.fixture
async def retriever(session: AsyncSession) -> StockDataRetriever:
    """Create a stock data retriever instance."""
    return StockDataRetriever(session)


@pytest.mark.asyncio
async def test_cache_operations(retriever: StockDataRetriever, sample_html: str) -> None:
    """Test cache operations."""
    symbol = "AAPL"
    start_date = "2024-01-01"
    cache_path = retriever._get_cache_path(symbol, f"{start_date}_0")

    # Test cache creation
    cache_path.write_text(sample_html, encoding="utf-8")
    assert cache_path.exists()
    assert retriever._is_cache_valid(cache_path)

    # Test cache expiration
    # Create a file with an old modification time
    old_time = datetime.now() - timedelta(days=settings.CACHE_EXPIRATION_DAYS + 1)
    cache_path.touch(exist_ok=True)
    os.utime(str(cache_path), (old_time.timestamp(), old_time.timestamp()))
    assert not retriever._is_cache_valid(cache_path)


@pytest.mark.asyncio
async def test_get_historical_data_success(
    retriever: StockDataRetriever, sample_html: str, session: AsyncSession
) -> None:
    """Test successful historical data retrieval."""
    symbol = "AAPL"
    start_date = "2024-01-01"
    end_date = "2024-01-02"

    # Mock the HTML response
    cache_path = retriever._get_cache_path(symbol, f"{start_date}_0")
    cache_path.write_text(sample_html, encoding="utf-8")

    # Get historical data
    stock_data_list = await retriever.get_historical_data(symbol, start_date, end_date)

    # Verify the results
    assert len(stock_data_list) == TEST_RECORDS_COUNT
    assert all(isinstance(data, StockData) for data in stock_data_list)
    assert all(data.symbol == symbol for data in stock_data_list)

    # Check first record
    first_record = stock_data_list[0]
    assert first_record.date == datetime(2024, 1, 1)
    assert first_record.open == TEST_OPEN_PRICE
    assert first_record.high == TEST_HIGH_PRICE
    assert first_record.low == TEST_LOW_PRICE
    assert first_record.close == TEST_CLOSE_PRICE
    assert first_record.adj_close == TEST_ADJ_CLOSE_PRICE
    assert first_record.volume == TEST_VOLUME


@pytest.mark.asyncio
async def test_get_historical_data_invalid_symbol(retriever: StockDataRetriever) -> None:
    """Test handling of invalid stock symbol."""
    with pytest.raises(APIError) as exc_info:
        await retriever.get_historical_data("INVALID_SYMBOL", "2024-01-01")
    assert "INVALID_SYMBOL" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_historical_data_invalid_date_range(retriever: StockDataRetriever) -> None:
    """Test handling of invalid date range."""
    with pytest.raises(ValidationError) as exc_info:
        await retriever.get_historical_data("AAPL", "2024-01-02", "2024-01-01")
    assert "Invalid date range" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_historical_data_empty_response(
    retriever: StockDataRetriever, session: AsyncSession
) -> None:
    """Test handling of empty response."""
    symbol = "AAPL"
    start_date = "2024-01-01"
    end_date = "2024-01-02"

    # Mock empty HTML response
    cache_path = retriever._get_cache_path(symbol, f"{start_date}_0")
    cache_path.write_text("<table data-test='historical-prices'></table>", encoding="utf-8")

    with pytest.raises(ValidationError) as exc_info:
        await retriever.get_historical_data(symbol, start_date, end_date)
    assert "No price data found" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_historical_data_retry_mechanism(
    retriever: StockDataRetriever, session: AsyncSession
) -> None:
    """Test retry mechanism for failed requests."""
    symbol = "AAPL"
    start_date = "2024-01-01"
    end_date = "2024-01-02"

    # Mock a failed request that succeeds on retry
    cache_path = retriever._get_cache_path(symbol, f"{start_date}_0")
    cache_path.write_text("", encoding="utf-8")  # Empty response to trigger retry

    with pytest.raises(APIError) as exc_info:
        await retriever.get_historical_data(symbol, start_date, end_date)
    assert "Failed after" in str(exc_info.value)
