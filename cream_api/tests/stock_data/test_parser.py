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


class ParsedData(TypedDict, total=False):
    """Type definition for parsed data."""

    prices: list[PriceData]


@pytest.fixture
def sample_html() -> str:
    """Get sample HTML for testing."""
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
            <td>100.00</td>
            <td>101.00</td>
            <td>99.00</td>
            <td>100.50</td>
            <td>100.50</td>
            <td>1,000,000</td>
        </tr>
    </table>
    """


@pytest.fixture
def parser() -> StockDataParser:
    """Create a parser instance."""
    return StockDataParser()


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
    raw_data = {
        "prices": [
            {
                "date": 1704067200,  # 2024-01-01
                "open": 100.00,
                "high": 101.00,
                "low": 99.00,
                "close": 100.50,
                "adjclose": 100.50,
                "volume": 1000000,
            }
        ]
    }

    df = parser.process_data(raw_data)
    assert not df.empty
    assert list(df.columns) == ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
    assert df.iloc[0]["Open"] == TEST_OPEN_PRICE
    assert df.iloc[0]["High"] == TEST_HIGH_PRICE
    assert df.iloc[0]["Low"] == TEST_LOW_PRICE
    assert df.iloc[0]["Close"] == TEST_CLOSE_PRICE
    assert df.iloc[0]["Adj Close"] == TEST_ADJ_CLOSE_PRICE
    assert df.iloc[0]["Volume"] == TEST_VOLUME


def test_process_invalid_data(parser: StockDataParser) -> None:
    """Test processing invalid data."""
    with pytest.raises(APIError):
        parser.process_data({"prices": [{"invalid": "data"}]})
