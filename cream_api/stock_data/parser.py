"""Stock data parser for extracting information from HTML content."""

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

# Constants for data filtering
DIVIDEND_ROW_FIELD_COUNT = 2
REQUIRED_FIELDS = {"date", "open", "high", "low", "close", "adj_close", "volume"}

# Column groups for processing
NUMERIC_COLUMNS = ["open", "high", "low", "close", "adj_close", "volume"]

# Dividend detection patterns
DIVIDEND_INDICATORS = {"dividend", "div", "distribution"}
STOCK_SPLIT_INDICATORS = {"split", "splits", "stock split"}

# Data validation constants
NUMERIC_TOLERANCE = 1e-10


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
        table = soup.select_one(self.HISTORICAL_PRICES_CSS_SELECTOR)
        return table

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
            headers = self._extract_headers(table)
            cleaned_headers = self._clean_headers(headers)
            rows = self._extract_rows(table, cleaned_headers)
            rows.sort(key=lambda row: pd.to_datetime(row["date"]), reverse=True)
            return rows
        except Exception as e:
            raise StockRetrievalError(f"Failed to extract table data: {e!s}") from e

    def _extract_headers(self, table: Any) -> list[str]:
        """Extract raw headers from the table.

        Args:
            table: BeautifulSoup table object

        Returns:
            List of raw header names

        Raises:
            StockRetrievalError: If headers cannot be extracted
        """
        thead = table.find("thead")
        if not thead:
            raise StockRetrievalError("No thead found in table")

        headers = [th.get_text(strip=True) for th in thead.find_all("th")]
        if not headers:
            raise StockRetrievalError("No headers found in table")

        return headers

    def _clean_headers(self, headers: list[str]) -> list[str]:
        """Clean and normalize header names.

        Args:
            headers: List of raw header names

        Returns:
            List of cleaned header names
        """
        cleaned_headers = []
        for header_text in headers:
            clean_header = header_text.replace("*", "").replace(".", "")
            base_header = clean_header.split()[0]
            if base_header == "CloseClose":
                base_header = "Close"
            elif base_header == "Adj":
                base_header = "Adj Close"
            cleaned_headers.append(base_header)

        return cleaned_headers

    def _extract_rows(self, table: Any, cleaned_headers: list[str]) -> list[dict[str, Any]]:
        """Extract and filter rows from the table.

        Args:
            table: BeautifulSoup table object
            cleaned_headers: List of cleaned header names

        Returns:
            List of filtered row data dictionaries
        """
        tbody = table.find("tbody")
        if not tbody:
            raise StockRetrievalError("No tbody found in table")

        rows = list(
            filter(
                self._is_valid_row, map(lambda tr: self._extract_row_data(tr, cleaned_headers), tbody.find_all("tr"))
            )
        )

        return rows

    def _extract_row_data(self, tr: Any, cleaned_headers: list[str]) -> dict[str, Any]:
        """Extract data from a single table row.

        Args:
            tr: BeautifulSoup tr object
            cleaned_headers: List of cleaned header names

        Returns:
            Dictionary containing row data
        """
        row_data = {}
        for td, header in zip(tr.find_all("td"), cleaned_headers, strict=False):
            value = td.get_text(strip=True)
            df_column = self._column_mapping.get(header)
            if df_column is None:
                raise StockRetrievalError(f"Unknown header: {header}")
            row_data[df_column] = value
        return row_data

    def _is_valid_row(self, row_data: dict[str, Any]) -> bool:
        """Check if a row contains valid data.

        Args:
            row_data: Dictionary containing row data

        Returns:
            True if row is valid, False otherwise
        """
        if self._is_dividend_or_split_row(row_data):
            return False

        if not REQUIRED_FIELDS.issubset(set(row_data.keys())):
            return False

        if not self._has_valid_volume(row_data):
            return False

        return True

    def _is_dividend_or_split_row(self, row_data: dict[str, Any]) -> bool:
        """Check if a row represents dividend or stock split data.

        Args:
            row_data: Dictionary containing row data

        Returns:
            True if row is dividend/split data, False otherwise
        """
        if len(row_data) == DIVIDEND_ROW_FIELD_COUNT and "date" in row_data and "open" in row_data:
            open_value = row_data["open"].lower()

            if any(indicator in open_value for indicator in DIVIDEND_INDICATORS):
                return True

            if any(indicator in open_value for indicator in STOCK_SPLIT_INDICATORS):
                return True

        if len(row_data) < len(REQUIRED_FIELDS):
            return True

        return False

    def _has_valid_volume(self, row_data: dict[str, Any]) -> bool:
        """Check if a row has valid volume data.

        Args:
            row_data: Dictionary containing row data

        Returns:
            True if volume is valid, False otherwise
        """
        try:
            volume_str = row_data["volume"].replace(",", "")
            volume_val = float(volume_str)
            return volume_val > 0
        except (ValueError, AttributeError, KeyError):
            return False

    def _validate_headers(self, headers: list[str]) -> bool:
        """
        Validate table headers against required columns.

        Args:
            headers: List of header strings

        Returns:
            True if headers match required columns, False otherwise
        """
        mapped_headers = set()
        for header in headers:
            if header in self._column_mapping:
                mapped_headers.add(self._column_mapping[header])
            else:
                base_header = header.split(None, 1)[0].strip()
                if base_header in self._column_mapping:
                    mapped_headers.add(self._column_mapping[base_header])

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
            df.columns = df.columns.str.lower()

            df["date"] = pd.to_datetime(df["date"])

            missing_cols = [col for col in NUMERIC_COLUMNS if col not in df.columns]
            if missing_cols:
                raise StockRetrievalError(f"Missing required columns: {missing_cols}")

            # Convert numeric columns with error handling
            for col in NUMERIC_COLUMNS:
                # Remove commas from numeric strings before conversion
                df[col] = df[col].astype(str).str.replace(",", "")
                df[col] = pd.to_numeric(df[col], errors="coerce")

            # Filter out rows with invalid numeric data (NaN values)
            df = df.dropna(subset=NUMERIC_COLUMNS)

            df = df.drop_duplicates(subset=["date"])
            df = df.sort_values("date")
            df[NUMERIC_COLUMNS] = df[NUMERIC_COLUMNS].fillna(df[NUMERIC_COLUMNS].mean())

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
        invalid_rows = df[
            (df["high"] < df["low"] - NUMERIC_TOLERANCE)
            | (df["high"] < df["open"] - NUMERIC_TOLERANCE)
            | (df["high"] < df["close"] - NUMERIC_TOLERANCE)
            | (df["low"] > df["open"] + NUMERIC_TOLERANCE)
            | (df["low"] > df["close"] + NUMERIC_TOLERANCE)
        ]

        if not invalid_rows.empty:
            raise StockRetrievalError("Invalid price relationships detected")

        return df
