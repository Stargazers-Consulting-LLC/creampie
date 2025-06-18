# Python Testing Guide

This guide outlines best practices for testing Python code, including test organization, fixtures, and test data management.

## 1. Testing Fundamentals

### General Testing Guidelines
1. Write unit tests for all functions
2. Use pytest for testing
3. Use fixtures for test setup
4. Use parametrize for multiple test cases
5. Use mock for external dependencies
6. Include both positive and negative test cases
7. Mock external dependencies in tests

### Test Directory Structure
```
cream_api/
├── tests/
│   ├── stock_data/
│   │   ├── fixtures/           # Test-specific data files
│   │   │   └── AAPL_2025-06-16.html
│   │   ├── test_loader.py
│   │   ├── test_parser.py
│   │   └── test_constants.py
│   └── ...
└── ...
```

## 2. Test Directory Management

### Directory Isolation
- Production data directories (e.g., `raw_responses/`) should NEVER be used in tests
- Each test module should have its own test-specific directories
- Use temporary directories for file operations in tests
```python
@pytest.fixture
def test_raw_responses_dir(tmp_path):
    """Create a temporary directory for test raw responses."""
    return os.path.join(tmp_path, "test_raw_responses")
```

### Patch Production Paths
```python
@pytest.fixture
async def loader(session: AsyncSession, test_raw_responses_dir: str) -> StockDataLoader:
    with patch("cream_api.settings.app_settings.HTML_RAW_RESPONSES_DIR", test_raw_responses_dir):
        return StockDataLoader(session)
```

### File Operations
- Store test data files in `tests/<module>/fixtures/`
- Reference fixtures using relative paths
- Keep test data minimal and focused
- Clean up after tests
- Use context managers for file operations

### File Path Management
```python
# Good: Use test-specific paths
TEST_FIXTURES_DIR = os.path.join("cream_api", "tests", "stock_data", "fixtures")
TEST_AAPL_FIXTURE_PATH = os.path.join(TEST_FIXTURES_DIR, TEST_AAPL_FIXTURE)

# Bad: Use production paths
RAW_RESPONSES_DIR = os.path.join("cream_api", "files", "raw_responses")  # Don't do this
```

## 3. Common Pitfalls

### Using Production Directories
❌ **Wrong**
```python
def test_process_files():
    # Don't use production directories
    for file in settings.HTML_RAW_RESPONSES_DIR.glob("*.html"):
        process_file(file)
```

✅ **Correct**
```python
@pytest.fixture
def test_dir(tmp_path):
    return os.path.join(tmp_path, "test_files")

def test_process_files(test_dir: str):
    # Use test-specific directory
    test_file = os.path.join(test_dir, "test.html")
    with open(test_file, "w") as f:
        f.write("test content")
    process_file(test_file)
```

### Hardcoding Paths
❌ **Wrong**
```python
TEST_FILE = "/path/to/production/file.html"  # Don't hardcode paths
```

✅ **Correct**
```python
TEST_FIXTURES_DIR = os.path.join("cream_api", "tests", "stock_data", "fixtures")
TEST_FILE = os.path.join(TEST_FIXTURES_DIR, "test.html")
```

### Assuming Directory Existence
❌ **Wrong**
```python
def test_something():
    # Don't assume directories exist
    process_files_in_directory("some/directory")
```

✅ **Correct**
```python
def test_something(tmp_path):
    test_dir = os.path.join(tmp_path, "test_directory")
    os.makedirs(test_dir, exist_ok=True)
    process_files_in_directory(test_dir)
```

## 4. Implementation Checklist

When writing tests that involve file operations:

- [ ] Use temporary directories for file operations
- [ ] Patch production paths with test paths
- [ ] Store test data in fixtures directory
- [ ] Use relative paths for test files
- [ ] Clean up files after tests
- [ ] Create necessary directories in fixtures
- [ ] Use context managers for file operations
- [ ] Test both success and error cases
- [ ] Verify file cleanup
- [ ] Document test data requirements

## 5. Best Practices

### Test Data Management
- **Keep test data and constants in sync**: Ensure test expectations match fixture files
- **Document test data requirements**: Add comments in fixture files to document expected data
- **Use descriptive fixture names**: Make it clear what data each fixture contains
- **Maintain test data consistency**: Update both constants and fixtures when data changes

### Configuration Testing
- **Mock configuration at module level**: Avoid redundant configuration loading in tests
- **Use consistent configuration patterns**: Mock configuration once and reuse across tests
- **Test configuration edge cases**: Verify behavior with different configuration values

```python
# Good - mock configuration once at module level
@pytest.fixture(autouse=True)
def mock_config():
    with patch("cream_api.stock_data.tasks.config") as mock_config:
        mock_config.raw_responses_dir = "/test/raw"
        mock_config.parsed_responses_dir = "/test/parsed"
        yield mock_config
```

### Performance Testing
- **Measure actual performance**: Implement real performance tests before making claims
- **Set realistic performance targets**: Base expectations on actual measurements
- **Test performance under load**: Verify behavior with realistic data volumes

```python
# Good - actual performance measurement with named constants
import time

# Define performance constants to avoid magic numbers
MAX_PROCESSING_TIME_SECONDS = 5.0

def test_processing_performance():
    start_time = time.time()
    result = process_large_dataset()
    end_time = time.time()

    processing_time = end_time - start_time
    assert processing_time < MAX_PROCESSING_TIME_SECONDS, f"Processing took {processing_time}s, expected <{MAX_PROCESSING_TIME_SECONDS}s"
```

### Error Handling Testing
- **Test critical failure scenarios**: Verify proper handling of application logic failures
- **Distinguish error types**: Test both critical errors (RuntimeError) and recoverable errors (Exception)
- **Verify error propagation**: Ensure errors are properly logged and handled

```python
# Good - test critical failure scenarios
def test_critical_failure_stops_task():
    with patch("os.listdir") as mock_listdir:
        mock_listdir.return_value = ["invalid.txt", "valid.html"]

        with pytest.raises(RuntimeError, match="CRITICAL: Non-HTML files"):
            process_raw_files_task()
```

### Task Integration Testing
- **Test components in isolation**: Mock external dependencies and test task behavior independently
- **Verify task lifecycle**: Test proper start/stop conditions and error handling
- **Test task interactions**: Ensure tasks work correctly when run together

```python
# Good - test task components in isolation
@pytest.mark.asyncio
async def test_process_raw_files_task_success():
    with patch("cream_api.stock_data.tasks.process_raw_files") as mock_process:
        mock_process.return_value = {"processed": 2, "failed": 0}

        result = await process_raw_files_task()

        assert result["processed"] == 2
        assert result["failed"] == 0
        mock_process.assert_called_once()
```

### Constants and Magic Numbers
- **Define test constants**: Use named constants instead of magic numbers in tests
- **Group related constants**: Keep test constants organized and documented
- **Use descriptive names**: Make constants self-documenting

```python
# Good - define test constants
class TestConstants:
    """Constants for testing."""
    MAX_PROCESSING_TIME_SECONDS = 5.0
    TEST_FILE_SIZE_BYTES = 1024
    EXPECTED_RECORD_COUNT = 10
    TIMEOUT_SECONDS = 30

def test_performance_with_constants():
    start_time = time.time()
    result = process_data()
    processing_time = time.time() - start_time

    assert processing_time < TestConstants.MAX_PROCESSING_TIME_SECONDS
    assert len(result) == TestConstants.EXPECTED_RECORD_COUNT
```

This guide ensures consistent, maintainable testing practices that align with the project's coding standards.
