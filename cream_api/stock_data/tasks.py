"""Background tasks for stock data operations."""

import asyncio
import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from stargazer_utils.logging import get_logger_for

from cream_api.db import AsyncSessionLocal
from cream_api.stock_data.models import TrackedStock
from cream_api.stock_data.retriever import StockDataRetriever

logger: logging.Logger = get_logger_for(__name__)


async def retrieve_historical_data_task(symbol: str, end_date: str | None) -> None:
    """Background task to retrieve historical stock data.

    Args:
        symbol: Stock symbol to retrieve data for
        end_date: Optional end date in YYYY-MM-DD format
    """
    retriever = StockDataRetriever()
    await retriever.get_historical_data(
        symbol=symbol,
        end_date=end_date,
    )


async def update_all_tracked_stocks(db: AsyncSession) -> None:
    """Update all tracked stocks.

    Args:
        db: Database session
    """
    try:
        # Get all active tracked stocks
        stmt = select(TrackedStock).where(TrackedStock.is_active)
        result = await db.execute(stmt)
        tracked_stocks = result.scalars().all()

        # Update each tracked stock
        for stock in tracked_stocks:
            try:
                await retrieve_historical_data_task(symbol=stock.symbol, end_date=None)
                stock.last_pull_status = "success"
                stock.last_pull_date = datetime.now()
            except Exception as e:
                stock.last_pull_status = "failure"
                stock.error_message = str(e)
                stock.last_pull_date = datetime.now()

        await db.commit()
    except Exception as e:
        await db.rollback()
        raise e


async def run_periodic_updates() -> None:
    """Run periodic updates of tracked stocks."""
    while True:
        try:
            async with AsyncSessionLocal() as session:
                await update_all_tracked_stocks(session)
                logger.info("Successfully updated all tracked stocks")
        except Exception as e:
            logger.error("Error updating tracked stocks: %s", str(e))

        # Wait 5 minutes before retrying if there was an error
        await asyncio.sleep(5 * 60)
