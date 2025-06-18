"""Stock data loading functionality."""

import logging
import os
import shutil
from typing import Any

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from cream_api.stock_data.config import StockDataConfig, get_stock_data_config
from cream_api.stock_data.models import StockData
from cream_api.stock_data.parser import StockDataParser

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
        """
        for stock_data in stock_data_list:
            stock_data.symbol = symbol
            self.session.add(stock_data)
        await self.session.commit()

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

    async def process_raw_files(self) -> None:
        """Process all HTML files in the raw responses directory."""
        parser = StockDataParser(config=self.config)

        for filename in os.listdir(self.config.raw_responses_dir):
            if filename.endswith(".html"):
                file_path = os.path.join(self.config.raw_responses_dir, filename)
                try:
                    symbol = filename.split("_")[0]
                    data = parser.parse_html_file(file_path)
                    await self.process_data(symbol, data)
                    dest_path = os.path.join(self.config.parsed_responses_dir, filename)
                    shutil.move(file_path, dest_path)

                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e!s}")
                    continue
