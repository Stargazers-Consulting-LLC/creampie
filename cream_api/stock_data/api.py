"""FastAPI endpoints for stock data retrieval.

This module provides REST API endpoints for tracking stock symbols and managing
stock data retrieval operations.

## Endpoints

### POST /stock-data/track
Start tracking a new stock symbol. This endpoint allows users to request
tracking for a specific stock symbol. The system will validate the symbol
format and either create a new tracking entry or return an existing one.

**Authentication:** Not required (will be added when user auth is implemented)

**Request Body:**
```json
{
    "symbol": "AAPL"
}
```

**Success Response (200):**
```json
{
    "status": "tracking",
    "message": "Stock AAPL is now being tracked",
    "symbol": "AAPL"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid stock symbol format
- `500 Internal Server Error`: Database or system error

### GET /stock-data/track
List all tracked stocks (admin only). This endpoint provides administrative
access to view all tracked stocks in the system, including their status
and metadata.

**Authentication:** Required (Bearer token)
**Authorization:** Admin role required (currently rejects all users)

**Success Response (200):**
```json
{
    "status": "success",
    "message": "Retrieved 3 tracked stocks",
    "stocks": [
        {
            "symbol": "AAPL",
            "is_active": true,
            "last_pull_date": "2024-01-15T10:30:00Z",
            "last_pull_status": "SUCCESS",
            "error_message": null
        }
    ]
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing authentication token
- `403 Forbidden`: User lacks admin privileges
- `500 Internal Server Error`: Database or system error

### DELETE /stock-data/tracked/{symbol}
Deactivate tracking for a specific stock symbol (admin only). This endpoint
allows administrators to disable tracking for a stock while preserving
the tracking record for potential reactivation.

**Authentication:** Required (Bearer token)
**Authorization:** Admin role required (currently rejects all users)

**Path Parameters:**
- `symbol`: Stock symbol to deactivate (e.g., "AAPL")

**Success Response (200):**
```json
{
    "status": "deactivated",
    "message": "Stock AAPL tracking has been deactivated",
    "symbol": "AAPL"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid stock symbol format
- `401 Unauthorized`: Invalid or missing authentication token
- `403 Forbidden`: User lacks admin privileges
- `404 Not Found`: Stock symbol not being tracked
- `500 Internal Server Error`: Database or system error

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
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from cream_api.common.constants import STOCK_DATA_PREFIX
from cream_api.common.exceptions import StockNotFoundError
from cream_api.db import get_async_db
from cream_api.stock_data.schemas import StockRequestCreate
from cream_api.stock_data.services import (
    InvalidStockSymbolError,
    StockDataError,
    process_stock_request,
)
from cream_api.users.models.app_user import AppUser
from cream_api.users.routes.auth import get_current_user_async

logger = logging.getLogger(__name__)

router = APIRouter(prefix=STOCK_DATA_PREFIX, tags=["stock-data"])


class StockTrackingResponse(BaseModel):
    """Response model for stock tracking operations."""

    status: str
    message: str
    symbol: str


class StockInfo(BaseModel):
    """Model for individual stock information."""

    symbol: str
    is_active: bool
    last_pull_date: str | None
    last_pull_status: str | None
    error_message: str | None


class TrackedStocksResponse(BaseModel):
    """Response model for listing tracked stocks."""

    status: str
    message: str
    stocks: list[StockInfo]


class StockDeactivationResponse(BaseModel):
    """Response model for stock deactivation."""

    status: str
    message: str
    symbol: str


@router.post(
    "/track",
    response_model=StockTrackingResponse,
    status_code=status.HTTP_200_OK,
    summary="Start tracking a stock symbol",
    description=(
        "Request tracking for a new stock symbol. The system validates the symbol format and creates a tracking entry."
    ),
)
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
        await process_stock_request(request.symbol, "system", db)

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


@router.get(
    "/track",
    response_model=TrackedStocksResponse,
    status_code=status.HTTP_200_OK,
    summary="List all tracked stocks (admin only)",
    description=(
        "Retrieve a list of all tracked stocks in the system. This endpoint requires "
        "admin privileges and is currently disabled until user roles are implemented."
    ),
)
async def list_tracked_stocks(
    current_user: Annotated[AppUser, Depends(get_current_user_async)],
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> dict:
    """List all tracked stocks (admin only).

    Args:
        current_user: Authenticated user (must be admin)
        db: Database session

    Returns:
        dict: Response containing list of tracked stocks

    Raises:
        HTTPException: If user is not authorized or there's an error
    """
    try:
        # For now, reject all users since admin roles aren't implemented
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required. User roles not yet implemented."
        )
    except HTTPException:
        raise
    except StockDataError as e:
        logger.error("Stock data error: %s", str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
    except Exception as e:
        logger.error("Unexpected error listing tracked stocks: %s", str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error") from e


@router.delete(
    "/tracked/{symbol}",
    response_model=StockDeactivationResponse,
    status_code=status.HTTP_200_OK,
    summary="Deactivate stock tracking (admin only)",
    description=(
        "Deactivate tracking for a specific stock symbol. This preserves the tracking "
        "record for potential reactivation. Requires admin privileges and is currently "
        "disabled until user roles are implemented."
    ),
)
async def deactivate_tracking(
    symbol: str,
    current_user: Annotated[AppUser, Depends(get_current_user_async)],
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> dict:
    """Deactivate tracking for a specific stock symbol (admin only).

    Args:
        symbol: Stock symbol to deactivate tracking for
        current_user: Authenticated user (must be admin)
        db: Database session

    Returns:
        dict: Response indicating the stock tracking has been deactivated

    Raises:
        HTTPException: If user is not authorized, symbol is invalid, or there's an error
    """
    try:
        # For now, reject all users since admin roles aren't implemented
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required. User roles not yet implemented."
        )

    except HTTPException:
        # Re-raise HTTP exceptions (like the 403 we just raised)
        raise
    except InvalidStockSymbolError as e:
        logger.warning("Invalid stock symbol for deactivation: %s", str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except StockNotFoundError as e:
        logger.warning("Stock not found for deactivation: %s", str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except StockDataError as e:
        logger.error("Stock data error: %s", str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
    except Exception as e:
        logger.error("Unexpected error deactivating stock tracking: %s", str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error") from e
