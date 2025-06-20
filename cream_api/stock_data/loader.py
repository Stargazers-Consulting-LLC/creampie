"""Stock data loading functionality."""

import logging
from typing import Any

import pandas as pd
import psycopg.errors
from sqlalchemy.ext.asyncio import AsyncSession

from cream_api.stock_data.config import StockDataConfig, get_stock_data_config
from cream_api.stock_data.models import StockData

logger = logging.getLogger(__name__)


class StockDataLoader:
    """Loader for stock data operations including validation, transformation, and database storage."""

    def __init__(
        self,
        session: AsyncSession,
        config: StockDataConfig | None = None,
    ):
        """Initialize the loader with a database session.

        Args:
            session: AsyncSession for database operations
            config: StockDataConfig instance (defaults to default config)
        """
        self.session = session
        self.config = config or get_stock_data_config()

    async def validate_data(self, data: dict[str, Any]) -> None:
        """Validate stock data structure.

        Args:
            data: Stock data to validate

        Raises:
            ValueError: If data is invalid
        """
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")

        if "prices" not in data:
            raise ValueError("Data must contain prices")

        if not data["prices"]:
            raise ValueError("Prices list cannot be empty")

        required_fields = {"date", "open", "high", "low", "close", "adj_close", "volume"}

        for i, price in enumerate(data["prices"]):
            missing_fields = required_fields - set(price.keys())
            if missing_fields:
                logger.error(f"Record {i} missing fields: {missing_fields}")
                raise ValueError(f"Missing required fields: {missing_fields}")

    async def transform_data(self, data: dict[str, Any]) -> list[StockData]:
        """Transform raw data into StockData objects.

        Args:
            data: Raw stock data

        Returns:
            List of StockData objects
        """
        await self.validate_data(data)
        stock_data_list = []

        for price in data["prices"]:
            volume_str = str(price["volume"]).replace(",", "")
            volume_numeric = pd.to_numeric(volume_str, errors="coerce")
            if pd.isna(volume_numeric) or volume_numeric <= 0:
                continue

            stock_data = StockData(
                date=pd.to_datetime(price["date"]),
                open=pd.to_numeric(price["open"], errors="coerce"),
                high=pd.to_numeric(price["high"], errors="coerce"),
                low=pd.to_numeric(price["low"], errors="coerce"),
                close=pd.to_numeric(price["close"], errors="coerce"),
                adj_close=pd.to_numeric(price["adj_close"], errors="coerce"),
                volume=int(volume_numeric),
            )
            stock_data_list.append(stock_data)

        return stock_data_list

    async def store_data(
        self,
        symbol: str,
        stock_data_list: list[StockData],
    ) -> None:
        """Store stock data in the database.

        Args:
            stock_data_list: List of StockData objects to store
            symbol: Stock symbol

        Raises:
            psycopg.errors.InsufficientPrivilege: If database user lacks sequence permissions
            Exception: For other database errors
        """
        try:
            for stock_data in stock_data_list:
                stock_data.symbol = symbol
                self.session.add(stock_data)
            await self.session.commit()
        except psycopg.errors.InsufficientPrivilege as e:
            logger.error(f"Database permission error for symbol {symbol}: {e}")
            logger.error("User lacks permission to access sequence stock_data_id_seq")
            logger.error("Please grant USAGE privilege on the sequence or ensure proper database permissions")
            raise
        except Exception as e:
            logger.error(f"Database error storing data for symbol {symbol}: {e}")
            raise

    async def process_data(
        self,
        symbol: str,
        data: dict[str, Any],
    ) -> None:
        """Process and store stock data.

        Args:
            data: Raw stock data
            symbol: Stock symbol
        """
        stock_data_list = await self.transform_data(data)
        await self.store_data(symbol, stock_data_list)
