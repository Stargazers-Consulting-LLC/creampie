"""Background tasks for stock data operations."""

import asyncio
import logging
import os
import shutil
from datetime import datetime

import psycopg.errors
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cream_api.db import AsyncSessionLocal
from cream_api.stock_data.config import get_stock_data_config
from cream_api.stock_data.loader import StockDataLoader
from cream_api.stock_data.models import TrackedStock
from cream_api.stock_data.processor import FileProcessor
from cream_api.stock_data.retriever import StockDataRetriever

logger = logging.getLogger(__name__)

RETRIEVAL_INTERVAL_SECONDS = 5 * 60
PROCESSING_INTERVAL_SECONDS = 10 * 60
DEADLETTER_RETRY_INTERVAL_SECONDS = 24 * 60 * 60

config = get_stock_data_config()


async def retrieve_historical_data_task(symbol: str, end_date: str | None = None) -> None:
    """Retrieve historical stock data for a given symbol.

    Args:
        symbol: Stock symbol to retrieve data for
        end_date: Optional end date in YYYY-MM-DD format
    """
    retriever = StockDataRetriever(config=config)
    await retriever.get_historical_data(symbol=symbol, end_date=end_date)


async def process_raw_files_task() -> None:
    """Process raw HTML files and load data into database."""
    if not os.path.exists(config.raw_responses_dir):
        logger.info("Raw responses directory does not exist, skipping file processing")
        return

    try:
        async with AsyncSessionLocal() as session:
            loader = StockDataLoader(session=session, config=config)
            processor = FileProcessor(loader=loader, config=config)
            await processor.process_raw_files()
            logger.info("Successfully completed file processing task")
    except psycopg.errors.InsufficientPrivilege as e:
        logger.error("Database permission error in file processing task: %s", type(e).__name__)
        raise
    except Exception as e:
        # Extract only the essential error information
        error_type = type(e).__name__
        error_msg = str(e)

        # Remove the massive parameter dump from the error message
        if "[parameters:" in error_msg:
            error_msg = error_msg.split("[parameters:")[0].strip()

        logger.error("Error during file processing task: %s: %s", error_type, error_msg)
        raise


async def retry_deadletter_files_task() -> None:
    """Move all files from the deadletter directory back to the raw directory every 24 hours."""
    while True:
        logger.info("retry_deadletter_files_task() heartbeat.")
        try:
            deadletter_dir = config.deadletter_responses_dir
            raw_dir = config.raw_responses_dir
            for filename in os.listdir(deadletter_dir):
                src_path = os.path.join(deadletter_dir, filename)
                dest_path = os.path.join(raw_dir, filename)
                try:
                    if os.path.exists(dest_path):
                        logger.warning("File already exists in raw directory, skipping: %s", dest_path)
                    else:
                        logger.info("Moving %s back to raw directory.", src_path)
                        shutil.move(src_path, dest_path)
                except Exception as move_error:
                    logger.critical("Failed to move %s to raw: %s", src_path, move_error)
        except Exception as e:
            # Extract only the essential error information
            error_type = type(e).__name__
            error_msg = str(e)

            # Remove the massive parameter dump from the error message
            if "[parameters:" in error_msg:
                error_msg = error_msg.split("[parameters:")[0].strip()

            logger.error("Error in deadletter retry: %s: %s", error_type, error_msg)

        logger.debug("Sleeping for %d seconds", DEADLETTER_RETRY_INTERVAL_SECONDS)
        await asyncio.sleep(DEADLETTER_RETRY_INTERVAL_SECONDS)


async def update_all_tracked_stocks(db: AsyncSession) -> None:
    """Update all tracked stocks with latest data.

    Args:
        db: Database session for tracking stock updates
    """
    try:
        stmt = select(TrackedStock).where(TrackedStock.is_active)
        result = await db.execute(stmt)
        tracked_stocks = result.scalars().all()
        logger.info("Found %d tracked stocks", len(tracked_stocks))

        for stock in tracked_stocks:
            stock.last_pull_date = datetime.now()
            try:
                await retrieve_historical_data_task(symbol=stock.symbol)
                stock.last_pull_status = "success"
            except Exception as e:
                stock.last_pull_status = "failure"
                # Clean error message for storage
                error_msg = str(e)
                if "[parameters:" in error_msg:
                    error_msg = error_msg.split("[parameters:")[0].strip()
                stock.error_message = error_msg
            await db.commit()
    except Exception:
        await db.rollback()
        raise


async def run_periodic_updates() -> None:
    """Run periodic updates of tracked stocks."""
    while True:
        logger.info("run_periodic_updates() heartbeat.")
        try:
            async with AsyncSessionLocal() as session:
                await update_all_tracked_stocks(session)
                logger.info("Successfully updated all tracked stocks")
        except Exception as e:
            # Extract only the essential error information
            error_type = type(e).__name__
            error_msg = str(e)

            # Remove the massive parameter dump from the error message
            if "[parameters:" in error_msg:
                error_msg = error_msg.split("[parameters:")[0].strip()

            logger.error("Error updating tracked stocks: %s: %s", error_type, error_msg)
            return
        else:
            logger.debug("Sleeping for %d seconds", RETRIEVAL_INTERVAL_SECONDS)
            await asyncio.sleep(RETRIEVAL_INTERVAL_SECONDS)


async def run_periodic_file_processing() -> None:
    """Run periodic processing of raw HTML files every 10 minutes."""
    while True:
        logger.info("run_periodic_file_processing() heartbeat.")
        try:
            await process_raw_files_task()
            logger.info("Successfully completed file processing cycle")
        except RuntimeError as e:
            logger.critical("Critical application logic failure in file processing: %s", str(e))
        except Exception as e:
            # Extract only the essential error information
            error_type = type(e).__name__
            error_msg = str(e)

            # Remove the massive parameter dump from the error message
            if "[parameters:" in error_msg:
                error_msg = error_msg.split("[parameters:")[0].strip()

            logger.error("Error during periodic file processing: %s: %s", error_type, error_msg)
        else:
            logger.debug("Sleeping for %d seconds", PROCESSING_INTERVAL_SECONDS)
            await asyncio.sleep(PROCESSING_INTERVAL_SECONDS)
