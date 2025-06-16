"""Stock data processing functionality."""

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cream_api.stock_data.exceptions import ValidationError
from cream_api.stock_data.models import StockData


class StockDataManager:
    """
    Manager for stock data operations including validation, transformation, and database management.
    """

    def __init__(self, session: AsyncSession):
        """Initialize the manager with a database session.

        Args:
            session: AsyncSession for database operations
        """
        self.session = session

    async def validate_data(self, data: dict[str, Any]) -> None:
        """Validate stock data structure.

        Args:
            data: Stock data to validate

        Raises:
            ValidationError: If data is invalid
        """
        if not isinstance(data, dict):
            raise ValidationError(
                "", [{"error": "Invalid data format", "details": "Data must be a dictionary"}]
            )

        if "prices" not in data:
            raise ValidationError(
                "", [{"error": "Missing prices", "details": "Data must contain prices"}]
            )

        if not data["prices"]:
            raise ValidationError(
                "", [{"error": "Empty prices", "details": "Prices list cannot be empty"}]
            )

        required_fields = {"date", "open", "high", "low", "close", "adj_close", "volume"}
        for price in data["prices"]:
            missing_fields = required_fields - set(price.keys())
            if missing_fields:
                raise ValidationError(
                    "",
                    [
                        {
                            "error": "Missing fields",
                            "details": f"Missing required fields: {missing_fields}",
                        }
                    ],
                )

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
    ) -> list[StockData]:
        """Process and store stock data.

        Args:
            data: Raw stock data
            symbol: Stock symbol

        Returns:
            List of stored StockData objects
        """
        stock_data_list = await self.transform_data(data)
        await self.store_data(symbol, stock_data_list)
        return stock_data_list

    async def get_historical_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str | None = None,
    ) -> list[StockData]:
        """
        Get historical stock data from the database.

        Args:
            symbol: Stock symbol
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format (defaults to today)

        Returns:
            List of StockData objects
        """
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")

        result = await self.session.execute(
            select(StockData)
            .where(StockData.symbol == symbol)
            .where(StockData.date >= datetime.strptime(start_date, "%Y-%m-%d"))
            .where(StockData.date <= datetime.strptime(end_date, "%Y-%m-%d"))
            .order_by(StockData.date)
        )
        return list(result.scalars().all())
