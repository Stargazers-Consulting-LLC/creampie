"""Background tasks for the cream_api package."""

import asyncio
import logging
from collections.abc import Callable, Coroutine, Sequence
from typing import Any

from fastapi import BackgroundTasks
from stargazer_utils.logging import get_logger_for

from cream_api.stock_data.tasks import run_periodic_updates

logger: logging.Logger = get_logger_for(__name__)

__all__ = ["schedule_background_task", "start_background_tasks"]


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


# Type alias for background task functions
BackgroundTaskFunc = Callable[..., Coroutine[Any, Any, None]]


def schedule_background_task(
    background_tasks: BackgroundTasks,
    task_func: BackgroundTaskFunc,
    **kwargs: Any,
) -> None:
    """Schedule a background task.

    Args:
        background_tasks: FastAPI background tasks manager
        task_func: Async function to run in background
        **kwargs: Arguments to pass to the task function
    """
    background_tasks.add_task(task_func, **kwargs)
