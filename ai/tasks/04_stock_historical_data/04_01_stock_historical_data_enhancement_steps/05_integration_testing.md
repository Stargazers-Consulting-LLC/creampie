# Integration Testing Guide

## Overview

This guide details the integration testing strategy for the stock historical data system. The tests will:

1. Verify component interactions
2. Test end-to-end workflows
3. Validate data flow
4. Ensure system reliability

## Implementation Steps

### 1. Create Integration Test Suite

Create `tests/integration/test_stock_data_flow.py`:

```python
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.cache.html_cache import HTMLCache
from src.data.data_processor import StockDataProcessor
from src.database.models import Base
from src.parser.yahoo_parser import YahooFinanceParser
from config.settings import get_settings

settings = get_settings()

@pytest.fixture
def test_db() -> Generator[Session, Any, None]:
    """Create test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def test_cache_dir(tmp_path: Path) -> Path:
    """Create test cache directory."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    return cache_dir

@pytest.fixture
def stock_data_components(test_db: Session, test_cache_dir: Path) -> dict[str, Any]:
    """Create stock data system components."""
    settings.CACHE_DIR = test_cache_dir
    return {
        "parser": YahooFinanceParser(),
        "processor": StockDataProcessor(test_db),
        "cache": HTMLCache(test_db),
    }

def test_end_to_end_flow(stock_data_components: dict[str, Any]) -> None:
    """Test complete stock data flow."""
    parser = stock_data_components["parser"]
    processor = stock_data_components["processor"]
    cache = stock_data_components["cache"]

    # Fetch and parse data
    soup = parser.fetch_stock_data("AAPL")
    assert soup is not None

    # Cache HTML
    html_content = str(soup)
    cache_path = cache.save_html("AAPL", html_content)
    assert cache_path.exists()

    # Process data
    df = parser.parse_html(html_content)
    processed_df = processor.process_data(df, "AAPL")

    # Save to database
    processor.save_to_db(processed_df)

    # Retrieve from database
    retrieved_df = processor.get_stock_data("AAPL")
    assert not retrieved_df.empty
    assert list(retrieved_df.columns) == [
        "symbol",
        "open",
        "high",
        "low",
        "close",
        "adj_close",
        "volume",
    ]

def test_cache_and_retrieve(stock_data_components: dict[str, Any]) -> None:
    """Test caching and retrieving data."""
    parser = stock_data_components["parser"]
    cache = stock_data_components["cache"]

    # Fetch and cache data
    soup = parser.fetch_stock_data("AAPL")
    assert soup is not None

    html_content = str(soup)
    cache_path = cache.save_html("AAPL", html_content)

    # Retrieve from cache
    cached_html = cache.get_cached_html("AAPL")
    assert cached_html == html_content

    # Verify cache stats
    stats = cache.get_cache_stats()
    assert stats["total_files"] == 1
    assert stats["unique_symbols"] == 1

def test_data_processing_flow(stock_data_components: dict[str, Any]) -> None:
    """Test data processing workflow."""
    parser = stock_data_components["parser"]
    processor = stock_data_components["processor"]

    # Fetch and parse data
    soup = parser.fetch_stock_data("AAPL")
    assert soup is not None

    # Process data
    df = parser.parse_html(str(soup))
    processed_df = processor.process_data(df, "AAPL")

    # Verify processed data
    assert "symbol" in processed_df.columns
    assert "daily_return" in processed_df.columns
    assert "volatility" in processed_df.columns
    assert "sma_20" in processed_df.columns
    assert "sma_50" in processed_df.columns

    # Calculate metrics
    metrics = processor.calculate_metrics(processed_df)
    assert "total_return" in metrics
    assert "volatility" in metrics
    assert "avg_volume" in metrics

def test_error_handling(stock_data_components: dict[str, Any]) -> None:
    """Test error handling in the system."""
    parser = stock_data_components["parser"]
    processor = stock_data_components["processor"]
    cache = stock_data_components["cache"]

    # Test invalid symbol
    soup = parser.fetch_stock_data("INVALID_SYMBOL")
    assert soup is None

    # Test invalid HTML
    with pytest.raises(ValueError):
        parser.parse_html("<invalid>html</invalid>")

    # Test cache expiration
    cache.save_html("AAPL", "<html>test</html>")
    cache.cleanup_expired_cache()
    assert not cache.get_cached_html("AAPL")

def test_concurrent_operations(stock_data_components: dict[str, Any]) -> None:
    """Test concurrent operations."""
    parser = stock_data_components["parser"]
    processor = stock_data_components["processor"]
    cache = stock_data_components["cache"]

    # Fetch multiple symbols
    symbols = ["AAPL", "TSLA", "MSFT"]
    for symbol in symbols:
        soup = parser.fetch_stock_data(symbol)
        if soup:
            html_content = str(soup)
            cache.save_html(symbol, html_content)
            df = parser.parse_html(html_content)
            processed_df = processor.process_data(df, symbol)
            processor.save_to_db(processed_df)

    # Verify all symbols are cached
    stats = cache.get_cache_stats()
    assert stats["unique_symbols"] == len(symbols)

    # Verify all symbols are in database
    for symbol in symbols:
        df = processor.get_stock_data(symbol)
        assert not df.empty
        assert df["symbol"].iloc[0] == symbol
```

### 2. Create Test Configuration

Create `tests/integration/conftest.py`:

```python
from pathlib import Path
from typing import Any, Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.database.models import Base
from config.settings import get_settings

settings = get_settings()

@pytest.fixture(scope="session")
def test_engine() -> Any:
    """Create test database engine."""
    return create_engine("sqlite:///:memory:")

@pytest.fixture(scope="session")
def test_db_engine(test_engine: Any) -> Generator[Any, Any, None]:
    """Create test database tables."""
    Base.metadata.create_all(test_engine)
    yield test_engine
    Base.metadata.drop_all(test_engine)

@pytest.fixture
def test_db_session(test_db_engine: Any) -> Generator[Session, Any, None]:
    """Create test database session."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_db_engine
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def test_cache_dir(tmp_path: Path) -> Path:
    """Create test cache directory."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    return cache_dir
```

## Test Categories

1. **End-to-End Tests**

   - Complete data flow
   - Component interactions
   - System integration

2. **Workflow Tests**

   - Data processing
   - Cache management
   - Database operations

3. **Error Handling Tests**

   - Invalid inputs
   - System failures
   - Edge cases

4. **Concurrent Operation Tests**
   - Multiple symbols
   - Parallel processing
   - Resource management

## Test Data Management

1. **Test Data Sources**

   - Real stock data
   - Generated test data
   - Edge case data

2. **Data Cleanup**

   - Database cleanup
   - Cache cleanup
   - File system cleanup

3. **Test Isolation**
   - Separate test database
   - Isolated cache directory
   - Independent test cases

## Test Execution

1. **Running Tests**

   ```bash
   pytest tests/integration -v
   ```

2. **Test Coverage**

   ```bash
   pytest tests/integration --cov=src --cov-report=html
   ```

3. **Test Reports**
   - HTML coverage report
   - Test execution summary
   - Error reports

## Next Steps

After implementing integration tests:

1. Run the test suite
2. Review test coverage
3. Fix any issues
4. Proceed to Deployment
