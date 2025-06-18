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
def test_raw_responses_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for test raw responses."""
    return tmp_path / "test_raw_responses"
```

### Patch Production Paths
```python
@pytest.fixture
async def loader(session: AsyncSession, test_raw_responses_dir: Path) -> StockDataLoader:
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
def test_dir(tmp_path: Path) -> Path:
    return tmp_path / "test_files"

def test_process_files(test_dir: Path):
    # Use test-specific directory
    test_file = test_dir / "test.html"
    test_file.write_text("test content")
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
def test_something(tmp_path: Path):
    test_dir = tmp_path / "test_directory"
    test_dir.mkdir(exist_ok=True)
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

## 5. Lessons Learned

### Test Data Alignment
- **Issue**: Test constants were out of sync with actual fixture data
- **Lesson**: Always ensure test data matches the actual fixture files
- **Best Practice**: When tests fail, first verify if test expectations match the test data
- **Implementation**: Keep test constants and fixture files in sync, and document the relationship between them

### Test Fixture Management
- **Issue**: Test fixture file name suggested June 16 data but contained June 13 data
- **Lesson**: Keep test fixture names and contents in sync
- **Best Practice**: Document expected data in fixture files
- **Implementation**: Add comments in fixture files to document the expected data

### Error Message Quality
- **Issue**: Initial error messages weren't descriptive enough
- **Lesson**: Good error messages are crucial for quick debugging
- **Best Practice**: Write clear assertion messages that show expected vs actual values
- **Implementation**: Use descriptive error messages in tests and validation code
