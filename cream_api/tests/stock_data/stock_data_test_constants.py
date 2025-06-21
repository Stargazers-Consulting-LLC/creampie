"""Constants for stock data tests.

This module contains test-specific constants used across stock data tests,
including test directories, sample data, and other test configuration.

References:
    - [Pytest Documentation](https://docs.pytest.org/)
    - [Python Type Hints](https://docs.python.org/3/library/typing.html)

### Legal
SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

import os
from datetime import datetime

# Core test data constants
DEFAULT_TEST_SYMBOL = "AAPL"
TEST_DATE = datetime.strptime("2025-06-16", "%Y-%m-%d")
TEST_RECORDS_COUNT = 1

# Price data constants
TEST_OPEN_PRICE = 197.30
TEST_HIGH_PRICE = 198.69
TEST_LOW_PRICE = 196.56
TEST_CLOSE_PRICE = 198.42
TEST_ADJ_CLOSE_PRICE = 198.42
TEST_VOLUME = 43_020_700

# Stock symbol mappings
TEST_STOCK_SYMBOLS: dict[str, str] = {
    "AAPL": "Apple Inc.",
    "TSLA": "Tesla Inc.",
    "GOOGL": "Alphabet Inc.",
    "MSFT": "Microsoft Corporation",
}

# Test data structures
TEST_STOCK_DATA: dict[str, list[dict[str, str]]] = {
    "prices": [
        {
            "date": TEST_DATE.strftime("%Y-%m-%d"),
            "open": str(TEST_OPEN_PRICE),
            "high": str(TEST_HIGH_PRICE),
            "low": str(TEST_LOW_PRICE),
            "close": str(TEST_CLOSE_PRICE),
            "adj_close": str(TEST_ADJ_CLOSE_PRICE),
            "volume": str(TEST_VOLUME),
        }
    ]
}

# HTML test content
TEST_HTML_CONTENT = f"""<table>
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
    <td>{TEST_DATE.strftime("%b %d, %Y")}</td>
    <td>{TEST_OPEN_PRICE:,.2f}</td>
    <td>{TEST_HIGH_PRICE:,.2f}</td>
    <td>{TEST_LOW_PRICE:,.2f}</td>
    <td>{TEST_CLOSE_PRICE:,.2f}</td>
    <td>{TEST_ADJ_CLOSE_PRICE:,.2f}</td>
    <td>{TEST_VOLUME:,}</td>
</tr>
</table>"""

# Directory and file configuration
TEST_RAW_RESPONSES_DIR = "test_raw_responses"
TEST_PARSED_RESPONSES_DIR = "test_parsed_responses"
TEST_DEADLETTER_RESPONSES_DIR = "test_deadletter_responses"
TEST_HTML_FILENAME = f"{DEFAULT_TEST_SYMBOL}_{TEST_DATE.strftime('%Y-%m-%d')}.html"

# Fixture configuration
TEST_FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
TEST_FIXTURE = f"{DEFAULT_TEST_SYMBOL}_{TEST_DATE.strftime('%Y-%m-%d')}.html"
TEST_FIXTURE_PATH = os.path.join(TEST_FIXTURES_DIR, TEST_FIXTURE)

# Server configuration
TEST_HOST = "localhost"
TEST_PORT = 8000
TEST_BASE_URL = f"http://{TEST_HOST}:{TEST_PORT}"
TEST_SERVER_BASE_URL = TEST_BASE_URL

# Rate limiter configuration
RATE_LIMITER_REQUESTS = 2
RATE_LIMITER_WINDOW = 1.0
TIMING_TOLERANCE = 0.1

# Validation constants
REQUIRED_COLUMNS_COUNT = 7

# Pagination constants
DEFAULT_PAGE_SIZE = 10

# Expected values for assertions
EXPECTED_THREE_STOCKS = 3
