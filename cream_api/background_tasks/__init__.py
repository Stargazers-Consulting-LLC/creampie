"""Background tasks for the cream_api package.

This module provides functionality for managing background tasks in the FastAPI application,
including starting periodic tasks during application startup and scheduling one-off tasks
using FastAPI's background task manager.
"""

import asyncio
import logging
from collections.abc import Callable, Coroutine, Sequence
from typing import Any

from fastapi import BackgroundTasks

from cream_api.stock_data.tasks import retry_deadletter_files_task, run_periodic_file_processing, run_periodic_updates

logger = logging.getLogger(__name__)

BackgroundTaskFunc = Callable[..., Coroutine[Any, Any, None]]

__all__ = ["schedule_background_task", "start_background_tasks"]


async def start_background_tasks() -> None:
    """Start all background tasks during application startup.

    This function initializes and runs all background tasks concurrently.
    Tasks run indefinitely until an error occurs or the application shuts down.

    Note: Tasks are started but not awaited, allowing them to run in the background
    while the server continues to start up.

    The following tasks are started:
    - run_periodic_updates: Updates tracked stocks every 5 minutes
    - run_periodic_file_processing: Processes raw files every 10 minutes
    - retry_deadletter_files_task: Processes deadletter files
    """
    tasks: Sequence[asyncio.Task] = [
        asyncio.create_task(run_periodic_updates()),
        asyncio.create_task(run_periodic_file_processing()),
        asyncio.create_task(retry_deadletter_files_task()),
    ]

    logger.info("Started %d background tasks", len(tasks))


def schedule_background_task(
    background_tasks: BackgroundTasks,
    task_func: BackgroundTaskFunc,
    **kwargs: Any,
) -> None:
    """Schedule a background task using FastAPI's background task manager.

    This function adds a task to FastAPI's background task queue, which will be
    executed after the response is sent to the client.

    Args:
        background_tasks: FastAPI background tasks manager instance
        task_func: Async function to run in background
        **kwargs: Arguments to pass to the task function

    Example:
        schedule_background_task(
            background_tasks,
            process_stock_data,
            symbol="AAPL",
            date="2025-01-27"
        )
    """
    background_tasks.add_task(task_func, **kwargs)
