"""Database models for stock data."""

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, UniqueConstraint
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
