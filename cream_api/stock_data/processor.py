"""Stock data processing functionality."""

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cream_api.stock_data.exceptions import ValidationError
from cream_api.stock_data.models import StockData


class DataProcessor:
    """Processor for stock data validation, transformation, and storage."""

    def __init__(self, session: AsyncSession):
        """Initialize the processor with a database session.

        Args:
            session: AsyncSession for database operations
        """
        self.session = session

    def validate_data(self, data: dict[str, Any], symbol: str) -> list[dict[str, str]]:
        """Validate stock data for required fields and data types.

        Args:
            data: Dictionary containing stock data
            symbol: Stock symbol for error reporting

        Returns:
            List of validation errors, empty if data is valid

        Raises:
            ValidationError: If data fails validation
        """
        errors = []
        required_fields = ["prices", "symbol", "currency"]

        # Check required fields
        for field in required_fields:
            if field not in data:
                errors.append(
                    {"error": "Missing required field", "details": f"Field '{field}' is required"}
                )

        if not data.get("prices"):
            errors.append({"error": "Empty data", "details": "No price data found"})

        if errors:
            raise ValidationError(symbol, errors)

        return []

    def transform_data(self, data: dict[str, Any]) -> list[StockData]:
        """Transform raw stock data into StockData model instances.

        Args:
            data: Dictionary containing stock data

        Returns:
            List of StockData model instances
        """
        stock_data_list = []
        symbol = data["symbol"]

        for price in data["prices"]:
            try:
                # Convert date string to datetime
                date = datetime.strptime(price["date"], "%Y-%m-%d")

                # Create StockData instance
                stock_data = StockData(
                    symbol=symbol,
                    date=date,
                    open=float(price["open"]),
                    high=float(price["high"]),
                    low=float(price["low"]),
                    close=float(price["close"]),
                    adj_close=float(price["adj_close"]),
                    volume=int(price["volume"]),
                )
                stock_data_list.append(stock_data)
            except (ValueError, KeyError) as e:
                raise ValidationError(
                    symbol,
                    [
                        {
                            "error": "Data transformation error",
                            "details": f"Failed to transform price data: {e!s}",
                        }
                    ],
                ) from e

        return stock_data_list

    async def store_data(self, stock_data_list: list[StockData]) -> None:
        """Store stock data in the database.

        Args:
            stock_data_list: List of StockData model instances to store

        Raises:
            ValidationError: If data storage fails
        """
        try:
            # Check for existing data to avoid duplicates
            for stock_data in stock_data_list:
                query = select(StockData).where(
                    StockData.symbol == stock_data.symbol, StockData.date == stock_data.date
                )
                result = await self.session.execute(query)
                existing = result.scalar_one_or_none()

                if existing:
                    # Update existing record
                    for key, value in stock_data.__dict__.items():
                        if not key.startswith("_"):
                            setattr(existing, key, value)
                else:
                    # Add new record
                    self.session.add(stock_data)

            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise ValidationError(
                stock_data_list[0].symbol if stock_data_list else "unknown",
                [{"error": "Data storage error", "details": f"Failed to store data: {e!s}"}],
            ) from e

    async def process_data(self, data: dict[str, Any], symbol: str) -> None:
        """Process stock data through validation, transformation, and storage.

        Args:
            data: Dictionary containing stock data
            symbol: Stock symbol for error reporting

        Raises:
            ValidationError: If any processing step fails
        """
        # Validate data
        self.validate_data(data, symbol)

        # Transform data
        stock_data_list = self.transform_data(data)

        # Store data
        await self.store_data(stock_data_list)
