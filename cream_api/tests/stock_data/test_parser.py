"""Tests for stock data parser."""

from typing import TypedDict

import pytest

from cream_api.stock_data.exceptions import APIError
from cream_api.stock_data.parser import StockDataParser
from cream_api.tests.stock_data.test_constants import (
    TEST_ADJ_CLOSE_PRICE,
    TEST_CLOSE_PRICE,
    TEST_HIGH_PRICE,
    TEST_LOW_PRICE,
    TEST_OPEN_PRICE,
    TEST_VOLUME,
)


class PriceData(TypedDict):
    """Type definition for price data."""

    date: str
    open: float
    high: float
    low: float
    close: float
    adj_close: float
    volume: int


class ParsedData(TypedDict):
    """Type definition for parsed data."""

    prices: list[PriceData]


@pytest.fixture
def parser() -> StockDataParser:
    """Create parser instance."""
    return StockDataParser()


@pytest.fixture
def sample_html() -> str:
    """Create sample HTML content."""
    return """
    <table data-test="historical-prices">
        <tr>
            <th>Date</th>
            <th>Open</th>
            <th>High</th>
            <th>Low</th>
            <th>Close</th>
            <th>Adj Close</th>
            <th>Volume</th>
        </tr>
        <tr>
            <td>Jan 01, 2024</td>
            <td>150.00</td>
            <td>155.00</td>
            <td>148.00</td>
            <td>152.00</td>
            <td>152.00</td>
            <td>1000000</td>
        </tr>
    </table>
    """


def test_parse_html(parser: StockDataParser, sample_html: str) -> None:
    """Test HTML parsing functionality."""
    data = parser.parse_html(sample_html)
    assert isinstance(data, dict)
    assert "prices" in data
    assert isinstance(data["prices"], list)
    assert len(data["prices"]) > 0
    assert isinstance(data["prices"][0], dict)

    price_data = data["prices"][0]
    assert price_data["open"] == TEST_OPEN_PRICE
    assert price_data["high"] == TEST_HIGH_PRICE
    assert price_data["low"] == TEST_LOW_PRICE
    assert price_data["close"] == TEST_CLOSE_PRICE
    assert price_data["adj_close"] == TEST_ADJ_CLOSE_PRICE
    assert price_data["volume"] == TEST_VOLUME


def test_parse_invalid_html(parser: StockDataParser) -> None:
    """Test parsing invalid HTML."""
    with pytest.raises(APIError):
        parser.parse_html("<invalid>html</invalid>")


def test_process_data(parser: StockDataParser) -> None:
    """Test data processing functionality."""
    data = {
        "prices": [
            {
                "date": "Jan 01, 2024",
                "open": TEST_OPEN_PRICE,
                "high": TEST_HIGH_PRICE,
                "low": TEST_LOW_PRICE,
                "close": TEST_CLOSE_PRICE,
                "adj_close": TEST_ADJ_CLOSE_PRICE,
                "volume": TEST_VOLUME,
            }
        ]
    }
    df = parser.process_data(data)
    assert not df.empty
    assert len(df) == 1
    assert df["open"].iloc[0] == TEST_OPEN_PRICE
    assert df["high"].iloc[0] == TEST_HIGH_PRICE
    assert df["low"].iloc[0] == TEST_LOW_PRICE
    assert df["close"].iloc[0] == TEST_CLOSE_PRICE
    assert df["adj_close"].iloc[0] == TEST_ADJ_CLOSE_PRICE
    assert df["volume"].iloc[0] == TEST_VOLUME


def test_process_invalid_data(parser: StockDataParser) -> None:
    """Test processing invalid data."""
    with pytest.raises(APIError):
        parser.process_data({"prices": [{"invalid": "data"}]})
