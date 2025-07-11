"""Tests for the stock data parser."""

import pandas as pd
import pytest
from bs4 import BeautifulSoup

from cream_api.common.exceptions import StockRetrievalError
from cream_api.stock_data.config import StockDataConfig
from cream_api.stock_data.parser import StockDataParser
from cream_api.tests.stock_data.stock_data_test_constants import (
    REQUIRED_COLUMNS_COUNT,
    TEST_ADJ_CLOSE_PRICE,
    TEST_CLOSE_PRICE,
    TEST_DATE,
    TEST_FIXTURE_PATH,
    TEST_HIGH_PRICE,
    TEST_LOW_PRICE,
    TEST_OPEN_PRICE,
    TEST_VOLUME,
)


@pytest.fixture
def parser(test_config: StockDataConfig) -> StockDataParser:
    """Create a parser instance for testing."""
    return StockDataParser(config=test_config)


@pytest.fixture
def sample_html() -> str:
    """Load sample HTML content from file."""
    with open(TEST_FIXTURE_PATH) as f:
        return f.read()


def test_parse_html_valid_content(parser: StockDataParser, sample_html: str) -> None:
    """Test parsing valid HTML content."""
    result = parser.parse_html(sample_html)
    assert "prices" in result
    assert len(result["prices"]) > 0

    # Verify first row data
    first_row = result["prices"][0]
    assert first_row["date"] == TEST_DATE.strftime("%b %d, %Y")
    assert float(first_row["open"].replace(",", "")) == TEST_OPEN_PRICE
    assert float(first_row["high"].replace(",", "")) == TEST_HIGH_PRICE
    assert float(first_row["low"].replace(",", "")) == TEST_LOW_PRICE
    assert float(first_row["close"].replace(",", "")) == TEST_CLOSE_PRICE
    assert float(first_row["adj_close"].replace(",", "")) == TEST_ADJ_CLOSE_PRICE
    assert int(first_row["volume"].replace(",", "")) == TEST_VOLUME


def test_parse_html_table_headers(parser: StockDataParser, sample_html: str) -> None:
    """Test that the HTML table has the correct headers."""
    soup = BeautifulSoup(sample_html, "html.parser")
    table = parser._find_data_table(soup)
    assert table is not None

    # Extract headers
    headers = [th.get_text(strip=True) for th in table.find_all("th")]
    assert len(headers) == REQUIRED_COLUMNS_COUNT

    # Clean headers the same way as the parser
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

    # Check if headers can be mapped to required columns
    assert all(header in parser._column_mapping for header in cleaned_headers)


def test_parse_html_invalid_content(parser: StockDataParser) -> None:
    """Test parsing invalid HTML content."""
    with pytest.raises(StockRetrievalError):
        parser.parse_html("invalid html")


def test_parse_html_missing_table(parser: StockDataParser) -> None:
    """Test parsing HTML with missing data table."""
    html = "<html><body><div>No table here</div></body></html>"
    with pytest.raises(StockRetrievalError):
        parser.parse_html(html)


def test_parse_html_file_valid(parser: StockDataParser) -> None:
    """Test parsing valid HTML file."""
    result = parser.parse_html_file(TEST_FIXTURE_PATH)
    assert "prices" in result
    assert len(result["prices"]) > 0


def test_parse_html_file_not_found(parser: StockDataParser) -> None:
    """Test parsing non-existent HTML file."""
    with pytest.raises(StockRetrievalError):
        parser.parse_html_file("nonexistent.html")


def test_process_data_valid(parser: StockDataParser, sample_html: str) -> None:
    """Test processing valid data."""
    parsed_data = parser.parse_html(sample_html)
    df = parser.process_data(parsed_data)
    assert not df.empty
    assert len(df.columns) == REQUIRED_COLUMNS_COUNT
    assert all(col in df.columns for col in ["date", "open", "high", "low", "close", "adj_close", "volume"])


def test_process_data_invalid(parser: StockDataParser) -> None:
    """Test processing invalid data."""
    with pytest.raises(StockRetrievalError):
        parser.process_data({"prices": []})


def test_find_data_table_valid(parser: StockDataParser, sample_html: str) -> None:
    """Test finding data table in valid HTML."""
    soup = BeautifulSoup(sample_html, "html.parser")
    table = parser._find_data_table(soup)
    assert table is not None


def test_find_data_table_invalid(parser: StockDataParser) -> None:
    """Test finding data table in invalid HTML."""
    soup = BeautifulSoup("<html><body></body></html>", "html.parser")
    table = parser._find_data_table(soup)
    assert table is None


def test_extract_table_data_valid(parser: StockDataParser, sample_html: str) -> None:
    """Test extracting data from valid table."""
    soup = BeautifulSoup(sample_html, "html.parser")
    table = parser._find_data_table(soup)
    assert table is not None

    data = parser._extract_table_data(table)
    assert len(data) > 0
    assert all(isinstance(row, dict) for row in data)


def test_extract_table_data_invalid(parser: StockDataParser) -> None:
    """Test extracting data from invalid table."""
    soup = BeautifulSoup("<table><tr><td>Invalid</td></tr></table>", "html.parser")
    with pytest.raises(StockRetrievalError):
        parser._extract_table_data(soup.table)


def test_validate_headers_valid(parser: StockDataParser) -> None:
    """Test validating valid headers."""
    headers = ["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"]
    assert parser._validate_headers(headers)


def test_validate_headers_invalid(parser: StockDataParser) -> None:
    """Test validating invalid headers."""
    headers = ["Invalid", "Headers"]
    assert not parser._validate_headers(headers)


def test_clean_data_valid(parser: StockDataParser, sample_html: str) -> None:
    """Test cleaning valid data."""
    parsed_data = parser.parse_html(sample_html)
    df = pd.DataFrame(parsed_data["prices"])
    cleaned_df = parser._clean_data(df)
    assert not cleaned_df.empty
    assert all(col in cleaned_df.columns for col in ["date", "open", "high", "low", "close", "adj_close", "volume"])
    assert cleaned_df["date"].dtype == "datetime64[ns]"
    assert all(
        cleaned_df[col].dtype in ["float64", "int64"] for col in ["open", "high", "low", "close", "adj_close", "volume"]
    )


def test_clean_data_invalid(parser: StockDataParser) -> None:
    """Test cleaning invalid data."""
    df = pd.DataFrame({"Date": ["invalid"], "Open": ["not a number"]})
    with pytest.raises(StockRetrievalError):
        parser._clean_data(df)


def test_validate_data_valid(parser: StockDataParser, sample_html: str) -> None:
    """Test validating valid data."""
    parsed_data = parser.parse_html(sample_html)
    df = pd.DataFrame(parsed_data["prices"])
    df = parser._clean_data(df)
    validated_df = parser._validate_data(df)
    assert not validated_df.empty


def test_validate_data_invalid_prices(parser: StockDataParser) -> None:
    """Test validating data with invalid prices."""
    df = pd.DataFrame(
        {
            "date": ["2024-01-01"],
            "open": [100.0],
            "high": [90.0],  # High price lower than open
            "low": [110.0],  # Low price higher than open
            "close": [100.5],
            "adj_close": [100.5],
            "volume": [1000000],
        }
    )
    df["date"] = pd.to_datetime(df["date"])
    with pytest.raises(StockRetrievalError):
        parser._validate_data(df)
