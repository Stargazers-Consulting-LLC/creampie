"""Stock data parser for extracting information from HTML content."""

import logging
from typing import Any

import pandas as pd
from bs4 import BeautifulSoup

from cream_api.common.exceptions import StockRetrievalError
from cream_api.stock_data.config import StockDataConfig, get_stock_data_config
from cream_api.tests.stock_data.test_constants import REQUIRED_COLUMNS_COUNT

# Required columns for data validation
REQUIRED_COLUMNS: list[str] = [
    "Date",
    "Open",
    "High",
    "Low",
    "Close",
    "Adj Close",
    "Volume",
]

# Column name mapping from HTML headers to DataFrame columns
COLUMN_MAPPING: dict[str, str] = {
    "Date": "date",
    "Open": "open",
    "High": "high",
    "Low": "low",
    "Close": "close",
    "Adj Close": "adj_close",
    "Volume": "volume",
}

logger = logging.getLogger(__name__)


class StockDataParser:
    """Parser for extracting stock data from HTML content."""

    # Selectors for the historical prices table
    HISTORICAL_PRICES_CSS_SELECTOR = ".table"

    def __init__(self, config: StockDataConfig | None = None) -> None:
        """Initialize parser.

        Args:
            config: StockDataConfig instance (defaults to default config)
        """
        self.config = config or get_stock_data_config()
        self._required_columns: set[str] = set(REQUIRED_COLUMNS)
        self._column_mapping: dict[str, str] = COLUMN_MAPPING

    def parse_html(self, html_content: str) -> dict[str, list[dict[str, Any]]]:
        """
        Parse HTML content and extract stock data.

        Args:
            html_content: Raw HTML string to parse

        Returns:
            Dictionary containing parsed stock data

        Raises:
            StockRetrievalError: If HTML content is invalid or missing required data
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            table = self._find_data_table(soup)
            if not table:
                raise StockRetrievalError("No data table found in HTML content")

            data = self._extract_table_data(table)
            return {"prices": data}
        except Exception as e:
            raise StockRetrievalError(f"Failed to parse HTML: {e!s}") from e

    def parse_html_file(self, file_path: str) -> dict[str, list[dict[str, Any]]]:
        """Parse stock data from an HTML file.

        Args:
            file_path: Path to the HTML file.

        Returns:
            Dictionary containing the parsed data.

        Raises:
            StockRetrievalError: If the file cannot be read or parsed.
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                html_content = f.read()
            return self.parse_html(html_content)
        except FileNotFoundError as err:
            raise StockRetrievalError(f"HTML file not found: {file_path}") from err
        except Exception as e:
            raise StockRetrievalError(f"Failed to read HTML file: {e!s}") from e

    def process_data(self, data: dict[str, list[dict[str, Any]]]) -> pd.DataFrame:
        """
        Process raw data into a DataFrame.

        Args:
            data: Dictionary containing raw stock data

        Returns:
            DataFrame with processed stock data

        Raises:
            StockRetrievalError: If data processing fails
        """
        try:
            df = pd.DataFrame(data["prices"])
            df = self._clean_data(df)
            df = self._validate_data(df)
            return df
        except Exception as e:
            raise StockRetrievalError(f"Failed to process data: {e!s}") from e

    def _find_data_table(self, soup: BeautifulSoup) -> Any | None:
        """
        Find the main data table in the HTML.

        Args:
            soup: BeautifulSoup object of parsed HTML

        Returns:
            BeautifulSoup table object or None if not found
        """
        return soup.select_one(self.HISTORICAL_PRICES_CSS_SELECTOR)

    def _extract_table_data(self, table: Any) -> list[dict[str, Any]]:
        """
        Extract data from the table.

        Args:
            table: BeautifulSoup table object

        Returns:
            List of dictionaries containing row data

        Raises:
            StockRetrievalError: If table structure is invalid
        """
        try:
            # Extract and clean headers from thead
            thead = table.find("thead")
            if not thead:
                raise StockRetrievalError("No thead found in table")

            headers = [th.get_text(strip=True) for th in thead.find_all("th")]
            if not headers:
                raise StockRetrievalError("No headers found in table")

            cleaned_headers = []
            for header_text in headers:
                # Remove special characters and normalize spaces
                clean_header = header_text.replace("*", "").replace(".", "")
                # Split on any whitespace and take first part
                base_header = clean_header.split()[0]
                # Handle special cases
                if base_header == "CloseClose":
                    base_header = "Close"
                elif base_header == "Adj":
                    base_header = "Adj Close"
                cleaned_headers.append(base_header)

            if not self._validate_headers(cleaned_headers):
                raise StockRetrievalError(
                    f"Invalid table headers. Expected {self._required_columns}, got {cleaned_headers}",
                )

            # Extract rows from tbody
            tbody = table.find("tbody")
            if not tbody:
                raise StockRetrievalError("No tbody found in table")

            rows = []
            for tr in tbody.find_all("tr"):
                row_data = {}
                for td, header in zip(tr.find_all("td"), cleaned_headers, strict=False):
                    # Get just the immediate text content, stripped of whitespace
                    value = td.get_text(strip=True)
                    # Map headers to DataFrame column names using the mapping dictionary
                    df_column = self._column_mapping.get(header)
                    if df_column is None:
                        raise StockRetrievalError(f"Unknown header: {header}")
                    # Store with lowercase column names for consistency
                    row_data[df_column] = value
                rows.append(row_data)

            # Sort rows by date in descending order (newest first)
            rows.sort(key=lambda x: pd.to_datetime(x["date"]), reverse=True)

            return rows
        except Exception as e:
            raise StockRetrievalError(f"Failed to extract table data: {e!s}") from e

    def _validate_headers(self, headers: list[str]) -> bool:
        """
        Validate table headers against required columns.

        Args:
            headers: List of header strings

        Returns:
            True if headers match required columns, False otherwise
        """
        # Check if all headers can be mapped to required columns
        mapped_headers = set()
        for header in headers:
            if header in self._column_mapping:
                mapped_headers.add(self._column_mapping[header])
            else:
                # Try to find a mapping by removing any description
                base_header = header.split(None, 1)[0].strip()
                if base_header in self._column_mapping:
                    mapped_headers.add(self._column_mapping[base_header])

        # Check if we have all required columns
        required_columns = {"date", "open", "high", "low", "close", "adj_close", "volume"}
        return len(headers) == REQUIRED_COLUMNS_COUNT and mapped_headers == required_columns

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and normalize the data.

        Args:
            df: DataFrame to clean

        Returns:
            Cleaned DataFrame

        Raises:
            StockRetrievalError: If data cleaning fails
        """
        try:
            # Ensure column names are lowercase
            df.columns = df.columns.str.lower()

            # Convert date column to datetime
            df["date"] = pd.to_datetime(df["date"])

            # Filter out dividend rows before processing
            # Dividend rows typically have text in numeric columns
            numeric_cols = ["open", "high", "low", "close", "adj_close", "volume"]
            for col in numeric_cols:
                if col not in df.columns:
                    raise StockRetrievalError(f"Missing required column: {col}")
                # Keep only rows where the value is purely numeric (after removing commas)
                df = df[df[col].str.replace(",", "").str.match(r"^\d*\.?\d+$")]

            # Convert numeric columns
            for col in numeric_cols:
                df[col] = df[col].str.replace(",", "")
                df[col] = pd.to_numeric(df[col], errors="raise")

            # Remove duplicates
            df = df.drop_duplicates(subset=["date"])

            # Sort by date
            df = df.sort_values("date")

            # Handle missing values
            df = self._handle_missing_values(df)

            # Print first few rows for debugging
            print("\nFirst few rows after cleaning:")
            print(df[["date", "open", "high", "low", "close"]].head().to_string())

            return df
        except Exception as e:
            raise StockRetrievalError(f"Failed to clean data: {e!s}") from e

    def _validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate the processed data.

        Args:
            df: DataFrame to validate

        Returns:
            Validated DataFrame

        Raises:
            StockRetrievalError: If data validation fails
        """
        try:
            # Check for required columns
            required_cols = ["date", "open", "high", "low", "close", "adj_close", "volume"]
            if not all(col in df.columns for col in required_cols):
                raise StockRetrievalError("Missing required columns")

            # Check for valid date range
            min_date = pd.Timestamp("1900-01-01")
            max_date = pd.Timestamp.now()
            if not df["date"].between(min_date, max_date).all():
                raise StockRetrievalError("Invalid date range")

            # Check for valid price ranges
            price_cols = ["open", "high", "low", "close", "adj_close"]
            for col in price_cols:
                if not df[col].between(0, float("inf")).all():
                    raise StockRetrievalError(f"Invalid {col} price range")

            # Check for valid volume
            if not df["volume"].between(0, float("inf")).all():
                raise StockRetrievalError("Invalid volume range")

            # Check price relationships with tolerance for floating point errors
            tolerance = 1e-10
            invalid_rows = df[
                (df["high"] < df["low"] - tolerance)
                | (df["high"] < df["open"] - tolerance)
                | (df["high"] < df["close"] - tolerance)
                | (df["low"] > df["open"] + tolerance)
                | (df["low"] > df["close"] + tolerance)
            ]

            if not invalid_rows.empty:
                # Log the problematic rows for debugging
                print("\nInvalid price relationships found:")
                print(invalid_rows[["date", "open", "high", "low", "close"]].to_string())
                raise StockRetrievalError("Invalid price relationships detected")

            return df
        except Exception as e:
            raise StockRetrievalError(f"Failed to validate data: {e!s}") from e

    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values in the data.

        Args:
            df: DataFrame to process

        Returns:
            DataFrame with missing values handled
        """
        # Fill missing volume with 0
        df["volume"] = df["volume"].fillna(0)

        # Fill missing prices with mean values
        price_cols = ["open", "high", "low", "close", "adj_close"]
        for col in price_cols:
            df[col] = df[col].fillna(df[col].mean())

        return df
