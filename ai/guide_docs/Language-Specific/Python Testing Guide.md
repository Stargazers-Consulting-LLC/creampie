# Python Testing Guide

> **For AI Assistants**: This guide outlines best practices for testing Python code, including test organization, fixtures, and test data management. All patterns include validation rules and implementation guidance for comprehensive test coverage.

## AI Metadata

**Template Version:** 2.0
**AI Processing Level:** High
**Required Context:** Python testing, pytest, mocking, test data management
**Validation Required:** Yes
**Code Generation:** Supported

**Dependencies:**
- `../Core%20Principles.md` - Decision-making frameworks
- `../Python%20Style%20Guide.md` - Python implementation patterns
- `../Domain-Specific/Web%20Scraping%20Patterns.md` - File processing patterns
- `../../project_context/Common%20Patterns.md` - Project-specific patterns
- `../../project_context/Architecture%20Overview.md` - System architecture

**Validation Rules:**
- All tests must include proper error handling and edge cases
- Test data must be isolated and not use production directories
- Mocking must be used for external dependencies
- Test organization must follow established patterns
- Performance tests must include realistic measurements

## Overview

**Document Purpose:** Comprehensive Python testing standards and best practices for the CreamPie project
**Scope:** Unit testing, integration testing, test data management, and performance testing
**Target Users:** AI assistants and developers implementing Python tests
**Last Updated:** Current

**AI Context:** This guide provides the foundational testing patterns that must be followed for all Python development in the project. It ensures comprehensive test coverage, proper isolation, and maintainable test suites.

## 1. Testing Fundamentals

### General Testing Guidelines
1. Write unit tests for all functions
2. Use pytest for testing
3. Use fixtures for test setup
4. Use parametrize for multiple test cases
5. Use mock for external dependencies
6. Include both positive and negative test cases
7. Mock external dependencies in tests

**Code Generation Hint**: These guidelines will inform all test implementation throughout the project.

**Validation**: All tests must follow these guidelines and include comprehensive coverage.

### Test Directory Structure
```
cream_api/
├── tests/
│   ├── conftest.py              # Shared test configuration
│   ├── stock_data/
│   │   ├── fixtures/           # Test-specific data files
│   │   │   └── AAPL_2025-06-16.html
│   │   ├── test_loader.py
│   │   ├── test_parser.py
│   │   └── test_constants.py
│   ├── users/
│   │   ├── test_auth.py
│   │   └── test_models.py
│   └── common/
│       └── test_rate_limiting.py
└── ...
```

**Code Generation Hint**: This structure will inform all test organization and file placement.

**Validation**: All test modules must follow this structure and naming conventions.

## 2. Test Data Management

### Directory Isolation
- Production data directories (e.g., `raw_responses/`) should NEVER be used in tests
- Each test module should have its own test-specific directories
- Use temporary directories for file operations in tests

**Code Generation Hint**: This isolation strategy will inform all test data management implementation.

**Validation**: All tests must use isolated test data and never reference production directories.

### Test Fixture Patterns
```python
import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch
from typing import AsyncGenerator

@pytest.fixture
def test_raw_responses_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for test raw responses."""
    test_dir = tmp_path / "test_raw_responses"
    test_dir.mkdir(exist_ok=True)
    return test_dir

@pytest.fixture
def sample_html_file(test_raw_responses_dir: Path) -> Path:
    """Create a sample HTML file for testing."""
    html_content = """
    <html>
        <body>
            <table class="stock-table">
                <tr><th>Symbol</th><th>Price</th></tr>
                <tr><td>AAPL</td><td>150.00</td></tr>
            </table>
        </body>
    </html>
    """
    file_path = test_raw_responses_dir / "test_stock_data.html"
    file_path.write_text(html_content)
    return file_path

@pytest.fixture
async def async_test_db():
    """Create async test database session."""
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemy.orm import sessionmaker

    # Use in-memory SQLite for testing
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        # Create tables
        from cream_api.models import Base
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    await engine.dispose()

@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    with patch("cream_api.settings.app_settings") as mock_settings:
        mock_settings.HTML_RAW_RESPONSES_DIR = Path("/test/raw")
        mock_settings.HTML_PARSED_RESPONSES_DIR = Path("/test/parsed")
        mock_settings.DATABASE_URL = "sqlite+aiosqlite:///:memory:"
        yield mock_settings
```

**Code Generation Hint**: These fixture patterns will inform all test setup and data management implementation.

**Validation**: All tests must use proper fixtures for data setup and cleanup.

### Patch Production Paths
```python
@pytest.fixture
async def loader_with_mock_paths(session: AsyncSession, test_raw_responses_dir: Path) -> StockDataLoader:
    """Create loader with mocked production paths."""
    with patch("cream_api.settings.app_settings.HTML_RAW_RESPONSES_DIR", test_raw_responses_dir):
        with patch("cream_api.settings.app_settings.HTML_PARSED_RESPONSES_DIR", test_raw_responses_dir / "parsed"):
            return StockDataLoader(session)

@pytest.fixture
def mock_external_api():
    """Mock external API calls."""
    with patch("cream_api.stock_data.retriever.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "<html>Mock response</html>"
        yield mock_get
```

**Code Generation Hint**: This patching pattern will inform all external dependency mocking implementation.

**Validation**: All external dependencies must be properly mocked in tests.

## 3. Test Organization Patterns

### Test Class Structure
```python
import pytest
from unittest.mock import Mock, patch
from typing import List, Dict, Any

class TestStockDataProcessor:
    """Test suite for StockDataProcessor."""

    @pytest.fixture(autouse=True)
    def setup(self, async_test_db, mock_config):
        """Setup test environment."""
        self.db = async_test_db
        self.config = mock_config
        self.processor = StockDataProcessor(self.db)

    def test_process_valid_data(self, sample_html_file: Path):
        """Test processing valid HTML data."""
        # Arrange
        expected_data = [
            {"symbol": "AAPL", "price": "150.00"}
        ]

        # Act
        result = self.processor.process_file(sample_html_file)

        # Assert
        assert result == expected_data
        assert len(result) == 1

    def test_process_invalid_file(self, test_raw_responses_dir: Path):
        """Test processing invalid file."""
        # Arrange
        invalid_file = test_raw_responses_dir / "invalid.txt"
        invalid_file.write_text("Not HTML content")

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid HTML file"):
            self.processor.process_file(invalid_file)

    @pytest.mark.parametrize("html_content,expected_count", [
        ("<table><tr><td>AAPL</td></tr></table>", 1),
        ("<table><tr><td>AAPL</td></tr><tr><td>TSLA</td></tr></table>", 2),
        ("<div>No table</div>", 0),
    ])
    def test_process_various_content(self, html_content: str, expected_count: int, test_raw_responses_dir: Path):
        """Test processing various HTML content."""
        # Arrange
        test_file = test_raw_responses_dir / "test.html"
        test_file.write_text(html_content)

        # Act
        result = self.processor.process_file(test_file)

        # Assert
        assert len(result) == expected_count
```

**Code Generation Hint**: This test class pattern will inform all test organization and structure implementation.

**Validation**: All test suites must follow this structure with proper setup, teardown, and parametrization.

### Async Test Patterns
```python
import pytest
import asyncio
from unittest.mock import AsyncMock

class TestAsyncStockDataProcessor:
    """Test suite for async stock data processing."""

    @pytest.fixture(autouse=True)
    async def setup(self, async_test_db):
        """Setup async test environment."""
        self.db = async_test_db
        self.processor = AsyncStockDataProcessor(self.db)

    @pytest.mark.asyncio
    async def test_async_process_files(self, sample_html_file: Path):
        """Test async file processing."""
        # Arrange
        files = [sample_html_file]

        # Act
        results = await self.processor.process_files(files)

        # Assert
        assert len(results) == 1
        assert results[0]["success"] is True

    @pytest.mark.asyncio
    async def test_async_process_with_error(self, test_raw_responses_dir: Path):
        """Test async processing with error handling."""
        # Arrange
        invalid_file = test_raw_responses_dir / "invalid.html"
        invalid_file.write_text("Invalid content")

        # Act
        results = await self.processor.process_files([invalid_file])

        # Assert
        assert len(results) == 1
        assert results[0]["success"] is False
        assert "error" in results[0]

    @pytest.mark.asyncio
    async def test_concurrent_processing(self, sample_html_file: Path):
        """Test concurrent file processing."""
        # Arrange
        files = [sample_html_file] * 5  # Process same file 5 times

        # Act
        start_time = asyncio.get_event_loop().time()
        results = await self.processor.process_files_concurrent(files)
        end_time = asyncio.get_event_loop().time()

        # Assert
        assert len(results) == 5
        assert all(r["success"] for r in results)
        assert end_time - start_time < 2.0  # Should complete quickly
```

**Code Generation Hint**: This async test pattern will inform all asynchronous test implementation.

**Validation**: All async tests must use proper async fixtures and error handling.

## 4. Mocking Patterns

### External API Mocking
```python
import pytest
from unittest.mock import Mock, patch, AsyncMock
from httpx import AsyncClient

class TestExternalAPIIntegration:
    """Test external API integration."""

    @pytest.fixture
    def mock_stock_api(self):
        """Mock stock API responses."""
        with patch("cream_api.stock_data.retriever.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "<html>Stock data</html>"

            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            yield mock_client_instance

    @pytest.mark.asyncio
    async def test_fetch_stock_data_success(self, mock_stock_api):
        """Test successful stock data fetching."""
        # Arrange
        symbol = "AAPL"

        # Act
        result = await fetch_stock_data(symbol)

        # Assert
        assert result is not None
        mock_stock_api.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_stock_data_failure(self, mock_stock_api):
        """Test stock data fetching failure."""
        # Arrange
        mock_stock_api.get.side_effect = Exception("API Error")
        symbol = "INVALID"

        # Act & Assert
        with pytest.raises(Exception, match="API Error"):
            await fetch_stock_data(symbol)
```

**Code Generation Hint**: This mocking pattern will inform all external API test implementation.

**Validation**: All external API tests must include proper mocking and error scenarios.

### Database Mocking
```python
import pytest
from unittest.mock import Mock, patch
from sqlalchemy.ext.asyncio import AsyncSession

class TestDatabaseOperations:
    """Test database operations."""

    @pytest.fixture
    def mock_session(self):
        """Mock database session."""
        session = Mock(spec=AsyncSession)
        session.commit = AsyncMock()
        session.rollback = AsyncMock()
        session.close = AsyncMock()
        return session

    @pytest.mark.asyncio
    async def test_save_stock_data(self, mock_session):
        """Test saving stock data to database."""
        # Arrange
        stock_data = {"symbol": "AAPL", "price": 150.00}

        # Act
        result = await save_stock_data(mock_session, stock_data)

        # Assert
        assert result is True
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_stock_data_error(self, mock_session):
        """Test database error handling."""
        # Arrange
        mock_session.commit.side_effect = Exception("Database error")
        stock_data = {"symbol": "AAPL", "price": 150.00}

        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            await save_stock_data(mock_session, stock_data)

        mock_session.rollback.assert_called_once()
```

**Code Generation Hint**: This database mocking pattern will inform all database test implementation.

**Validation**: All database tests must include proper session mocking and error handling.

## 5. Performance Testing

### Performance Test Patterns
```python
import pytest
import time
import asyncio
from typing import List

class TestPerformance:
    """Performance test suite."""

    # Performance constants
    MAX_PROCESSING_TIME_SECONDS = 5.0
    MAX_MEMORY_USAGE_MB = 100
    MIN_THROUGHPUT_RECORDS_PER_SECOND = 10

    def test_processing_performance(self, large_dataset: List[Dict]):
        """Test processing performance with large dataset."""
        # Arrange
        start_time = time.time()

        # Act
        result = process_large_dataset(large_dataset)
        end_time = time.time()

        # Assert
        processing_time = end_time - start_time
        assert processing_time < self.MAX_PROCESSING_TIME_SECONDS, \
            f"Processing took {processing_time}s, expected <{self.MAX_PROCESSING_TIME_SECONDS}s"

        assert len(result) == len(large_dataset)

    @pytest.mark.asyncio
    async def test_concurrent_processing_performance(self, sample_html_file: Path):
        """Test concurrent processing performance."""
        # Arrange
        files = [sample_html_file] * 50  # Process 50 files concurrently
        start_time = asyncio.get_event_loop().time()

        # Act
        results = await process_files_concurrent(files)
        end_time = asyncio.get_event_loop().time()

        # Assert
        processing_time = end_time - start_time
        throughput = len(files) / processing_time

        assert throughput >= self.MIN_THROUGHPUT_RECORDS_PER_SECOND, \
            f"Throughput {throughput:.2f} records/sec, expected >= {self.MIN_THROUGHPUT_RECORDS_PER_SECOND}"

        assert all(r["success"] for r in results)

    def test_memory_usage(self, large_dataset: List[Dict]):
        """Test memory usage during processing."""
        import psutil
        import os

        # Arrange
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Act
        result = process_large_dataset(large_dataset)
        final_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Assert
        memory_increase = final_memory - initial_memory
        assert memory_increase < self.MAX_MEMORY_USAGE_MB, \
            f"Memory increase {memory_increase:.2f}MB, expected <{self.MAX_MEMORY_USAGE_MB}MB"
```

**Code Generation Hint**: This performance test pattern will inform all performance testing implementation.

**Validation**: All performance tests must include realistic measurements and clear assertions.

## 6. Integration Testing

### API Integration Testing
```python
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

class TestAPIEndpoints:
    """Test API endpoint integration."""

    @pytest.fixture
    def client(self, test_app):
        """Create test client."""
        return TestClient(test_app)

    def test_get_stock_data_endpoint(self, client: TestClient):
        """Test GET /stock-data endpoint."""
        # Act
        response = client.get("/stock-data/AAPL")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "symbol" in data
        assert "price" in data

    def test_post_stock_tracking(self, client: TestClient):
        """Test POST /stock-data/track endpoint."""
        # Arrange
        payload = {"symbol": "TSLA"}

        # Act
        response = client.post("/stock-data/track", json=payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "TSLA"
        assert data["is_active"] is True

    @pytest.mark.asyncio
    async def test_async_api_endpoint(self, async_client: AsyncClient):
        """Test async API endpoint."""
        # Act
        response = await async_client.get("/stock-data/AAPL")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "symbol" in data
```

**Code Generation Hint**: This integration test pattern will inform all API integration testing implementation.

**Validation**: All integration tests must include proper client setup and response validation.

## 7. Test Data Management

### Test Data Factory Patterns
```python
from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime

@dataclass
class TestStockData:
    """Test stock data factory."""
    symbol: str = "AAPL"
    price: float = 150.00
    volume: int = 1000000
    date: datetime = None

    def __post_init__(self):
        if self.date is None:
            self.date = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "symbol": self.symbol,
            "price": self.price,
            "volume": self.volume,
            "date": self.date.isoformat()
        }

    @classmethod
    def create_batch(cls, count: int) -> List[Dict[str, Any]]:
        """Create batch of test data."""
        symbols = ["AAPL", "TSLA", "GOOGL", "MSFT", "AMZN"]
        return [
            cls(symbol=symbols[i % len(symbols)], price=100 + i * 10).to_dict()
            for i in range(count)
        ]

@pytest.fixture
def sample_stock_data() -> TestStockData:
    """Create sample stock data."""
    return TestStockData()

@pytest.fixture
def large_dataset() -> List[Dict[str, Any]]:
    """Create large dataset for performance testing."""
    return TestStockData.create_batch(1000)
```

**Code Generation Hint**: This test data factory pattern will inform all test data creation implementation.

**Validation**: All test data must be created using proper factories and fixtures.

## Implementation Guidelines

### For AI Assistants
1. **Follow these patterns** for all test implementation
2. **Use proper fixtures** for test setup and teardown
3. **Mock external dependencies** to ensure test isolation
4. **Include comprehensive error cases** in test coverage
5. **Use parametrization** for multiple test scenarios
6. **Implement performance tests** for critical operations
7. **Follow test organization** patterns for maintainability
8. **Use proper assertions** with descriptive messages

### For Human Developers
1. **Reference these patterns** when writing tests
2. **Use isolated test data** and never reference production
3. **Mock external dependencies** for reliable tests
4. **Include both success and error cases** in test coverage
5. **Use descriptive test names** and assertions
6. **Follow established patterns** for consistency
7. **Test performance** for critical operations

## Quality Assurance

### Test Coverage Standards
- All functions must have unit tests
- All API endpoints must have integration tests
- All error paths must be tested
- Performance tests must be included for critical operations
- Test data must be properly isolated

### Test Quality Standards
- Tests must be independent and repeatable
- Test names must be descriptive and clear
- Assertions must include descriptive messages
- Test data must be minimal and focused
- Error handling must be comprehensive

### Performance Standards
- Unit tests must complete in under 1 second
- Integration tests must complete in under 5 seconds
- Performance tests must include realistic measurements
- Memory usage must be monitored and controlled
- Concurrent operations must be properly tested

### Maintenance Standards
- Tests must be updated with code changes
- Test data must be kept current and relevant
- Mock responses must reflect actual API behavior
- Performance benchmarks must be regularly updated
- Test documentation must be maintained

---

**AI Quality Checklist**: Before implementing tests, ensure:
- [x] Test data is properly isolated from production
- [x] External dependencies are properly mocked
- [x] Both success and error cases are covered
- [x] Performance tests include realistic measurements
- [x] Test organization follows established patterns
- [x] Assertions include descriptive messages
- [x] Test data factories are used for consistency
- [x] Async tests use proper async patterns
