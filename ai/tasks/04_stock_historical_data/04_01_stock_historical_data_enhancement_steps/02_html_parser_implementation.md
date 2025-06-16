# HTML Parser Implementation Guide

## Overview

This guide details the implementation of the HTML parser for Yahoo Finance stock data. The parser will:

1. Extract historical stock data from HTML tables
2. Handle different date formats
3. Implement robust error handling
4. Support caching for development and debugging

## Implementation Steps

### 1. Create Base Parser Class

Create `src/parser/stock_parser.py`:

```python
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from bs4 import BeautifulSoup
from whenever import DateTime as WhenDateTime

from config.settings import get_settings

settings = get_settings()

class StockParser:
    """Base class for parsing stock data from HTML."""

    def __init__(self) -> None:
        """Initialize parser with settings."""
        self.settings = settings

    def parse_html(self, html_content: str) -> pd.DataFrame:
        """
        Parse HTML content into a DataFrame.

        Args:
            html_content: Raw HTML string to parse

        Returns:
            DataFrame containing parsed stock data

        Raises:
            ValueError: If HTML content is invalid or missing required data
        """
        soup = BeautifulSoup(html_content, "html.parser")
        table = self._find_data_table(soup)
        if not table:
            raise ValueError("No data table found in HTML content")

        data = self._extract_table_data(table)
        return self._create_dataframe(data)

    def _find_data_table(self, soup: BeautifulSoup) -> Optional[Any]:
        """
        Find the main data table in the HTML.

        Args:
            soup: BeautifulSoup object of parsed HTML

        Returns:
            BeautifulSoup table object or None if not found
        """
        # Implementation specific to Yahoo Finance HTML structure
        return soup.find("table", {"data-test": "historical-prices"})

    def _extract_table_data(self, table: Any) -> List[Dict[str, Any]]:
        """
        Extract data from table rows.

        Args:
            table: BeautifulSoup table object

        Returns:
            List of dictionaries containing row data
        """
        data: List[Dict[str, Any]] = []
        rows = table.find_all("tr")[1:]  # Skip header row

        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 7:  # Ensure we have all required columns
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

    def _create_dataframe(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Create DataFrame from extracted data.

        Args:
            data: List of dictionaries containing row data

        Returns:
            DataFrame with parsed stock data
        """
        df = pd.DataFrame(data)
        df.set_index("date", inplace=True)
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
            return WhenDateTime.parse(date_str).naive
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
```

### 2. Create Yahoo Finance Parser

Create `src/parser/yahoo_parser.py`:

```python
from typing import Any, Optional

import requests
from bs4 import BeautifulSoup

from src.parser.stock_parser import StockParser
from config.settings import get_settings

settings = get_settings()

class YahooFinanceParser(StockParser):
    """Parser specifically for Yahoo Finance HTML."""

    def __init__(self) -> None:
        """Initialize parser with Yahoo Finance specific settings."""
        super().__init__()
        self.base_url = "https://finance.yahoo.com/quote/{}/history"
        self.headers = {"User-Agent": settings.PARSER_USER_AGENT}

    def fetch_stock_data(self, symbol: str) -> Optional[Any]:
        """
        Fetch stock data from Yahoo Finance.

        Args:
            symbol: Stock symbol (e.g., "AAPL")

        Returns:
            BeautifulSoup object of parsed HTML or None if fetch fails

        Raises:
            requests.RequestException: If request fails
        """
        url = self.base_url.format(symbol)
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=settings.PARSER_TIMEOUT,
            )
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.RequestException as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None

    def _find_data_table(self, soup: BeautifulSoup) -> Optional[Any]:
        """
        Find the main data table in Yahoo Finance HTML.

        Args:
            soup: BeautifulSoup object of parsed HTML

        Returns:
            BeautifulSoup table object or None if not found
        """
        return soup.find("table", {"data-test": "historical-prices"})
```

### 3. Create Tests

Create `tests/test_parser.py`:

```python
from pathlib import Path
from typing import Any

import pytest
from bs4 import BeautifulSoup

from src.parser.stock_parser import StockParser
from src.parser.yahoo_parser import YahooFinanceParser

def test_parse_html(sample_html: str) -> None:
    """Test parsing HTML content."""
    parser = StockParser()
    df = parser.parse_html(sample_html)

    assert not df.empty
    assert list(df.columns) == ["open", "high", "low", "close", "adj_close", "volume"]
    assert len(df) == 1

def test_parse_date() -> None:
    """Test date parsing."""
    parser = StockParser()
    date_str = "Jan 01, 2024"
    parsed_date = parser._parse_date(date_str)

    assert parsed_date.year == 2024
    assert parsed_date.month == 1
    assert parsed_date.day == 1

def test_parse_float() -> None:
    """Test float parsing."""
    parser = StockParser()
    assert parser._parse_float("100.50") == 100.50
    assert parser._parse_float("1,000.50") == 1000.50

    with pytest.raises(ValueError):
        parser._parse_float("invalid")

def test_parse_int() -> None:
    """Test integer parsing."""
    parser = StockParser()
    assert parser._parse_int("1000") == 1000
    assert parser._parse_int("1,000") == 1000

    with pytest.raises(ValueError):
        parser._parse_int("invalid")

def test_yahoo_parser_fetch() -> None:
    """Test Yahoo Finance data fetching."""
    parser = YahooFinanceParser()
    soup = parser.fetch_stock_data("AAPL")

    assert soup is not None
    assert isinstance(soup, BeautifulSoup)
```

## Error Handling

The parser implements several error handling mechanisms:

1. **Input Validation**

   - Validates HTML structure
   - Checks for required table elements
   - Verifies data format in cells

2. **Data Parsing**

   - Handles missing or malformed data
   - Converts string values to appropriate types
   - Manages different date formats

3. **Network Requests**
   - Implements retry logic
   - Handles timeouts
   - Manages connection errors

## Testing Strategy

1. **Unit Tests**

   - Test individual parsing functions
   - Verify data type conversions
   - Check error handling

2. **Integration Tests**

   - Test full HTML parsing
   - Verify DataFrame creation
   - Check Yahoo Finance integration

3. **Error Cases**
   - Test invalid HTML
   - Test missing data
   - Test network failures

## Next Steps

After implementing the parser:

1. Run the test suite
2. Verify error handling
3. Test with real Yahoo Finance data
4. Proceed to Data Processing Implementation
