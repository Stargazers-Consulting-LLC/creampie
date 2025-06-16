"""Main FastAPI application module."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from stargazer_utils.logging import get_logger_for

from cream_api.settings import get_app_settings
from cream_api.users.routes import auth

logger: logging.Logger = get_logger_for(__name__)


settings = get_app_settings()

# Create required directories
logger.info("Creating directories...")
settings.HTML_RAW_RESPONSES_DIR.mkdir(exist_ok=True, parents=True)

app = FastAPI(title="Cream API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)

logger.info("App started.")


@app.get("/")
async def root() -> dict[str, str]:
    """Health check endpoint to verify API is running."""
    return {"app": "root"}
