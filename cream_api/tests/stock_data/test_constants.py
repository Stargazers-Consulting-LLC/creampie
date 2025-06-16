"""Constants for stock data tests."""

# Test data values
TEST_OPEN_PRICE = 150.00
TEST_HIGH_PRICE = 155.00
TEST_LOW_PRICE = 148.00
TEST_CLOSE_PRICE = 152.00
TEST_ADJ_CLOSE_PRICE = 152.00
TEST_VOLUME = 1000000
TEST_RECORDS_COUNT = 1
TEST_UPDATED_OPEN_PRICE = 151.00

# Table column count
REQUIRED_COLUMNS_COUNT = 7

# Rate limiter test configuration
RATE_LIMITER_REQUESTS = 2  # Number of requests allowed per window
RATE_LIMITER_WINDOW = 1.0  # Time window in seconds
TIMING_TOLERANCE = 0.1  # Allow 100ms timing variation

# Test server configuration
TEST_SERVER_BASE_URL = "http://localhost:8000"  # FastAPI default port

TEST_STOCK_SYMBOL = "TST"
