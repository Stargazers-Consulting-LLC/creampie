"""Tests for error handling in stock data functionality."""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from cream_api.stock_data.retriever import StockDataRetriever


@pytest_asyncio.fixture
async def session(async_test_db: AsyncSession) -> AsyncSession:
    """Create a database session for testing."""
    return async_test_db


@pytest_asyncio.fixture
async def retriever(session: AsyncSession) -> StockDataRetriever:
    """Create a stock data retriever instance."""
    return StockDataRetriever(session)
