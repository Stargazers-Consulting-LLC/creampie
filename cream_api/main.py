import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Required for background tasks and custom event loop operations
async_event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()

# Routers
# app.include_router()

# CORS configuration for local development
ORIGINS = ["http://localhost:3000", "localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/",
)
async def root() -> dict[str, str]:
    """Health check endpoint to verify API is running."""
    return {"app": "root"}
