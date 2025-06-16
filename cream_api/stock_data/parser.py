"""Stock data parser for extracting information from HTML content."""

from datetime import datetime
from typing import Any

import pandas as pd
from bs4 import BeautifulSoup

from cream_api.settings import get_app_settings
from cream_api.stock_data.exceptions import APIError
from cream_api.tests.stock_data.test_constants import REQUIRED_COLUMNS_COUNT

settings = get_app_settings()


class StockDataParser:
    """Parser for extracting stock data from HTML content."""

    def __init__(self) -> None:
        """Initialize parser with settings."""
        self.settings = settings
        self.required_columns = [
            "Date",
            "Open",
            "High",
            "Low",
            "Close",
            "Adj Close",
            "Volume",
        ]

    def parse_html(self, html_content: str) -> dict[str, list[dict[str, Any]]]:
        """
        Parse HTML content and extract stock data.

        Args:
            html_content: Raw HTML string to parse

        Returns:
            Dictionary containing parsed stock data

        Raises:
            APIError: If HTML content is invalid or missing required data
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            table = self._find_data_table(soup)
            if not table:
                raise APIError("AAPL", "No data table found in HTML content")

            data = self._extract_table_data(table)
            return {"prices": data}
        except Exception as e:
            raise APIError("AAPL", f"Failed to parse HTML: {e!s}") from e

    def process_data(self, data: dict[str, list[dict[str, Any]]]) -> pd.DataFrame:
        """
        Process raw data into a DataFrame.

        Args:
            data: Dictionary containing raw stock data

        Returns:
            DataFrame with processed stock data

        Raises:
            APIError: If data processing fails
        """
        try:
            df = pd.DataFrame(data["prices"])
            df = self._clean_data(df)
            df = self._validate_data(df)
            return df
        except Exception as e:
            raise APIError("AAPL", f"Failed to process data: {e!s}") from e

    def _find_data_table(self, soup: BeautifulSoup) -> Any | None:
        """
        Find the main data table in the HTML.

        Args:
            soup: BeautifulSoup object of parsed HTML

        Returns:
            BeautifulSoup table object or None if not found
        """
        return soup.find("table", {"data-test": "historical-prices"})

    def _extract_table_data(self, table: Any) -> list[dict[str, Any]]:
        """
        Extract data from table rows.

        Args:
            table: BeautifulSoup table object

        Returns:
            List of dictionaries containing row data
        """
        data: list[dict[str, Any]] = []
        rows = table.find_all("tr")[1:]  # Skip header row

        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= REQUIRED_COLUMNS_COUNT:  # Ensure we have all required columns
                try:
                    row_data = {
                        "date": self._parse_date(cols[0].text.strip()),
                        "open": self._parse_float(cols[1].text.strip()),
                        "high": self._parse_float(cols[2].text.strip()),
                        "low": self._parse_float(cols[3].text.strip()),
                        "close": self._parse_float(cols[4].text.strip()),
                        "adj_close": self._parse_float(cols[5].text.strip()),
                        "volume": self._parse_int(cols[6].text.strip()),
                    }
                    data.append(row_data)
                except (ValueError, IndexError) as e:
                    # Log error but continue processing other rows
                    print(f"Error parsing row: {e}")

        return data

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and normalize the data.

        Args:
            df: Raw DataFrame to clean

        Returns:
            Cleaned DataFrame
        """
        # Convert date column to datetime
        df["date"] = pd.to_datetime(df["date"])

        # Remove duplicates
        df = df.drop_duplicates(subset=["date"])

        # Sort by date
        df = df.sort_values("date")

        # Handle missing values
        df = self._handle_missing_values(df)

        return df

    def _validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate the processed data.

        Args:
            df: DataFrame to validate

        Returns:
            Validated DataFrame

        Raises:
            APIError: If validation fails
        """
        # Validate date range
        if df["date"].min() < datetime(1900, 1, 1):
            raise APIError("AAPL", "Data contains dates before 1900")

        if df["date"].max() > datetime.now():
            raise APIError("AAPL", "Data contains future dates")

        # Validate price relationships
        invalid_high = (
            (df["high"] < df["open"]) | (df["high"] < df["close"]) | (df["high"] < df["low"])
        )
        invalid_low = (
            (df["low"] > df["open"]) | (df["low"] > df["close"]) | (df["low"] > df["high"])
        )

        if invalid_high.any() or invalid_low.any():
            raise APIError("AAPL", "Invalid price relationships detected")

        # Validate volume
        if (df["volume"] < 0).any():
            raise APIError("AAPL", "Negative volume values detected")

        return df

    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values in the dataset.

        Args:
            df: DataFrame with potential missing values

        Returns:
            DataFrame with handled missing values
        """
        # Fill missing values for price columns with mean values
        price_cols = ["open", "high", "low", "close", "adj_close"]
        for col in price_cols:
            df[col] = df[col].fillna(df[col].mean())

        # Set volume to 0 for missing values
        df["volume"] = df["volume"].fillna(0)

        return df

    def _parse_date(self, date_str: str) -> datetime:
        """
        Parse date string to datetime object.

        Args:
            date_str: Date string in format "MMM DD, YYYY"

        Returns:
            Datetime object

        Raises:
            ValueError: If date string is invalid
        """
        try:
            return datetime.strptime(date_str, "%b %d, %Y")
        except Exception as e:
            raise ValueError(f"Invalid date format: {date_str}") from e

    def _parse_float(self, value: str) -> float:
        """
        Parse string to float.

        Args:
            value: String containing float value

        Returns:
            Float value

        Raises:
            ValueError: If value cannot be parsed as float
        """
        try:
            return float(value.replace(",", ""))
        except ValueError as e:
            raise ValueError(f"Invalid float value: {value}") from e

    def _parse_int(self, value: str) -> int:
        """
        Parse string to integer.

        Args:
            value: String containing integer value

        Returns:
            Integer value

        Raises:
            ValueError: If value cannot be parsed as integer
        """
        try:
            return int(value.replace(",", ""))
        except ValueError as e:
            raise ValueError(f"Invalid integer value: {value}") from e
