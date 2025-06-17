"""Constants for stock data tests."""

import os
from datetime import datetime

# Number of required columns in the stock data table
REQUIRED_COLUMNS_COUNT = 7

# Test data values
TEST_DATE = datetime(2025, 6, 13)  # Updated to match actual data
TEST_OPEN_PRICE = 199.73
TEST_HIGH_PRICE = 200.37
TEST_LOW_PRICE = 195.70
TEST_CLOSE_PRICE = 196.45
TEST_ADJ_CLOSE_PRICE = 196.45
TEST_VOLUME = 51447300  # Updated to match actual data

# Test data will be extracted from the actual HTML file
# These values will be updated based on the first row of data
TEST_RECORDS_COUNT = 1
TEST_UPDATED_OPEN_PRICE = 199.73

# Rate limiter test configuration
RATE_LIMITER_REQUESTS = 2  # Number of requests allowed per window
RATE_LIMITER_WINDOW = 1.0  # Time window in seconds
TIMING_TOLERANCE = 0.1  # Allow 100ms timing variation

# Test server configuration
TEST_SERVER_BASE_URL = "http://localhost:8000"  # FastAPI default port

TEST_STOCK_SYMBOL = "TST"

# Test fixture files
TEST_AAPL_FIXTURE = "AAPL_2025-06-16_20250616_185555.html"
TEST_FIXTURES_DIR = os.path.join("cream_api", "tests", "stock_data", "fixtures")
TEST_AAPL_FIXTURE_PATH = os.path.join(TEST_FIXTURES_DIR, TEST_AAPL_FIXTURE)
