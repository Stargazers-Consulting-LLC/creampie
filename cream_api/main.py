"""Main FastAPI application module.

This module sets up the FastAPI application with all necessary middleware,
routers, and event handlers. It also configures the application's lifespan
for proper startup and shutdown handling.
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from stargazer_utils.logging import get_logger_for

from cream_api.background_tasks import start_background_tasks
from cream_api.settings import get_app_settings
from cream_api.stock_data.config import get_stock_data_config
from cream_api.users.routes import auth

logger: logging.Logger = get_logger_for(__name__)

settings = get_app_settings()

# Create required directories
logger.info("Creating directories...")
stock_data_config = get_stock_data_config()
stock_data_config.raw_responses_dir.mkdir(exist_ok=True, parents=True)
stock_data_config.parsed_responses_dir.mkdir(exist_ok=True, parents=True)


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)


@app.get("/")
async def root() -> dict[str, str]:
    """Health check endpoint to verify API is running."""
    return {"app": "root"}


logger.info("App started.")
