"""Business logic services for stock tracking operations.

This module provides core business logic functions for processing stock tracking
requests and managing tracked stocks. It handles the separation of concerns
between API endpoints and business logic.

References:
    - [FastAPI Documentation](https://fastapi.tiangolo.com/)
    - [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
    - [Python Type Hints](https://docs.python.org/3/library/typing.html)

### Legal
SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

import logging
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from stargazer_utils.logging import get_logger_for

from cream_api.common.exceptions import (
    InvalidStockSymbolError,
    StockDataError,
    StockNotFoundError,
)
from cream_api.stock_data.constants import MAX_STOCK_SYMBOL_LENGTH
from cream_api.stock_data.models import TrackedStock
from cream_api.stock_data.schemas import PullStatus

logger: logging.Logger = get_logger_for(__name__)


async def process_stock_request(symbol: str, user_id: str, db: AsyncSession) -> TrackedStock:
    """Process a stock tracking request from a user.

    This function handles the business logic for processing stock tracking requests.
    It checks for existing tracking, handles duplicates gracefully, and creates
    new tracking entries when needed.

    Args:
        symbol: Stock symbol to track (must be uppercase)
        user_id: ID of the user making the request
        db: Database session for operations

    Returns:
        TrackedStock: The tracked stock object (either existing or newly created)

    Raises:
        InvalidStockSymbolError: If the symbol format is invalid
        StockDataError: For database or other operational errors
    """
    logger.info("Processing stock tracking request for symbol '%s' from user '%s'", symbol, user_id)

    try:
        # Validate symbol format
        if not symbol or not symbol.strip():
            raise InvalidStockSymbolError(symbol, "Symbol cannot be empty")

        symbol = symbol.strip().upper()

        # Basic validation - symbols should be 1-10 characters, alphanumeric, starting with letter
        if len(symbol) > MAX_STOCK_SYMBOL_LENGTH:
            raise InvalidStockSymbolError(symbol, f"Symbol must be {MAX_STOCK_SYMBOL_LENGTH} characters or less")

        if not symbol[0].isalpha():
            raise InvalidStockSymbolError(symbol, "Symbol must start with a letter")

        if not symbol.isalnum():
            raise InvalidStockSymbolError(symbol, "Symbol must contain only letters and numbers")

        # Check if stock is already being tracked
        stmt = select(TrackedStock).where(TrackedStock.symbol == symbol)
        result = await db.execute(stmt)
        existing_tracking = result.scalar_one_or_none()

        if existing_tracking:
            if existing_tracking.is_active:
                logger.info("Stock '%s' is already being tracked (active)", symbol)
                return existing_tracking
            else:
                logger.info("Stock '%s' is disabled and will remain disabled", symbol)
                return existing_tracking

        # Create new tracking entry
        logger.info("Creating new tracking entry for stock '%s'", symbol)
        new_tracking = TrackedStock(
            symbol=symbol,
            last_pull_date=datetime.now(UTC),
            last_pull_status=PullStatus.PENDING,
            is_active=True,
        )

        db.add(new_tracking)
        await db.commit()
        await db.refresh(new_tracking)

        logger.info("Successfully created tracking for stock '%s'", symbol)
        return new_tracking

    except (InvalidStockSymbolError, StockDataError):
        raise
    except Exception as e:
        logger.error("Unexpected error processing stock request for '%s': %s", symbol, str(e))
        await db.rollback()
        raise StockDataError(f"Failed to process stock tracking request: {e!s}") from e


async def get_tracked_stocks(db: AsyncSession) -> list[TrackedStock]:
    """Get all tracked stocks for admin access.

    This function retrieves all tracked stocks from the database, including
    both active and inactive entries. It's designed for administrative use.

    Args:
        db: Database session for operations

    Returns:
        List[TrackedStock]: List of all tracked stock objects

    Raises:
        StockDataError: For database or other operational errors
    """
    logger.info("Retrieving all tracked stocks for admin access")

    try:
        stmt = select(TrackedStock).order_by(TrackedStock.symbol)
        result = await db.execute(stmt)
        tracked_stocks = result.scalars().all()

        logger.info("Retrieved %d tracked stocks", len(tracked_stocks))
        return list(tracked_stocks)

    except Exception as e:
        logger.error("Error retrieving tracked stocks: %s", str(e))
        raise StockDataError(f"Failed to retrieve tracked stocks: {e!s}") from e


async def deactivate_stock_tracking(symbol: str, db: AsyncSession) -> TrackedStock:
    """Deactivate tracking for a specific stock symbol.

    This function deactivates tracking for a stock symbol, marking it as inactive
    but preserving the tracking record for potential reactivation.

    Args:
        symbol: Stock symbol to deactivate tracking for
        db: Database session for operations

    Returns:
        TrackedStock: The deactivated tracked stock object

    Raises:
        InvalidStockSymbolError: If the symbol format is invalid
        StockNotFoundError: If the stock is not being tracked
        StockDataError: For database or other operational errors
    """
    logger.info("Deactivating tracking for stock '%s'", symbol)

    try:
        # Validate symbol format
        if not symbol or not symbol.strip():
            raise InvalidStockSymbolError(symbol, "Symbol cannot be empty")

        symbol = symbol.strip().upper()

        # Find the tracked stock
        stmt = select(TrackedStock).where(TrackedStock.symbol == symbol)
        result = await db.execute(stmt)
        tracked_stock = result.scalar_one_or_none()

        if not tracked_stock:
            raise StockNotFoundError(symbol)

        if not tracked_stock.is_active:
            logger.info("Stock '%s' is already deactivated", symbol)
            return tracked_stock

        # Deactivate the tracking
        tracked_stock.is_active = False
        tracked_stock.last_pull_status = PullStatus.DISABLED
        tracked_stock.error_message = "Tracking deactivated by admin"

        await db.commit()
        await db.refresh(tracked_stock)

        logger.info("Successfully deactivated tracking for stock '%s'", symbol)
        return tracked_stock

    except (InvalidStockSymbolError, StockNotFoundError, StockDataError):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        logger.error("Unexpected error deactivating tracking for '%s': %s", symbol, str(e))
        await db.rollback()
        raise StockDataError(f"Failed to deactivate stock tracking: {e!s}") from e


async def get_active_tracked_stocks(db: AsyncSession) -> list[TrackedStock]:
    """Get only active tracked stocks.

    This function retrieves only the actively tracked stocks from the database.
    It's useful for background tasks that need to process only active stocks.

    Args:
        db: Database session for operations

    Returns:
        List[TrackedStock]: List of active tracked stock objects

    Raises:
        StockDataError: For database or other operational errors
    """
    logger.info("Retrieving active tracked stocks")

    try:
        stmt = select(TrackedStock).where(TrackedStock.is_active).order_by(TrackedStock.symbol)
        result = await db.execute(stmt)
        active_stocks = result.scalars().all()

        logger.info("Retrieved %d active tracked stocks", len(active_stocks))
        return list(active_stocks)

    except Exception as e:
        logger.error("Error retrieving active tracked stocks: %s", str(e))
        raise StockDataError(f"Failed to retrieve active tracked stocks: {e!s}") from e
