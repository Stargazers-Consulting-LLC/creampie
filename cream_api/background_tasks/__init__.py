"""Background tasks for the cream_api package."""

import asyncio
import logging
from collections.abc import Sequence

from stargazer_utils.logging import get_logger_for

from cream_api.background_tasks.stock_updates import run_periodic_updates

logger: logging.Logger = get_logger_for(__name__)

__all__ = ["run_periodic_updates"]


async def start_background_tasks() -> None:
    """Start all background tasks.

    This function should be called during application startup to initialize
    all background tasks. New tasks should be added to the tasks list.
    """
    tasks: Sequence[asyncio.Task] = [
        asyncio.create_task(run_periodic_updates(), name="stock_updates"),
        # Add new background tasks here
    ]

    logger.info("Started %d background tasks", len(tasks))

    # Wait for all tasks to complete (they shouldn't unless there's an error)
    try:
        await asyncio.gather(*tasks)
    except Exception as e:
        logger.error("Background task failed: %s", str(e))
        # Re-raise to ensure the application knows about the failure
        raise
