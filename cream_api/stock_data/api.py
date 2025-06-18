"""FastAPI endpoints for stock data retrieval."""

import logging
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cream_api.db import get_async_db
from cream_api.stock_data.models import TrackedStock

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stock-data", tags=["stock-data"])


class TrackStockRequest(BaseModel):
    """Request model for tracking a new stock."""

    symbol: str = Field(..., min_length=1, description="Stock symbol to track")


@router.post("/track")
async def track_stock(
    request: TrackStockRequest,
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> dict:
    """Start tracking a new stock symbol.

    Args:
        request: TrackStockRequest containing the symbol to track
        background_tasks: FastAPI background tasks manager
        db: Database session

    Returns:
        dict: Response indicating the stock is now being tracked

    Raises:
        HTTPException: If there's an error starting tracking
    """
    try:
        # Check if stock is already being tracked
        stmt = select(TrackedStock).where(TrackedStock.symbol == request.symbol)
        result = await db.execute(stmt)
        existing_tracking = result.scalar_one_or_none()

        if not existing_tracking:
            # Create new tracking entry
            new_tracking = TrackedStock(
                symbol=request.symbol,
                last_pull_date=datetime.now(),
                last_pull_status="pending",
                is_active=True,
            )
            db.add(new_tracking)
            await db.commit()

        return {
            "status": "tracking",
            "message": f"Stock {request.symbol} is now being tracked",
            "symbol": request.symbol,
        }
    except Exception as e:
        await db.rollback()
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=str(e)) from e
