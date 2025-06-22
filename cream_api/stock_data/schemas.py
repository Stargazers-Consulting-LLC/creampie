"""Pydantic schemas for stock tracking requests.

This module provides Pydantic models for validating stock tracking request data,
including input validation, response models, and admin listing schemas.

References:
    - [Pydantic Documentation](https://docs.pydantic.dev/)
    - [FastAPI Documentation](https://fastapi.tiangolo.com/)
    - [Python Type Hints](https://docs.python.org/3/library/typing.html)

### Legal
SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

import string
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator

from cream_api.stock_data.constants import MAX_STOCK_SYMBOL_LENGTH


class PullStatus(str, Enum):
    """Enumeration for stock data pull status."""

    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    DISABLED = "disabled"


class StockRequestCreate(BaseModel):
    """Schema for creating a new stock tracking request."""

    symbol: str = Field(..., min_length=1, max_length=MAX_STOCK_SYMBOL_LENGTH, description="Stock symbol to track")

    @field_validator("symbol")
    @classmethod
    def validate_symbol_format(cls, v: str) -> str:
        """Validate stock symbol format."""
        # User-friendly normalization: trim whitespace and convert to uppercase
        symbol = v.strip().upper()

        # Check for remaining whitespace/newlines (shouldn't happen after strip, but safety check)
        if any(c in string.whitespace for c in symbol):
            raise ValueError("Stock symbol cannot contain whitespace, newlines, or tabs")

        if not (1 < len(symbol) <= MAX_STOCK_SYMBOL_LENGTH):
            raise ValueError("Stock symbol must be 2-10 characters long")

        valid_chars = string.ascii_uppercase + string.digits
        if not all(c in valid_chars for c in symbol):
            raise ValueError("Stock symbol must contain only uppercase letters (A-Z) and digits (0-9)")

        if symbol[0] not in string.ascii_uppercase:
            raise ValueError("Stock symbol must start with a letter (A-Z)")

        return symbol


class StockRequestResponse(BaseModel):
    """Schema for stock tracking request response."""

    id: str = Field(..., description="Unique identifier for the tracking request")
    symbol: str = Field(..., description="Stock symbol being tracked")
    is_active: bool = Field(..., description="Whether the tracking is currently active")
    last_pull_date: datetime = Field(..., description="Last time data was pulled for this symbol")
    last_pull_status: PullStatus = Field(..., description="Status of the last data pull attempt")
    error_message: str | None = Field(None, description="Error message from last failed pull attempt")


class TrackedStockListResponse(BaseModel):
    """Schema for listing tracked stocks (admin endpoint)."""

    stocks: list[StockRequestResponse] = Field(..., description="List of tracked stocks")
    total_count: int = Field(..., description="Total number of tracked stocks")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")


class StockTrackingUpdate(BaseModel):
    """Schema for updating stock tracking status."""

    is_active: bool = Field(..., description="Whether to activate or deactivate tracking")
    last_pull_status: PullStatus = Field(..., description="Status to set for the last pull attempt")
    error_message: str | None = Field(None, description="Error message to set for failed pulls")
