"""Unit tests for stock data business logic services."""

from datetime import UTC, datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cream_api.common.exceptions import (
    InvalidStockSymbolError,
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

# Test constants
EXPECTED_THREE_STOCKS = 3
EXPECTED_TWO_ACTIVE_STOCKS = 2


class TestProcessStockRequest:
    """Test cases for process_stock_request function."""

    @pytest.mark.asyncio
    async def test_process_stock_request_new_symbol_success(self, async_test_db: AsyncSession) -> None:
        """Test successful processing of a new stock symbol."""
        result = await process_stock_request("AAPL", "user123", async_test_db)
        stmt = select(TrackedStock).where(TrackedStock.symbol == "AAPL")
        db_result = await async_test_db.execute(stmt)
        saved_stock = db_result.scalar_one()

        assert result.symbol == "AAPL"
        assert result.is_active is True
        assert result.last_pull_status == PullStatus.PENDING
        assert result.error_message is None
        assert saved_stock.id == result.id

    @pytest.mark.asyncio
    async def test_process_stock_request_existing_active_symbol(self, async_test_db: AsyncSession) -> None:
        """Test processing when symbol is already actively tracked."""
        # Arrange
        existing_stock = TrackedStock(
            symbol="TSLA",
            last_pull_date=datetime.now(UTC),
            last_pull_status=PullStatus.SUCCESS,
            is_active=True,
        )
        async_test_db.add(existing_stock)
        await async_test_db.commit()

        # Act
        result = await process_stock_request("TSLA", "user123", async_test_db)

        # Assert
        assert result.symbol == "TSLA"
        assert result.is_active is True
        assert result.last_pull_status == PullStatus.SUCCESS  # Should remain unchanged
        assert result.id == existing_stock.id

    @pytest.mark.asyncio
    async def test_process_stock_request_disabled_symbol_remains_disabled(self, async_test_db: AsyncSession) -> None:
        """Test that disabled stock symbols remain disabled."""
        # Arrange
        disabled_stock = TrackedStock(
            symbol="MSFT",
            last_pull_date=datetime.now(UTC),
            last_pull_status=PullStatus.FAILED,
            is_active=False,
            error_message="Previous error",
        )
        async_test_db.add(disabled_stock)
        await async_test_db.commit()

        # Act
        result = await process_stock_request("MSFT", "user123", async_test_db)

        # Assert
        assert result.symbol == "MSFT"
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
        # Act
        result = await process_stock_request("aapl", "user123", async_test_db)

        # Assert
        assert result.symbol == "AAPL"

    @pytest.mark.asyncio
    async def test_process_stock_request_symbol_trimmed(self, async_test_db: AsyncSession) -> None:
        """Test that symbol is trimmed of whitespace."""
        # Act
        result = await process_stock_request("  AAPL  ", "user123", async_test_db)

        # Assert
        assert result.symbol == "AAPL"


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
        # Arrange
        stocks = [
            TrackedStock(symbol="AAPL", is_active=True),
            TrackedStock(symbol="TSLA", is_active=False),
            TrackedStock(symbol="MSFT", is_active=True),
        ]
        for stock in stocks:
            async_test_db.add(stock)
        await async_test_db.commit()

        # Act
        result = await get_tracked_stocks(async_test_db)

        # Assert
        assert len(result) == EXPECTED_THREE_STOCKS
        symbols = [stock.symbol for stock in result]
        assert symbols == ["AAPL", "MSFT", "TSLA"]  # Should be ordered by symbol


class TestDeactivateStockTracking:
    """Test cases for deactivate_stock_tracking function."""

    @pytest.mark.asyncio
    async def test_deactivate_stock_tracking_success(self, async_test_db: AsyncSession) -> None:
        """Test successful deactivation of stock tracking."""
        # Arrange
        active_stock = TrackedStock(
            symbol="AAPL",
            is_active=True,
            last_pull_status=PullStatus.SUCCESS,
        )
        async_test_db.add(active_stock)
        await async_test_db.commit()

        # Act
        result = await deactivate_stock_tracking("AAPL", async_test_db)

        # Assert
        assert result.symbol == "AAPL"
        assert result.is_active is False
        assert result.last_pull_status == PullStatus.DISABLED
        assert result.error_message == "Tracking deactivated by admin"

    @pytest.mark.asyncio
    async def test_deactivate_stock_tracking_already_deactivated(self, async_test_db: AsyncSession) -> None:
        """Test deactivating already deactivated stock."""
        # Arrange
        inactive_stock = TrackedStock(
            symbol="TSLA",
            is_active=False,
            last_pull_status=PullStatus.DISABLED,
        )
        async_test_db.add(inactive_stock)
        await async_test_db.commit()

        # Act
        result = await deactivate_stock_tracking("TSLA", async_test_db)

        # Assert
        assert result.symbol == "TSLA"
        assert result.is_active is False
        assert result.last_pull_status == PullStatus.DISABLED

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
        # Arrange
        active_stock = TrackedStock(symbol="AAPL", is_active=True)
        async_test_db.add(active_stock)
        await async_test_db.commit()

        # Act
        result = await deactivate_stock_tracking("aapl", async_test_db)

        # Assert
        assert result.symbol == "AAPL"
        assert result.is_active is False


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
