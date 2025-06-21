"""FastAPI endpoints for stock data retrieval.

This module provides REST API endpoints for tracking stock symbols and managing
stock data retrieval operations.

References:
    - [FastAPI Documentation](https://fastapi.tiangolo.com/)
    - [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
    - [Pydantic Documentation](https://docs.pydantic.dev/)

### Legal
SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from cream_api.db import get_async_db
from cream_api.stock_data.schemas import StockRequestCreate
from cream_api.stock_data.services import (
    InvalidStockSymbolError,
    StockDataError,
    process_stock_request,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stock-data", tags=["stock-data"])


@router.post("/track")
async def track_stock(
    request: StockRequestCreate,
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> dict:
    """Start tracking a new stock symbol.

    Args:
        request: StockRequestCreate containing the symbol to track
        db: Database session

    Returns:
        dict: Response indicating the stock is now being tracked

    Raises:
        HTTPException: If there's an error starting tracking
    """
    try:
        # Use the business logic service to process the request
        # Note: user_id is hardcoded as "system" for now since we don't have user auth yet
        await process_stock_request(request.symbol, "system", db)

        # Return simple response format that tests expect
        return {
            "status": "tracking",
            "message": f"Stock {request.symbol} is now being tracked",
            "symbol": request.symbol,
        }
    except InvalidStockSymbolError as e:
        logger.warning("Invalid stock symbol requested: %s", str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except StockDataError as e:
        logger.error("Stock data error: %s", str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
    except Exception as e:
        logger.error("Unexpected error tracking stock: %s", str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error") from e
