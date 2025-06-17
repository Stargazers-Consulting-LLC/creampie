"""Database models for stock data."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from cream_api.db import ModelBase


class StockData(ModelBase):
    """Model for storing historical stock data.

    Attributes:
        id: Primary key
        symbol: Stock symbol (e.g., 'AAPL')
        date: Date of the stock data
        open: Opening price
        high: Highest price during the day
        low: Lowest price during the day
        close: Closing price
        adj_close: Adjusted closing price
        volume: Trading volume
    """

    __tablename__ = "stock_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String, nullable=False, index=True)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    adj_close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        # Ensure we don't have duplicate data for the same symbol and date
        UniqueConstraint("symbol", "date", name="uix_symbol_date"),
    )


class TrackedStock(ModelBase):
    """Model for tracking when stock data was last pulled into the system.

    Attributes:
        id: Primary key (UUID)
        symbol: Stock symbol (e.g., 'AAPL')
        last_pull_date: Date when the stock data was last pulled
        last_pull_status: Status of the last pull attempt (success/failure)
        error_message: Optional error message if the last pull failed
        is_active: Whether the stock is currently being tracked for updates
    """

    __tablename__ = "tracked_stock"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol: Mapped[str] = mapped_column(String, nullable=False, index=True)
    last_pull_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(UTC))
    last_pull_status: Mapped[str] = mapped_column(String, nullable=False, default="pending")
    error_message: Mapped[str] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (
        # Ensure we don't have duplicate tracking entries for the same symbol
        UniqueConstraint("symbol", name="uix_symbol"),
    )
