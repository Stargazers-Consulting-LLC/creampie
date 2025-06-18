"""Constants for stock data tests.

This module contains test-specific constants used across stock data tests,
including test directories, sample data, and other test configuration.
"""

import os
from datetime import datetime

# Test data constants
TEST_SYMBOL = "TEST"
TEST_DATE = datetime.strptime("2025-06-13", "%Y-%m-%d")  # Match fixture data
TEST_RECORDS_COUNT = 1  # Number of records in test data

# Price data
TEST_OPEN_PRICE = 199.73
TEST_HIGH_PRICE = 200.37
TEST_LOW_PRICE = 195.70
TEST_CLOSE_PRICE = 196.45
TEST_ADJ_CLOSE_PRICE = 196.45
TEST_VOLUME = 51_447_300

# Test data dictionary
TEST_STOCK_DATA = {
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

# HTML content
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
TEST_HTML_FILENAME = f"{TEST_SYMBOL}_{TEST_DATE.strftime('%Y-%m-%d')}.html"

# Fixture configuration
TEST_FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
TEST_FIXTURE = f"{TEST_SYMBOL}_{TEST_DATE.strftime('%Y-%m-%d')}.html"
TEST_FIXTURE_PATH = os.path.join(TEST_FIXTURES_DIR, TEST_FIXTURE)

# Server configuration
TEST_HOST = "localhost"
TEST_PORT = 8000
TEST_BASE_URL = f"http://{TEST_HOST}:{TEST_PORT}"
TEST_SERVER_BASE_URL = TEST_BASE_URL  # Alias for backward compatibility

# Rate limiter configuration
RATE_LIMITER_REQUESTS = 2  # Number of requests allowed per window
RATE_LIMITER_WINDOW = 1.0  # Time window in seconds
TIMING_TOLERANCE = 0.1  # Allow 100ms timing variation

# Data validation constants
REQUIRED_COLUMNS_COUNT = 7
