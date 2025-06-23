"""Database models for stock data.

This module defines SQLAlchemy ORM models for stock data storage and tracking.
It includes models for historical stock price data and stock tracking metadata
with proper indexing and constraints for optimal database performance.

References:
    - [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
    - [PostgreSQL Documentation](https://www.postgresql.org/docs/)

### Legal
SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Float, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from cream_api.db import ModelBase


class StockData(ModelBase):
    """Model for storing historical stock data.

    This model represents individual stock price records with OHLCV (Open, High, Low, Close, Volume)
    data for a specific symbol and date. It includes proper indexing on symbol and date
    for efficient querying, and a unique constraint to prevent duplicate records.

    Attributes:
        id: Unique identifier for the record
        symbol: Stock symbol (e.g., AAPL, MSFT)
        date: Date of the stock data
        open: Opening price for the day
        high: Highest price during the day
        low: Lowest price during the day
        close: Closing price for the day
        adj_close: Adjusted closing price (accounts for dividends/splits)
        volume: Trading volume for the day
    """

    __tablename__ = "stock_data"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol: Mapped[str] = mapped_column(String, nullable=False, index=True)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    adj_close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[int] = mapped_column(BigInteger, nullable=False)

    __table_args__ = (UniqueConstraint("symbol", "date", name="uix_symbol_date"),)


class TrackedStock(ModelBase):
    """Model for tracking when stock data was last pulled into the system.

    This model maintains metadata about stock data retrieval operations, including
    when data was last fetched, the status of the operation, and any error messages.
    It supports tracking multiple stocks with individual status monitoring.

    Attributes:
        id: Unique identifier for the tracking record
        symbol: Stock symbol being tracked
        last_pull_date: Timestamp of the last data pull attempt
        last_pull_status: Status of the last pull operation (pending, success, failed)
        error_message: Error message if the last pull failed
        is_active: Whether this stock is currently being tracked
    """

    __tablename__ = "tracked_stock"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol: Mapped[str] = mapped_column(String, nullable=False, index=True)
    last_pull_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(UTC))
    last_pull_status: Mapped[str] = mapped_column(String, nullable=False, default="pending")
    error_message: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (UniqueConstraint("symbol", name="uix_symbol"),)
