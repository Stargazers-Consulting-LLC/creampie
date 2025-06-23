"""Tests for stock data services.

This module contains comprehensive unit tests for the stock data services module,
including request processing, database operations, and error handling. It tests
all service functions with various scenarios including success cases, error
conditions, and edge cases.

The tests cover symbol validation, database interactions, error handling,
and business logic to ensure robust service functionality.

References:
    - [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)
    - [Pytest Async](https://pytest-asyncio.readthedocs.io/)

### Legal
SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from cream_api.common.exceptions import (
    InvalidStockSymbolError,
    StockDataError,
    StockNotFoundError,
)
from cream_api.stock_data.models import TrackedStock
from cream_api.stock_data.schemas import PullStatus
from cream_api.stock_data.services import (
    deactivate_stock_tracking,
    get_active_tracked_stocks,
    get_tracked_stocks,
    process_stock_request,
)
from cream_api.tests.stock_data.stock_data_test_constants import DEFAULT_TEST_SYMBOL, TEST_STOCK_SYMBOLS

# Test constants for magic numbers
EXPECTED_TOTAL_STOCKS = 3
EXPECTED_ACTIVE_STOCKS = 2


class DummyResultNone:
    def scalar_one_or_none(self) -> None:
        return None


class DummyResultStock:
    def scalar_one_or_none(self) -> TrackedStock:
        return TrackedStock(symbol=DEFAULT_TEST_SYMBOL, is_active=True)


class TestProcessStockRequest:
    """Test cases for process_stock_request function."""

    @pytest.mark.asyncio
    async def test_process_stock_request_new_symbol_success(self, async_test_db: AsyncSession) -> None:
        """Test that process_stock_request successfully creates tracking for new symbols.

        Verifies that when a new stock symbol is requested, the function creates
        a new tracking entry with proper default values and saves it to the database.
        """
        result = await process_stock_request(DEFAULT_TEST_SYMBOL, "user123", async_test_db)
        stmt = select(TrackedStock).where(TrackedStock.symbol == DEFAULT_TEST_SYMBOL)
        db_result = await async_test_db.execute(stmt)
        saved_stock = db_result.scalar_one()

        assert result.symbol == DEFAULT_TEST_SYMBOL
        assert result.is_active is True
        assert result.last_pull_status == PullStatus.PENDING
        assert result.error_message is None
        assert saved_stock.id == result.id

    @pytest.mark.asyncio
    async def test_process_stock_request_existing_active_symbol(self, async_test_db: AsyncSession) -> None:
        """Test that process_stock_request returns existing tracking for active symbols.

        Verifies that when requesting tracking for a symbol that is already
        actively tracked, the function returns the existing tracking without
        modifying its state.
        """
        existing_stock = TrackedStock(
            symbol=DEFAULT_TEST_SYMBOL,
            last_pull_date=datetime.now(UTC),
            last_pull_status=PullStatus.SUCCESS,
            is_active=True,
        )
        async_test_db.add(existing_stock)
        await async_test_db.commit()

        result = await process_stock_request(DEFAULT_TEST_SYMBOL, "user123", async_test_db)

        assert result.symbol == DEFAULT_TEST_SYMBOL
        assert result.is_active is True
        assert result.last_pull_status == PullStatus.SUCCESS
        assert result.id == existing_stock.id

    @pytest.mark.asyncio
    async def test_process_stock_request_disabled_symbol_remains_disabled(self, async_test_db: AsyncSession) -> None:
        """Test that process_stock_request preserves disabled state for inactive symbols.

        Verifies that when requesting tracking for a symbol that is currently
        disabled, the function returns the existing tracking without reactivating it.
        """
        test_symbol = "TSLA"
        assert test_symbol in TEST_STOCK_SYMBOLS

        disabled_stock = TrackedStock(
            symbol=test_symbol,
            last_pull_date=datetime.now(UTC),
            last_pull_status=PullStatus.FAILED,
            is_active=False,
            error_message="Previous error",
        )
        async_test_db.add(disabled_stock)
        await async_test_db.commit()

        result = await process_stock_request(test_symbol, "user123", async_test_db)

        assert result.symbol == test_symbol
        assert result.is_active is False
        assert result.last_pull_status == PullStatus.FAILED
        assert result.error_message == "Previous error"
        assert result.id == disabled_stock.id

    @pytest.mark.asyncio
    async def test_process_stock_request_empty_symbol(self, async_test_db: AsyncSession) -> None:
        """Test that process_stock_request rejects empty symbols with appropriate error.

        Verifies that the function raises InvalidStockSymbolError when provided
        with an empty string symbol.
        """
        with pytest.raises(InvalidStockSymbolError, match="Symbol cannot be empty"):
            await process_stock_request("", "user123", async_test_db)

    @pytest.mark.asyncio
    async def test_process_stock_request_whitespace_symbol(self, async_test_db: AsyncSession) -> None:
        """Test that process_stock_request rejects whitespace-only symbols.

        Verifies that the function raises InvalidStockSymbolError when provided
        with a symbol containing only whitespace characters.
        """
        with pytest.raises(InvalidStockSymbolError, match="Symbol cannot be empty"):
            await process_stock_request("   ", "user123", async_test_db)

    @pytest.mark.asyncio
    async def test_process_stock_request_symbol_too_long(self, async_test_db: AsyncSession) -> None:
        """Test that process_stock_request rejects symbols exceeding maximum length.

        Verifies that the function raises InvalidStockSymbolError when provided
        with a symbol longer than the maximum allowed length.
        """
        with pytest.raises(InvalidStockSymbolError, match="Symbol must be 10 characters or less"):
            await process_stock_request("VERYLONGSYMBOL", "user123", async_test_db)

    @pytest.mark.asyncio
    async def test_process_stock_request_symbol_starts_with_number(self, async_test_db: AsyncSession) -> None:
        """Test that process_stock_request rejects symbols starting with numbers.

        Verifies that the function raises InvalidStockSymbolError when provided
        with a symbol that starts with a numeric digit.
        """
        with pytest.raises(InvalidStockSymbolError, match="Symbol must start with a letter"):
            await process_stock_request("1AAPL", "user123", async_test_db)

    @pytest.mark.asyncio
    async def test_process_stock_request_symbol_contains_invalid_chars(self, async_test_db: AsyncSession) -> None:
        """Test that process_stock_request rejects symbols with invalid characters.

        Verifies that the function raises InvalidStockSymbolError when provided
        with a symbol containing special characters or non-alphanumeric content.
        """
        with pytest.raises(InvalidStockSymbolError, match="Symbol must contain only letters and numbers"):
            await process_stock_request("AAPL!", "user123", async_test_db)

    @pytest.mark.asyncio
    async def test_process_stock_request_symbol_normalized_to_uppercase(self, async_test_db: AsyncSession) -> None:
        """Test that process_stock_request normalizes symbols to uppercase.

        Verifies that the function converts lowercase symbols to uppercase
        format during processing.
        """
        lowercase_symbol = DEFAULT_TEST_SYMBOL.lower()

        result = await process_stock_request(lowercase_symbol, "user123", async_test_db)

        assert result.symbol == DEFAULT_TEST_SYMBOL

    @pytest.mark.asyncio
    async def test_process_stock_request_symbol_trimmed(self, async_test_db: AsyncSession) -> None:
        """Test that process_stock_request trims whitespace from symbols.

        Verifies that the function removes leading and trailing whitespace
        from input symbols during processing.
        """
        padded_symbol = f"  {DEFAULT_TEST_SYMBOL}  "

        result = await process_stock_request(padded_symbol, "user123", async_test_db)

        assert result.symbol == DEFAULT_TEST_SYMBOL

    @pytest.mark.asyncio
    async def test_process_stock_request_database_error_handling(self, async_test_db: AsyncSession) -> None:
        """Test that process_stock_request handles database errors gracefully.

        Verifies that the function properly handles SQLAlchemy errors during
        database operations and performs rollback when needed.
        """
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute.side_effect = SQLAlchemyError("Database connection failed")
        mock_db.rollback = AsyncMock()

        with pytest.raises(StockDataError, match="Failed to process stock tracking request"):
            await process_stock_request(DEFAULT_TEST_SYMBOL, "user123", mock_db)

        mock_db.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_stock_request_commit_error_handling(self, async_test_db: AsyncSession) -> None:
        """Test that process_stock_request handles commit errors gracefully.

        Verifies that the function properly handles commit failures and
        performs rollback when database commits fail.
        """
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute.return_value = DummyResultNone()
        mock_db.commit.side_effect = SQLAlchemyError("Commit failed")
        mock_db.rollback = AsyncMock()

        with pytest.raises(StockDataError, match="Failed to process stock tracking request"):
            await process_stock_request(DEFAULT_TEST_SYMBOL, "user123", mock_db)

        mock_db.rollback.assert_awaited_once()


class TestGetTrackedStocks:
    """Test cases for get_tracked_stocks function."""

    @pytest.mark.asyncio
    async def test_get_tracked_stocks_empty_list(self, async_test_db: AsyncSession) -> None:
        """Test that get_tracked_stocks returns empty list when no stocks are tracked.

        Verifies that the function returns an empty list when there are no
        tracked stocks in the database.
        """
        result = await get_tracked_stocks(async_test_db)
        assert result == []

    @pytest.mark.asyncio
    async def test_get_tracked_stocks_with_stocks(self, async_test_db: AsyncSession) -> None:
        """Test that get_tracked_stocks returns all tracked stocks.

        Verifies that the function returns all tracked stocks including both
        active and inactive entries, ordered by symbol.
        """
        stocks = [
            TrackedStock(symbol="AAPL", is_active=True),
            TrackedStock(symbol="TSLA", is_active=False),
            TrackedStock(symbol="GOOGL", is_active=True),
        ]
        for stock in stocks:
            async_test_db.add(stock)
        await async_test_db.commit()

        result = await get_tracked_stocks(async_test_db)

        assert len(result) == EXPECTED_TOTAL_STOCKS
        assert result[0].symbol == "AAPL"
        assert result[1].symbol == "GOOGL"
        assert result[2].symbol == "TSLA"

    @pytest.mark.asyncio
    async def test_get_tracked_stocks_database_error_handling(self, async_test_db: AsyncSession) -> None:
        """Test that get_tracked_stocks handles database errors gracefully.

        Verifies that the function properly handles SQLAlchemy errors during
        database queries and raises appropriate exceptions.
        """
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute.side_effect = SQLAlchemyError("Database query failed")

        with pytest.raises(StockDataError, match="Failed to retrieve tracked stocks"):
            await get_tracked_stocks(mock_db)


class TestDeactivateStockTracking:
    """Test cases for deactivate_stock_tracking function."""

    @pytest.mark.asyncio
    async def test_deactivate_stock_tracking_success(self, async_test_db: AsyncSession) -> None:
        """Test that deactivate_stock_tracking successfully deactivates active stocks.

        Verifies that the function properly deactivates an active stock tracking
        entry and updates its status to disabled.
        """
        active_stock = TrackedStock(
            symbol=DEFAULT_TEST_SYMBOL,
            last_pull_date=datetime.now(UTC),
            last_pull_status=PullStatus.SUCCESS,
            is_active=True,
        )
        async_test_db.add(active_stock)
        await async_test_db.commit()

        result = await deactivate_stock_tracking(DEFAULT_TEST_SYMBOL, async_test_db)

        assert result.symbol == DEFAULT_TEST_SYMBOL
        assert result.is_active is False
        assert result.last_pull_status == PullStatus.DISABLED
        assert result.error_message == "Tracking deactivated by admin"

    @pytest.mark.asyncio
    async def test_deactivate_stock_tracking_already_deactivated(self, async_test_db: AsyncSession) -> None:
        """Test that deactivate_stock_tracking handles already deactivated stocks.

        Verifies that the function returns the existing tracking without
        modification when attempting to deactivate an already inactive stock.
        """
        inactive_stock = TrackedStock(
            symbol=DEFAULT_TEST_SYMBOL,
            last_pull_date=datetime.now(UTC),
            last_pull_status=PullStatus.DISABLED,
            is_active=False,
            error_message="Already deactivated",
        )
        async_test_db.add(inactive_stock)
        await async_test_db.commit()

        result = await deactivate_stock_tracking(DEFAULT_TEST_SYMBOL, async_test_db)

        assert result.symbol == DEFAULT_TEST_SYMBOL
        assert result.is_active is False
        assert result.last_pull_status == PullStatus.DISABLED
        assert result.error_message == "Already deactivated"

    @pytest.mark.asyncio
    async def test_deactivate_stock_tracking_stock_not_found(self, async_test_db: AsyncSession) -> None:
        """Test that deactivate_stock_tracking raises error for untracked stocks.

        Verifies that the function raises StockNotFoundError when attempting
        to deactivate tracking for a symbol that is not being tracked.
        """
        with pytest.raises(StockNotFoundError, match="Stock TSLA is not being tracked"):
            await deactivate_stock_tracking("TSLA", async_test_db)

    @pytest.mark.asyncio
    async def test_deactivate_stock_tracking_empty_symbol(self, async_test_db: AsyncSession) -> None:
        """Test that deactivate_stock_tracking rejects empty symbols.

        Verifies that the function raises InvalidStockSymbolError when provided
        with an empty string symbol.
        """
        with pytest.raises(InvalidStockSymbolError, match="Symbol cannot be empty"):
            await deactivate_stock_tracking("", async_test_db)

    @pytest.mark.asyncio
    async def test_deactivate_stock_tracking_symbol_normalized(self, async_test_db: AsyncSession) -> None:
        """Test that deactivate_stock_tracking normalizes symbol format.

        Verifies that the function properly normalizes symbols by trimming
        whitespace and converting to uppercase before processing.
        """
        active_stock = TrackedStock(
            symbol=DEFAULT_TEST_SYMBOL,
            last_pull_date=datetime.now(UTC),
            last_pull_status=PullStatus.SUCCESS,
            is_active=True,
        )
        async_test_db.add(active_stock)
        await async_test_db.commit()

        padded_lowercase_symbol = f"  {DEFAULT_TEST_SYMBOL.lower()}  "
        result = await deactivate_stock_tracking(padded_lowercase_symbol, async_test_db)

        assert result.symbol == DEFAULT_TEST_SYMBOL
        assert result.is_active is False

    @pytest.mark.asyncio
    async def test_deactivate_stock_tracking_database_error_handling(self, async_test_db: AsyncSession) -> None:
        """Test that deactivate_stock_tracking handles database errors gracefully.

        Verifies that the function properly handles SQLAlchemy errors during
        database operations and performs rollback when needed.
        """
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute.side_effect = SQLAlchemyError("Database query failed")
        mock_db.rollback = AsyncMock()

        with pytest.raises(StockDataError, match="Failed to deactivate stock tracking"):
            await deactivate_stock_tracking(DEFAULT_TEST_SYMBOL, mock_db)

        mock_db.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_deactivate_stock_tracking_commit_error_handling(self, async_test_db: AsyncSession) -> None:
        """Test that deactivate_stock_tracking handles commit errors gracefully.

        Verifies that the function properly handles commit failures and
        performs rollback when database commits fail.
        """
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute.return_value = DummyResultStock()
        mock_db.commit.side_effect = SQLAlchemyError("Commit failed")
        mock_db.rollback = AsyncMock()

        with pytest.raises(StockDataError, match="Failed to deactivate stock tracking"):
            await deactivate_stock_tracking(DEFAULT_TEST_SYMBOL, mock_db)

        mock_db.rollback.assert_awaited_once()


class TestGetActiveTrackedStocks:
    """Test cases for get_active_tracked_stocks function."""

    @pytest.mark.asyncio
    async def test_get_active_tracked_stocks_empty_list(self, async_test_db: AsyncSession) -> None:
        """Test that get_active_tracked_stocks returns empty list when no active stocks exist.

        Verifies that the function returns an empty list when there are no
        actively tracked stocks in the database.
        """
        result = await get_active_tracked_stocks(async_test_db)
        assert result == []

    @pytest.mark.asyncio
    async def test_get_active_tracked_stocks_only_active(self, async_test_db: AsyncSession) -> None:
        """Test that get_active_tracked_stocks returns only active stocks.

        Verifies that the function filters and returns only stocks that are
        currently active, excluding inactive or disabled stocks.
        """
        stocks = [
            TrackedStock(symbol="AAPL", is_active=True),
            TrackedStock(symbol="TSLA", is_active=False),
            TrackedStock(symbol="GOOGL", is_active=True),
        ]
        for stock in stocks:
            async_test_db.add(stock)
        await async_test_db.commit()

        result = await get_active_tracked_stocks(async_test_db)

        assert len(result) == EXPECTED_ACTIVE_STOCKS
        assert all(stock.is_active for stock in result)
        assert result[0].symbol == "AAPL"
        assert result[1].symbol == "GOOGL"

    @pytest.mark.asyncio
    async def test_get_active_tracked_stocks_database_error_handling(self, async_test_db: AsyncSession) -> None:
        """Test that get_active_tracked_stocks handles database errors gracefully.

        Verifies that the function properly handles SQLAlchemy errors during
        database queries and raises appropriate exceptions.
        """
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute.side_effect = SQLAlchemyError("Database query failed")

        with pytest.raises(StockDataError, match="Failed to retrieve active tracked stocks"):
            await get_active_tracked_stocks(mock_db)
