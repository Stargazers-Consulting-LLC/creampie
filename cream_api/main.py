"""Main FastAPI application module."""

import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from cream_api.users.routes import auth

app = FastAPI(title="Cream API")

# Required for background tasks and custom event loop operations
async_event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()

# Enables frontend to make API requests during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)


@app.get(
    "/",
)
async def root() -> dict[str, str]:
    """Health check endpoint to verify API is running."""
    return {"app": "root"}
