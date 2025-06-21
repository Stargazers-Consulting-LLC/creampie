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
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_serializer

# Constants
MAX_STOCK_SYMBOL_LENGTH = 10


class PullStatus(str, Enum):
    """Enumeration for stock data pull status."""

    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    DISABLED = "disabled"


class StockRequestCreate(BaseModel):
    """Schema for creating a new stock tracking request.

    This schema validates stock symbol format and ensures proper input validation
    for stock tracking requests.
    """

    symbol: str = Field(
        ...,
        min_length=1,
        max_length=MAX_STOCK_SYMBOL_LENGTH,
        description="Stock symbol to track (2-10 characters, uppercase letters and digits only)",
        examples=["AAPL", "TSLA", "GOOGL", "MSFT"],
    )

    @field_validator("symbol")
    @classmethod
    def validate_symbol_format(cls, v: str) -> str:
        """Validate stock symbol format.

        Args:
            v: The symbol value to validate

        Returns:
            str: The validated symbol in uppercase

        Raises:
            ValueError: If the symbol format is invalid
        """
        # Check for whitespace characters in original input
        whitespace_chars = [" ", "\t", "\n", "\r", "\f", "\v"]
        if any(c in whitespace_chars for c in v):
            raise ValueError("Stock symbol cannot contain whitespace characters")

        # Convert to uppercase for consistency
        symbol = v.upper().strip()

        # Validate length
        if not (1 < len(symbol) <= MAX_STOCK_SYMBOL_LENGTH):
            raise ValueError("Stock symbol must be 2-10 characters long")

        # Validate format: uppercase letters and digits 0-9 only
        valid_chars = string.ascii_uppercase + string.digits
        if not all(c in valid_chars for c in symbol):
            raise ValueError("Stock symbol must contain only uppercase letters (A-Z) and digits (0-9)")

        # Additional validation: must start with a letter
        if symbol[0] not in string.ascii_uppercase:
            raise ValueError("Stock symbol must start with a letter (A-Z)")

        return symbol


class StockRequestResponse(BaseModel):
    """Schema for stock tracking request responses.

    This schema represents the response when a stock tracking request is processed,
    including the tracking status and relevant metadata.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique identifier for the tracked stock")
    symbol: str = Field(..., description="Stock symbol being tracked")
    is_active: bool = Field(..., description="Whether the stock tracking is currently active")
    last_pull_date: datetime | None = Field(None, description="Date and time of the last successful data pull")
    last_pull_status: PullStatus = Field(..., description="Status of the last data pull attempt")
    error_message: str | None = Field(None, description="Error message from the last failed pull attempt")
    created_at: datetime = Field(..., description="When the tracking request was created")

    @model_serializer
    def ser_model(self, info: Any) -> dict[str, Any]:
        """Custom serializer to handle datetime fields."""
        data = self.model_dump()
        # Convert datetime fields to ISO format
        if data.get("last_pull_date"):
            data["last_pull_date"] = data["last_pull_date"].isoformat()
        if data.get("created_at"):
            data["created_at"] = data["created_at"].isoformat()
        return data


class TrackedStockListResponse(BaseModel):
    """Schema for listing tracked stocks (admin endpoint).

    This schema provides a paginated list of all tracked stocks with their
    current status and metadata for administrative purposes.
    """

    stocks: list[StockRequestResponse] = Field(..., description="List of tracked stocks")
    total_count: int = Field(..., description="Total number of tracked stocks")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")


class StockTrackingUpdate(BaseModel):
    """Schema for updating stock tracking status.

    This schema allows administrators to update the tracking status
    of existing stock tracking requests.
    """

    is_active: bool = Field(..., description="Whether to activate or deactivate tracking")
    last_pull_status: PullStatus = Field(..., description="Status to set for the last pull attempt")
    error_message: str | None = Field(None, description="Error message to set for failed pulls")
