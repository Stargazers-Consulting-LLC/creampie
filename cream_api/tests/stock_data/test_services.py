"""Unit tests for stock data business logic services."""

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
from cream_api.tests.stock_data.test_constants import DEFAULT_TEST_SYMBOL, TEST_STOCK_SYMBOLS

# Test constants
EXPECTED_THREE_STOCKS = 3
EXPECTED_TWO_ACTIVE_STOCKS = 2


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
        """Test successful processing of a new stock symbol."""
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
        """Test processing when symbol is already actively tracked."""
        # Arrange
        existing_stock = TrackedStock(
            symbol=DEFAULT_TEST_SYMBOL,
            last_pull_date=datetime.now(UTC),
            last_pull_status=PullStatus.SUCCESS,
            is_active=True,
        )
        async_test_db.add(existing_stock)
        await async_test_db.commit()

        # Act
        result = await process_stock_request(DEFAULT_TEST_SYMBOL, "user123", async_test_db)

        # Assert
        assert result.symbol == DEFAULT_TEST_SYMBOL
        assert result.is_active is True
        assert result.last_pull_status == PullStatus.SUCCESS  # Should remain unchanged
        assert result.id == existing_stock.id

    @pytest.mark.asyncio
    async def test_process_stock_request_disabled_symbol_remains_disabled(self, async_test_db: AsyncSession) -> None:
        """Test that disabled stock symbols remain disabled."""
        # Use a different symbol for this test
        test_symbol = "TSLA"
        assert test_symbol in TEST_STOCK_SYMBOLS

        # Arrange
        disabled_stock = TrackedStock(
            symbol=test_symbol,
            last_pull_date=datetime.now(UTC),
            last_pull_status=PullStatus.FAILED,
            is_active=False,
            error_message="Previous error",
        )
        async_test_db.add(disabled_stock)
        await async_test_db.commit()

        # Act
        result = await process_stock_request(test_symbol, "user123", async_test_db)

        # Assert
        assert result.symbol == test_symbol
        assert result.is_active is False  # Should remain disabled
        assert result.last_pull_status == PullStatus.FAILED  # Should remain unchanged
        assert result.error_message == "Previous error"  # Should remain unchanged
        assert result.id == disabled_stock.id

    @pytest.mark.asyncio
    async def test_process_stock_request_empty_symbol(self, async_test_db: AsyncSession) -> None:
        """Test processing with empty symbol raises error."""
        # Act & Assert
        with pytest.raises(InvalidStockSymbolError, match="Symbol cannot be empty"):
            await process_stock_request("", "user123", async_test_db)

    @pytest.mark.asyncio
    async def test_process_stock_request_whitespace_symbol(self, async_test_db: AsyncSession) -> None:
        """Test processing with whitespace-only symbol raises error."""
        # Act & Assert
        with pytest.raises(InvalidStockSymbolError, match="Symbol cannot be empty"):
            await process_stock_request("   ", "user123", async_test_db)

    @pytest.mark.asyncio
    async def test_process_stock_request_symbol_too_long(self, async_test_db: AsyncSession) -> None:
        """Test processing with symbol longer than 10 characters raises error."""
        # Act & Assert
        with pytest.raises(InvalidStockSymbolError, match="Symbol must be 10 characters or less"):
            await process_stock_request("VERYLONGSYMBOL", "user123", async_test_db)

    @pytest.mark.asyncio
    async def test_process_stock_request_symbol_starts_with_number(self, async_test_db: AsyncSession) -> None:
        """Test processing with symbol starting with number raises error."""
        # Act & Assert
        with pytest.raises(InvalidStockSymbolError, match="Symbol must start with a letter"):
            await process_stock_request("1AAPL", "user123", async_test_db)

    @pytest.mark.asyncio
    async def test_process_stock_request_symbol_contains_invalid_chars(self, async_test_db: AsyncSession) -> None:
        """Test processing with symbol containing invalid characters raises error."""
        # Act & Assert
        with pytest.raises(InvalidStockSymbolError, match="Symbol must contain only letters and numbers"):
            await process_stock_request("AAPL!", "user123", async_test_db)

    @pytest.mark.asyncio
    async def test_process_stock_request_symbol_normalized_to_uppercase(self, async_test_db: AsyncSession) -> None:
        """Test that symbol is normalized to uppercase."""
        lowercase_symbol = DEFAULT_TEST_SYMBOL.lower()

        # Act
        result = await process_stock_request(lowercase_symbol, "user123", async_test_db)

        # Assert
        assert result.symbol == DEFAULT_TEST_SYMBOL

    @pytest.mark.asyncio
    async def test_process_stock_request_symbol_trimmed(self, async_test_db: AsyncSession) -> None:
        """Test that symbol is trimmed of whitespace."""
        padded_symbol = f"  {DEFAULT_TEST_SYMBOL}  "

        # Act
        result = await process_stock_request(padded_symbol, "user123", async_test_db)

        # Assert
        assert result.symbol == DEFAULT_TEST_SYMBOL

    @pytest.mark.asyncio
    async def test_process_stock_request_database_error_handling(self, async_test_db: AsyncSession) -> None:
        """Test handling of database errors during stock request processing."""
        # Arrange - Mock the database session to raise an error
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute.side_effect = SQLAlchemyError("Database connection failed")
        mock_db.rollback = AsyncMock()

        # Act & Assert
        with pytest.raises(StockDataError, match="Failed to process stock tracking request"):
            await process_stock_request(DEFAULT_TEST_SYMBOL, "user123", mock_db)

        # Verify rollback was called
        mock_db.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_stock_request_commit_error_handling(self, async_test_db: AsyncSession) -> None:
        """Test handling of commit errors during stock request processing."""
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
        """Test getting tracked stocks when none exist."""
        # Act
        result = await get_tracked_stocks(async_test_db)

        # Assert
        assert result == []

    @pytest.mark.asyncio
    async def test_get_tracked_stocks_with_stocks(self, async_test_db: AsyncSession) -> None:
        """Test getting tracked stocks when multiple exist."""
        # Use specific symbols from constants
        symbols = ["AAPL", "TSLA", "MSFT"]

        # Arrange
        stocks = [
            TrackedStock(symbol=symbols[0], is_active=True),
            TrackedStock(symbol=symbols[1], is_active=False),
            TrackedStock(symbol=symbols[2], is_active=True),
        ]
        for stock in stocks:
            async_test_db.add(stock)
        await async_test_db.commit()

        # Act
        result = await get_tracked_stocks(async_test_db)

        # Assert
        assert len(result) == EXPECTED_THREE_STOCKS
        result_symbols = [stock.symbol for stock in result]
        expected_symbols = sorted(symbols)  # Should be ordered by symbol
        assert result_symbols == expected_symbols

    @pytest.mark.asyncio
    async def test_get_tracked_stocks_database_error_handling(self, async_test_db: AsyncSession) -> None:
        """Test handling of database errors when retrieving tracked stocks."""
        # Arrange - Mock the database session to raise an error
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute.side_effect = SQLAlchemyError("Database connection failed")

        # Act & Assert
        with pytest.raises(StockDataError, match="Failed to retrieve tracked stocks"):
            await get_tracked_stocks(mock_db)


class TestDeactivateStockTracking:
    """Test cases for deactivate_stock_tracking function."""

    @pytest.mark.asyncio
    async def test_deactivate_stock_tracking_success(self, async_test_db: AsyncSession) -> None:
        """Test successful deactivation of stock tracking."""
        # Arrange
        active_stock = TrackedStock(
            symbol=DEFAULT_TEST_SYMBOL,
            is_active=True,
            last_pull_status=PullStatus.SUCCESS,
        )
        async_test_db.add(active_stock)
        await async_test_db.commit()

        # Act
        result = await deactivate_stock_tracking(DEFAULT_TEST_SYMBOL, async_test_db)

        # Assert
        assert result.symbol == DEFAULT_TEST_SYMBOL
        assert result.is_active is False
        assert result.last_pull_status == PullStatus.DISABLED
        assert result.error_message == "Tracking deactivated by admin"

    @pytest.mark.asyncio
    async def test_deactivate_stock_tracking_already_deactivated(self, async_test_db: AsyncSession) -> None:
        """Test deactivating an already deactivated stock."""
        # Use a different symbol for this test
        test_symbol = "TSLA"
        assert test_symbol in TEST_STOCK_SYMBOLS

        # Arrange
        inactive_stock = TrackedStock(
            symbol=test_symbol,
            is_active=False,
            last_pull_status=PullStatus.DISABLED,
            error_message="Already deactivated",
        )
        async_test_db.add(inactive_stock)
        await async_test_db.commit()

        # Act
        result = await deactivate_stock_tracking(test_symbol, async_test_db)

        # Assert
        assert result.symbol == test_symbol
        assert result.is_active is False  # Should remain deactivated
        assert result.last_pull_status == PullStatus.DISABLED  # Should remain unchanged
        assert result.error_message == "Already deactivated"  # Should remain unchanged

    @pytest.mark.asyncio
    async def test_deactivate_stock_tracking_stock_not_found(self, async_test_db: AsyncSession) -> None:
        """Test deactivating non-existent stock raises error."""
        # Act & Assert
        with pytest.raises(StockNotFoundError, match="Stock UNKNOWN is not being tracked"):
            await deactivate_stock_tracking("UNKNOWN", async_test_db)

    @pytest.mark.asyncio
    async def test_deactivate_stock_tracking_empty_symbol(self, async_test_db: AsyncSession) -> None:
        """Test deactivating with empty symbol raises error."""
        # Act & Assert
        with pytest.raises(InvalidStockSymbolError, match="Symbol cannot be empty"):
            await deactivate_stock_tracking("", async_test_db)

    @pytest.mark.asyncio
    async def test_deactivate_stock_tracking_symbol_normalized(self, async_test_db: AsyncSession) -> None:
        """Test that symbol is normalized during deactivation."""
        lowercase_symbol = DEFAULT_TEST_SYMBOL.lower()

        # Arrange
        active_stock = TrackedStock(symbol=DEFAULT_TEST_SYMBOL, is_active=True)
        async_test_db.add(active_stock)
        await async_test_db.commit()

        # Act
        result = await deactivate_stock_tracking(lowercase_symbol, async_test_db)

        # Assert
        assert result.symbol == DEFAULT_TEST_SYMBOL  # Should be normalized to uppercase
        assert result.is_active is False

    @pytest.mark.asyncio
    async def test_deactivate_stock_tracking_database_error_handling(self, async_test_db: AsyncSession) -> None:
        """Test handling of database errors during deactivation."""
        # Arrange - Mock the database session to raise an error
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute.side_effect = SQLAlchemyError("Database connection failed")
        mock_db.rollback = AsyncMock()

        # Act & Assert
        with pytest.raises(StockDataError, match="Failed to deactivate stock tracking"):
            await deactivate_stock_tracking(DEFAULT_TEST_SYMBOL, mock_db)

        # Verify rollback was called
        mock_db.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_deactivate_stock_tracking_commit_error_handling(self, async_test_db: AsyncSession) -> None:
        """Test handling of commit errors during deactivation."""
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
        """Test getting active tracked stocks when none exist."""
        # Act
        result = await get_active_tracked_stocks(async_test_db)

        # Assert
        assert result == []

    @pytest.mark.asyncio
    async def test_get_active_tracked_stocks_only_active(self, async_test_db: AsyncSession) -> None:
        """Test getting only active tracked stocks."""
        # Arrange
        stocks = [
            TrackedStock(symbol="AAPL", is_active=True),
            TrackedStock(symbol="TSLA", is_active=False),
            TrackedStock(symbol="MSFT", is_active=True),
            TrackedStock(symbol="GOOGL", is_active=False),
        ]
        for stock in stocks:
            async_test_db.add(stock)
        await async_test_db.commit()

        # Act
        result = await get_active_tracked_stocks(async_test_db)

        # Assert
        assert len(result) == EXPECTED_TWO_ACTIVE_STOCKS
        symbols = [stock.symbol for stock in result]
        assert symbols == ["AAPL", "MSFT"]  # Should be ordered by symbol

    @pytest.mark.asyncio
    async def test_get_active_tracked_stocks_database_error_handling(self, async_test_db: AsyncSession) -> None:
        """Test handling of database errors when retrieving active tracked stocks."""
        # Arrange - Mock the database session to raise an error
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute.side_effect = SQLAlchemyError("Database connection failed")

        # Act & Assert
        with pytest.raises(StockDataError, match="Failed to retrieve active tracked stocks"):
            await get_active_tracked_stocks(mock_db)
