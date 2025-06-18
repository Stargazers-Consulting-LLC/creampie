"""Background tasks for the cream_api package."""

import asyncio
import logging
from collections.abc import Callable, Coroutine, Sequence
from typing import Any

from fastapi import BackgroundTasks
from stargazer_utils.logging import get_logger_for

from cream_api.stock_data.tasks import run_periodic_file_processing, run_periodic_updates

logger: logging.Logger = get_logger_for(__name__)


BackgroundTaskFunc = Callable[..., Coroutine[Any, Any, None]]

__all__ = ["schedule_background_task", "start_background_tasks"]


async def start_background_tasks() -> None:
    """Start all background tasks during application startup.

    This function initializes and runs all background tasks concurrently.
    Tasks run indefinitely until an error occurs or the application shuts down.

    Raises:
        Exception: If any background task fails
    """
    tasks: Sequence[asyncio.Task] = [
        asyncio.create_task(run_periodic_updates()),
        asyncio.create_task(run_periodic_file_processing()),
    ]

    logger.info("Started %d background tasks", len(tasks))

    try:
        await asyncio.gather(*tasks)
    except Exception as e:
        logger.error("Background task failed: %s", str(e))
        raise


def schedule_background_task(
    background_tasks: BackgroundTasks,
    task_func: BackgroundTaskFunc,
    **kwargs: Any,
) -> None:
    """Schedule a background task using FastAPI's background task manager.

    Args:
        background_tasks: FastAPI background tasks manager
        task_func: Async function to run in background
        **kwargs: Arguments to pass to the task function
    """
    background_tasks.add_task(task_func, **kwargs)
