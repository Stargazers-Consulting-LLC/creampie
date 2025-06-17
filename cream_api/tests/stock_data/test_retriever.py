"""Tests for stock data retriever."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from cream_api.settings import get_app_settings
from cream_api.stock_data.retriever import StockDataRetriever

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


@pytest_asyncio.fixture
async def session(async_test_db: AsyncSession) -> AsyncSession:
    """Create a database session for testing."""
    return async_test_db


@pytest_asyncio.fixture
async def retriever() -> StockDataRetriever:
    """Create a stock data retriever instance."""
    return StockDataRetriever()
