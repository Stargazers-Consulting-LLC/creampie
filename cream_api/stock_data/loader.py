"""Stock data loading functionality."""

import shutil
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from cream_api.stock_data.config import StockDataConfig, get_stock_data_config
from cream_api.stock_data.models import StockData
from cream_api.stock_data.parser import StockDataParser


class StockDataLoader:
    """
    Loader for stock data operations including validation, transformation, and database storage.
    """

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
        for price in data["prices"]:
            missing_fields = required_fields - set(price.keys())
            if missing_fields:
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
            stock_data = StockData(
                date=datetime.strptime(price["date"], "%Y-%m-%d"),
                open=float(price["open"]),
                high=float(price["high"]),
                low=float(price["low"]),
                close=float(price["close"]),
                adj_close=float(price["adj_close"]),
                volume=int(price["volume"]),
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
        """Process all HTML files in the raw responses directory.

        For each file:
        1. Parses the HTML content using StockDataParser
        2. Stores the data in the database
        3. Moves the file to the parsed responses directory
        """
        parser = StockDataParser(config=self.config)

        # Process each file in the raw directory
        for file_path in self.config.raw_responses_dir.glob("*.html"):
            try:
                # Extract symbol from filename (assuming format: SYMBOL_YYYY-MM-DD.html)
                symbol = file_path.stem.split("_")[0]

                # Parse the HTML file
                data = parser.parse_html_file(str(file_path))

                # Process and store the data
                await self.process_data(symbol, data)

                # Move file to parsed directory
                shutil.move(str(file_path), str(self.config.parsed_responses_dir / file_path.name))

            except Exception as e:
                print(f"Error processing file {file_path}: {e!s}")
                continue
