# Test Directory Management

This guide outlines best practices for managing test directories and ensuring proper test isolation in the project.

## 1. Directory Structure

### Test-Specific Directories
```
cream_api/
├── tests/
│   ├── stock_data/
│   │   ├── fixtures/           # Test-specific data files
│   │   │   └── AAPL_2025-06-16_20250616_185555.html
│   │   ├── test_loader.py
│   │   ├── test_parser.py
│   │   └── test_constants.py
│   └── ...
└── ...
```

### Production vs Test Directories
- Production data directories (e.g., `raw_responses/`) should NEVER be used in tests
- Each test module should have its own test-specific directories
- Use temporary directories for file operations in tests

## 2. Best Practices

### Directory Isolation
1. **Use Temporary Directories**
   ```python
   @pytest.fixture
   def test_raw_responses_dir(tmp_path: Path) -> Path:
       """Create a temporary directory for test raw responses."""
       return tmp_path / "test_raw_responses"
   ```

2. **Patch Production Paths**
   ```python
   @pytest.fixture
   async def loader(session: AsyncSession, test_raw_responses_dir: Path) -> StockDataLoader:
       with patch("cream_api.settings.app_settings.HTML_RAW_RESPONSES_DIR", test_raw_responses_dir):
           return StockDataLoader(session)
   ```

3. **Use Test Fixtures**
   - Store test data files in `tests/<module>/fixtures/`
   - Reference fixtures using relative paths
   - Keep test data minimal and focused

### File Operations
1. **Clean Up After Tests**
   - Temporary directories are automatically cleaned up by pytest
   - Explicitly clean up any files created during tests
   - Use context managers for file operations

2. **File Path Management**
   ```python
   # Good: Use test-specific paths
   TEST_FIXTURES_DIR = os.path.join("cream_api", "tests", "stock_data", "fixtures")
   TEST_AAPL_FIXTURE_PATH = os.path.join(TEST_FIXTURES_DIR, TEST_AAPL_FIXTURE)

   # Bad: Use production paths
   RAW_RESPONSES_DIR = os.path.join("cream_api", "files", "raw_responses")  # Don't do this
   ```

3. **Directory Creation**
   ```python
   # Good: Create directories in fixtures
   test_raw_responses_dir.mkdir(exist_ok=True)
   test_parsed_responses_dir.mkdir(exist_ok=True)

   # Bad: Assume directories exist
   # Don't rely on production directories existing
   ```

## 3. Common Pitfalls

### 1. Using Production Directories
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

### 2. Hardcoding Paths
❌ **Wrong**
```python
TEST_FILE = "/path/to/production/file.html"  # Don't hardcode paths
```

✅ **Correct**
```python
TEST_FIXTURES_DIR = os.path.join("cream_api", "tests", "stock_data", "fixtures")
TEST_FILE = os.path.join(TEST_FIXTURES_DIR, "test.html")
```

### 3. Assuming Directory Existence
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

## 4. Lessons Learned

1. **Test Isolation**
   - Each test should be completely independent
   - Tests should not rely on external state
   - Use fixtures to set up test environment

2. **Directory Management**
   - Keep test data in test-specific directories
   - Use temporary directories for file operations
   - Clean up after tests

3. **Path Handling**
   - Use relative paths for test fixtures
   - Patch production paths in tests
   - Don't hardcode absolute paths

4. **File Operations**
   - Create necessary directories in fixtures
   - Use context managers for file operations
   - Clean up files after tests

## 5. Implementation Checklist

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
