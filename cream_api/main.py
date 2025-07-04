"""Main FastAPI application module.

This module sets up the FastAPI application with all necessary middleware,
routers, and event handlers. It also configures the application's lifespan
for proper startup and shutdown handling with background task management.

References:
    - [FastAPI Documentation](https://fastapi.tiangolo.com/)
    - [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

### Legal
SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

import logging
import os
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from cream_api.background_tasks import start_background_tasks
from cream_api.common.constants import API_PREFIX
from cream_api.settings import configure_logging, get_app_settings
from cream_api.stock_data.api import router as stock_data_router
from cream_api.stock_data.config import get_stock_data_config
from cream_api.users.routes.auth import router as auth_router

settings = get_app_settings()

# Configure logging using settings
configure_logging(settings)

logger = logging.getLogger(__name__)

# Create required directories
logger.info("Creating directories...")
stock_data_config = get_stock_data_config()
os.makedirs(stock_data_config.raw_responses_dir, exist_ok=True)
os.makedirs(stock_data_config.parsed_responses_dir, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Handle application startup and shutdown events.

    This context manager is responsible for:
    1. Starting background tasks on application startup
    2. Logging application lifecycle events
    3. Cleaning up resources on shutdown

    Args:
        app: The FastAPI application instance

    Yields:
        None: The context manager yields nothing
    """
    # Startup
    logger.info("Starting up application...")

    if settings.enable_background_tasks:
        await start_background_tasks()
    else:
        logger.info("Background tasks are disabled in settings")
    logger.info("App started.")
    yield
    # Shutdown
    logger.info("App shutting down.")


app = FastAPI(title="Cream API", lifespan=lifespan)


# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    """Log all incoming requests for debugging.

    This middleware logs detailed information about all incoming HTTP requests
    including method, URL, headers, and response status for debugging purposes.

    Args:
        request: The incoming HTTP request
        call_next: Function to call the next middleware/route handler

    Returns:
        Response: The HTTP response from the application
    """
    logger.info(f"Incoming request: {request.method} {request.url}")
    logger.info(f"Request headers: {dict(request.headers)}")

    response = await call_next(request)

    logger.info(f"Response status: {response.status_code}")
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(stock_data_router, prefix=API_PREFIX)


@app.get("/")
async def root() -> dict[str, str]:
    """Health check endpoint to verify API is running.

    Returns:
        dict[str, str]: Simple health check response
    """
    return {"app": "root"}


logger.info("App started.")
