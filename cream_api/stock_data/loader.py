"""Stock data loading functionality.

This module provides data loading, validation, transformation, and database storage
capabilities for stock data operations. It handles bulk data processing with
PostgreSQL-specific optimizations for performance and data integrity.

References:
    - [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
    - [Pandas Documentation](https://pandas.pydata.org/docs/)
    - [PostgreSQL Documentation](https://www.postgresql.org/docs/)

### Legal
SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

import logging
from itertools import batched
from typing import Any

import pandas as pd
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from stargazer_utils.logging import get_logger_for

from cream_api.stock_data.config import StockDataConfig, get_stock_data_config
from cream_api.stock_data.models import StockData

logger: logging.Logger = get_logger_for(__name__)


class StockDataLoader:
    """Loader for stock data operations including validation, transformation, and database storage.

    This class provides comprehensive data processing capabilities for stock data,
    including validation of data structure, transformation of raw data into database
    models, and efficient bulk storage operations with PostgreSQL-specific optimizations.

    The loader supports batch processing to handle large datasets efficiently and
    includes robust error handling and logging for production use.
    """

    def __init__(
        self,
        session: AsyncSession,
        config: StockDataConfig | None = None,
    ) -> None:
        """Initialize the loader with a database session.

        Args:
            session: AsyncSession for database operations
            config: Configuration instance (defaults to default config)
        """
        self.session = session
        self.config = config or get_stock_data_config()

    async def validate_data(self, data: dict[str, Any]) -> None:
        """Validate stock data structure.

        Args:
            data: Stock data to validate

        Raises:
            ValueError: If data structure is invalid or missing required fields
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
            data: Raw stock data dictionary

        Returns:
            List of validated StockData objects

        Raises:
            ValueError: If data validation fails
            Exception: If data transformation fails
        """
        try:
            logger.debug("Starting transform_data")
            await self.validate_data(data)
            logger.debug("Data validation passed")

            stock_data_list = []

            for i, price in enumerate(data["prices"]):
                try:
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
                except Exception as e:
                    logger.error(f"Error processing price record {i}: {type(e).__name__}: {e!s}")
                    logger.error(f"Problematic record: {price}")
                    raise

            return stock_data_list

        except Exception as e:
            logger.error(f"Error in transform_data: {type(e).__name__}: {e!s}")
            raise

    async def store_data(
        self,
        symbol: str,
        stock_data_list: list[StockData],
    ) -> None:
        """Store stock data in the database using ON CONFLICT DO UPDATE.

        This method uses PostgreSQL's ON CONFLICT DO UPDATE pattern to handle
        duplicate key violations gracefully. If a record with the same symbol
        and date already exists, it will be updated with the new values.

        Args:
            symbol: Stock symbol for the data
            stock_data_list: List of StockData objects to store

        Raises:
            psycopg.errors.InsufficientPrivilege: If database user lacks sequence permissions
            Exception: For other database errors
        """
        try:
            if not stock_data_list:
                logger.debug(f"No valid stock data to store for symbol {symbol}")
                return

            # Process in batches to avoid PostgreSQL parameter limit (65,535 parameters max)
            batch_size = 1000  # 1000 records * 8 parameters = 8000 parameters per batch
            total_records = len(stock_data_list)
            logger.info(f"Processing {total_records} records for {symbol} in batches of {batch_size}")

            for batch_num, batch in enumerate(batched(stock_data_list, batch_size), 1):
                total_batches = (total_records + batch_size - 1) // batch_size

                try:
                    # Prepare data for bulk upsert
                    upsert_data = []
                    for stock_data in batch:
                        upsert_data.append(
                            {
                                "symbol": symbol,
                                "date": stock_data.date,
                                "open": stock_data.open,
                                "high": stock_data.high,
                                "low": stock_data.low,
                                "close": stock_data.close,
                                "adj_close": stock_data.adj_close,
                                "volume": stock_data.volume,
                            }
                        )

                    # Use PostgreSQL-specific insert with ON CONFLICT DO UPDATE
                    stmt = pg_insert(StockData).values(upsert_data)

                    # Re-enable ON CONFLICT logic
                    stmt = stmt.on_conflict_do_update(
                        index_elements=["symbol", "date"],  # The unique constraint
                        set_={
                            "open": stmt.excluded.open,
                            "high": stmt.excluded.high,
                            "low": stmt.excluded.low,
                            "close": stmt.excluded.close,
                            "adj_close": stmt.excluded.adj_close,
                            "volume": stmt.excluded.volume,
                        },
                    )

                    await self.session.execute(stmt)
                    await self.session.commit()

                    logger.info(f"Successfully upserted batch {batch_num}/{total_batches} for {symbol}")

                except Exception as e:
                    logger.error(f"Error in batch {batch_num} for {symbol}: {type(e).__name__}: {e!s}")
                    raise

            logger.info(f"Successfully completed all batches for {symbol} ({total_records} total records)")

        except Exception as e:
            logger.error(f"Database error storing data for {symbol}: {type(e).__name__}: {e!s}")
            raise

    async def process_data(
        self,
        symbol: str,
        data: dict[str, Any],
    ) -> None:
        """Process and store stock data.

        Args:
            symbol: Stock symbol for the data
            data: Raw stock data dictionary

        Raises:
            Exception: If any step in the processing pipeline fails
        """
        try:
            logger.debug(f"Starting process_data for {symbol}")
            stock_data_list = await self.transform_data(data)
            logger.debug(f"Transformed {len(stock_data_list)} records for {symbol}")
            await self.store_data(symbol, stock_data_list)
            logger.debug(f"Completed process_data for {symbol}")
        except Exception as e:
            logger.error(f"Error processing data for {symbol}: {type(e).__name__}: {e!s}")
            raise
