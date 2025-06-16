"""Stock data retrieval functionality."""

from datetime import datetime
from typing import Any, cast

import aiohttp
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from cream_api.common.http import HTTP_OK
from cream_api.stock_data.exceptions import APIError, ValidationError
from cream_api.stock_data.models import StockData


class StockDataRetriever:
    """Retriever for historical stock data from Yahoo Finance."""

    def __init__(self, session: AsyncSession):
        """Initialize the retriever with a database session.

        Args:
            session: AsyncSession for database operations
        """
        self.session = session
        self.base_url = "https://finance.yahoo.com/"

    async def _fetch_data(self, symbol: str, start_date: str, end_date: str) -> dict[str, Any]:
        """
        Fetch stock data from Yahoo Finance website.

        Args:
            symbol: Stock symbol
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format

        Returns:
            Raw response data

        Raises:
            APIError: If the request fails or returns invalid data
        """
        # Convert dates to timestamps
        start_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
        end_timestamp = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())

        # Validate date range
        if start_timestamp > end_timestamp:
            raise ValidationError(
                symbol,
                [
                    {
                        "error": "Invalid date range",
                        "details": f"Start date {start_date} is after end date {end_date}",
                    }
                ],
            )

        # Construct URL with parameters
        url = f"{self.base_url}/quote/{symbol}/history"
        params: dict[str, Any] = {}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status != HTTP_OK:
                        raise APIError(symbol, f"Request failed with status {response.status}")
                    return cast(dict[str, Any], await response.json())
        except aiohttp.ClientError as e:
            raise APIError(symbol, f"Network error: {e!s}") from e
        except Exception as e:
            raise APIError(symbol, f"Unexpected error during request: {e!s}") from e

    def _process_response(self, symbol: str, data: dict[str, Any]) -> pd.DataFrame:
        """
        Process raw API response into a DataFrame.

        Args:
            symbol: Stock symbol being processed
            data: Raw API response

        Returns:
            Processed stock data

        Raises:
            APIError: If the response data is invalid or cannot be processed
        """
        try:
            # Extract the historical data from the response
            history = data["prices"]

            # Convert to DataFrame
            df = pd.DataFrame(history)

            # Convert timestamp to datetime
            df["date"] = pd.to_datetime(df["date"], unit="s")
            df.set_index("date", inplace=True)

            # Rename columns to match our model
            df = df.rename(
                columns={
                    "open": "Open",
                    "high": "High",
                    "low": "Low",
                    "close": "Close",
                    "adjclose": "Adj Close",
                    "volume": "Volume",
                }
            )

            # Select and reorder columns
            df = df[["Open", "High", "Low", "Close", "Adj Close", "Volume"]]

            return df

        except (KeyError, IndexError) as e:
            raise APIError(symbol, f"Failed to process response: {e!s}") from e
        except Exception as e:
            raise APIError(symbol, f"Unexpected error processing data: {e!s}") from e

    async def get_historical_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str | None = None,
    ) -> None:
        """
        Retrieve historical stock data and store it in the database.

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format. Defaults to today.

        Raises:
            APIError: If there's an error retrieving or processing the data
            ValidationError: If the data fails validation
        """
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")

        try:
            # Fetch data from API
            raw_data = await self._fetch_data(symbol, start_date, end_date)
            data = self._process_response(symbol, raw_data)

            # Validate data
            errors = []
            if data.empty:
                errors.append(
                    {
                        "error": "Empty data",
                        "details": "No data returned for the specified date range",
                    }
                )
            if errors:
                raise ValidationError(symbol, errors)

            # Convert data to database models
            for date, row in data.iterrows():
                stock_data = StockData(
                    symbol=symbol,
                    date=date,
                    open=float(row["Open"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    close=float(row["Close"]),
                    adj_close=float(row["Adj Close"]),
                    volume=int(row["Volume"]),
                )
                self.session.add(stock_data)

            await self.session.commit()

        except (APIError, ValidationError):
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise APIError(symbol, f"Unexpected error: {e!s}") from e
