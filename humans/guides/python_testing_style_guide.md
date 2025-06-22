# Python Testing Style Guide

> This guide provides comprehensive testing standards and best practices for Python code in the CreamPie project. It covers unit testing, integration testing, fixtures, mocking, and test organization.

## Table of Contents
1. [General Principles](#general-principles)
2. [Test Structure and Organization](#test-structure-and-organization)
3. [Unit Testing Patterns](#unit-testing-patterns)
4. [Integration Testing](#integration-testing)
5. [Test Fixtures and Setup](#test-fixtures-and-setup)
6. [Mocking and Patching](#mocking-and-patching)
7. [Test Data Management](#test-data-management)
8. [Performance Testing](#performance-testing)
9. [Coverage and Quality Metrics](#coverage-and-quality-metrics)
10. [Debugging Strategies](#debugging-strategies)
11. [Best Practices and Anti-patterns](#best-practices-and-anti-patterns)
12. [Example Patterns](#example-patterns)

---

## General Principles
- **Test everything that could break**: Focus on business logic, edge cases, and error conditions.
- **Write tests first (TDD)**: Write tests before implementing features when possible.
- **Keep tests simple and readable**: Tests should be easy to understand and maintain.
- **Test behavior, not implementation**: Focus on what the code does, not how it does it.
- **Use descriptive test names**: Test names should clearly describe what is being tested.
- **One assertion per test**: Each test should verify one specific behavior.
- **Tests should be independent**: Tests should not depend on each other or external state.
- **Use appropriate test isolation**: Each test should run in isolation with clean state.

## Test Structure and Organization
- Organize tests to mirror your source code structure.
- Use descriptive test class and method names.
- Group related tests using test classes or modules.
- Use `conftest.py` for shared fixtures and configuration.
- Example structure:

```
tests/
├── conftest.py
├── unit/
│   ├── test_api.py
│   ├── test_models.py
│   └── test_services.py
├── integration/
│   ├── test_database.py
│   └── test_external_apis.py
└── fixtures/
    └── sample_data.json
```

## Unit Testing Patterns
- Test individual functions and methods in isolation.
- Use dependency injection to make code testable.
- Mock external dependencies (databases, APIs, file systems).
- Test both happy path and error conditions.
- Use parameterized tests for multiple input scenarios.

### Test Method Naming
Use descriptive names that follow the pattern: `test_<method>_<scenario>_<expected_result>`

```python
def test_create_user_with_valid_data_returns_user_object(self):
    pass

def test_create_user_with_invalid_email_raises_validation_error(self):
    pass

def test_get_user_by_id_when_user_exists_returns_user(self):
    pass

def test_get_user_by_id_when_user_not_found_returns_none(self):
    pass
```

### Test Class Structure
```python
class TestUserService:
    """Test cases for UserService class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.user_service = UserService()
        self.test_user_data = {
            "email": "test@example.com",
            "name": "Test User"
        }

    def test_create_user_success(self):
        """Test successful user creation."""
        # Arrange
        user_data = self.test_user_data.copy()

        # Act
        result = self.user_service.create_user(user_data)

        # Assert
        assert result.email == user_data["email"]
        assert result.name == user_data["name"]
        assert result.id is not None

    def test_create_user_duplicate_email_raises_error(self):
        """Test that creating user with duplicate email raises error."""
        # Arrange
        user_data = self.test_user_data.copy()
        self.user_service.create_user(user_data)

        # Act & Assert
        with pytest.raises(DuplicateEmailError):
            self.user_service.create_user(user_data)
```

## Integration Testing
- Test interactions between multiple components.
- Use real databases and external services in controlled environments.
- Test complete workflows and user scenarios.
- Use test databases that can be reset between tests.

```python
class TestUserAPI:
    """Integration tests for User API endpoints."""

    @pytest.mark.asyncio
    async def test_create_user_endpoint(self, client, test_db):
        """Test user creation through API endpoint."""
        # Arrange
        user_data = {
            "email": "test@example.com",
            "name": "Test User"
        }

        # Act
        response = await client.post("/users/", json=user_data)

        # Assert
        assert response.status_code == 201
        result = response.json()
        assert result["email"] == user_data["email"]
        assert result["name"] == user_data["name"]
```

## Test Fixtures and Setup
- Use pytest fixtures for reusable test setup.
- Create fixtures for common test data and objects.
- Use fixture scopes appropriately (function, class, module, session).
- Clean up resources in fixture teardown.

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.fixture
def sample_user_data():
    """Provide sample user data for tests."""
    return {
        "email": "test@example.com",
        "name": "Test User",
        "password": "secure_password"
    }

@pytest.fixture
async def test_db():
    """Create a test database session."""
    # Setup
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine)
    async with async_session() as session:
        yield session

    # Teardown
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def mock_external_api():
    """Mock external API calls."""
    with patch("app.services.external_api.ExternalAPIClient") as mock:
        mock.return_value.get_data.return_value = {"status": "success"}
        yield mock
```

## Mocking and Patching
- Mock external dependencies to isolate units under test.
- Use `unittest.mock` or `pytest-mock` for mocking.
- Mock at the right level (prefer mocking interfaces over implementations).
- Verify that mocks are called with expected arguments.

```python
from unittest.mock import patch, MagicMock

class TestStockDataService:
    """Test cases for StockDataService."""

    @patch("app.services.stock_data.ExternalAPIClient")
    def test_fetch_stock_data_success(self, mock_api_client):
        """Test successful stock data fetching."""
        # Arrange
        mock_client = MagicMock()
        mock_api_client.return_value = mock_client
        mock_client.get_stock_data.return_value = {
            "symbol": "AAPL",
            "price": 150.0
        }

        service = StockDataService()

        # Act
        result = service.fetch_stock_data("AAPL")

        # Assert
        assert result["symbol"] == "AAPL"
        assert result["price"] == 150.0
        mock_client.get_stock_data.assert_called_once_with("AAPL")

    @patch("app.services.stock_data.ExternalAPIClient")
    def test_fetch_stock_data_api_error(self, mock_api_client):
        """Test handling of API errors."""
        # Arrange
        mock_client = MagicMock()
        mock_api_client.return_value = mock_client
        mock_client.get_stock_data.side_effect = APIError("Service unavailable")

        service = StockDataService()

        # Act & Assert
        with pytest.raises(StockDataError):
            service.fetch_stock_data("AAPL")
```

## Test Data Management
- Use factories or builders for creating test data.
- Keep test data minimal and focused.
- Use parameterized tests for multiple data scenarios.
- Avoid hardcoded test data in test methods.

```python
import factory
from faker import Faker

fake = Faker()

class UserFactory(factory.Factory):
    """Factory for creating test user data."""

    class Meta:
        model = dict

    email = factory.LazyFunction(fake.email)
    name = factory.LazyFunction(fake.name)
    password = factory.LazyFunction(lambda: fake.password())

class TestUserService:
    """Test cases using factory for test data."""

    def test_create_user_with_factory_data(self):
        """Test user creation using factory data."""
        # Arrange
        user_data = UserFactory()

        # Act
        result = self.user_service.create_user(user_data)

        # Assert
        assert result.email == user_data["email"]
        assert result.name == user_data["name"]

    @pytest.mark.parametrize("invalid_email", [
        "invalid-email",
        "missing@domain",
        "@nodomain.com",
        "spaces @domain.com"
    ])
    def test_create_user_invalid_emails(self, invalid_email):
        """Test user creation with various invalid emails."""
        user_data = UserFactory(email=invalid_email)

        with pytest.raises(ValidationError):
            self.user_service.create_user(user_data)
```

## Performance Testing
- Test performance-critical code paths.
- Use benchmarks to measure performance improvements.
- Test with realistic data volumes.
- Monitor memory usage and execution time.

```python
import time
import pytest

class TestPerformance:
    """Performance tests for critical code paths."""

    def test_bulk_user_creation_performance(self):
        """Test performance of bulk user creation."""
        # Arrange
        users_data = [UserFactory() for _ in range(1000)]
        start_time = time.time()

        # Act
        results = [self.user_service.create_user(data) for data in users_data]

        # Assert
        end_time = time.time()
        execution_time = end_time - start_time

        assert len(results) == 1000
        assert execution_time < 5.0  # Should complete within 5 seconds

    @pytest.mark.benchmark
    def test_database_query_performance(self, benchmark):
        """Benchmark database query performance."""
        def query_users():
            return self.user_service.get_all_users()

        result = benchmark(query_users)
        assert len(result) > 0
```

## Coverage and Quality Metrics
- Aim for high test coverage (80%+ for critical code).
- Use coverage tools to identify untested code.
- Focus on critical business logic coverage.
- Use mutation testing to verify test quality.

```python
# pytest.ini configuration
[tool:pytest]
addopts =
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

## Debugging Strategies

### Check Existing Reports First

**Problem**: Jumping straight into debugging without checking existing error reports wastes time.

**Solution**: Always check existing reports first:
1. **ALWAYS** check `ai/outputs/lint_results/` for existing tool reports
2. **ALWAYS** check `ai/outputs/test_results/` for existing test failure reports
3. **ALWAYS** check `ai/outputs/` for any other relevant reports
4. **ALWAYS** read the actual error messages from these reports
5. **ONLY THEN** begin debugging based on concrete error information

**Key Insight**: Don't assume you need to run tools when error reports already exist.

### Take a Step Back Before Making Changes

**Problem**: Making rapid changes without understanding the root cause leads to breaking more tests.

**Solution**: Pause and analyze before making changes:
1. Understand what the test is actually testing
2. Identify the root cause of the failure
3. Consider the impact of changes on other tests
4. Make targeted, minimal changes
5. Verify the fix doesn't break other functionality

**Key Insight**: Slow down to speed up - understanding the problem saves time in the long run.

### Use Systematic Debugging Approach

**Problem**: Random debugging attempts are inefficient and frustrating.

**Solution**: Use a systematic approach:
1. **Reproduce the issue** - Run the failing test to see the exact error
2. **Understand the context** - What is the test trying to verify?
3. **Identify the root cause** - Why is the test failing?
4. **Make minimal changes** - Fix only what's broken
5. **Verify the fix** - Ensure the fix works and doesn't break other tests

**Key Insight**: Systematic debugging is faster than trial and error.

### Don't Ignore Test Failures

**Problem**: Assuming tests pass just because a script executes leads to false confidence.

**Solution**: Always verify test results:
- **NEVER** assume tests pass just because a script executes
- **ALWAYS** check test result files for actual outcomes
- **ALWAYS** read test failure messages and error details
- **ALWAYS** verify test outcomes through actual result files

**Key Insight**: Test results are the source of truth, not assumptions.

### Test User Behavior, Not Implementation

**Problem**: Tests focused on implementation details rather than user behavior are brittle and hard to maintain.

**Solution**: Write tests that simulate real user interactions:
```python
# ✅ Good: Test user behavior
async def test_user_can_request_stock_tracking(self, client, test_db):
    """Test that users can successfully request stock tracking."""
    # Arrange
    user_data = {"symbol": "AAPL"}

    # Act
    response = await client.post("/stock-data/track", json=user_data)

    # Assert
    assert response.status_code == 200
    result = response.json()
    assert result["symbol"] == "AAPL"
    assert result["status"] == "tracking"

# ❌ Bad: Test implementation details
def test_calls_validation_function(self):
    """Test that validation function is called."""
    with patch('app.services.validate_symbol') as mock_validate:
        # ... testing internal validation calls
        mock_validate.assert_called_once()
```

### Mock at the Right Level

**Problem**: Over-mocking makes tests brittle and hard to debug.

**Solution**: Mock at the API boundary, not internal functions:
```python
# ✅ Good: Mock external API calls
@patch("app.services.stock_data.ExternalAPIClient")
def test_fetch_stock_data_success(self, mock_api_client):
    """Test successful stock data fetching."""
    # Mock external dependency
    mock_client = MagicMock()
    mock_api_client.return_value = mock_client
    mock_client.get_stock_data.return_value = {"symbol": "AAPL", "price": 150.0}

    # Test the service
    service = StockDataService()
    result = service.fetch_stock_data("AAPL")

    assert result["symbol"] == "AAPL"

# ❌ Bad: Mock internal validation
@patch("app.services.validate_symbol")
def test_validation_is_called(self, mock_validate):
    """Test that internal validation is called."""
    # Don't mock internal logic
    mock_validate.return_value = True
    # ... testing internal calls
```

### Test Error States Comprehensively

**Problem**: Only testing happy paths leaves error scenarios untested.

**Solution**: Test all error scenarios:
```python
async def test_stock_tracking_invalid_symbol(self, client, test_db):
    """Test handling of invalid stock symbols."""
    # Arrange
    invalid_data = {"symbol": "INVALID"}

    # Act
    response = await client.post("/stock-data/track", json=invalid_data)

    # Assert
    assert response.status_code == 400
    result = response.json()
    assert "invalid symbol" in result["detail"].lower()

async def test_stock_tracking_api_error(self, client, test_db):
    """Test handling of API errors."""
    # Arrange
    with patch("app.services.ExternalAPIClient") as mock_api:
        mock_api.return_value.get_data.side_effect = APIError("Service unavailable")

        # Act
        response = await client.post("/stock-data/track", json={"symbol": "AAPL"})

        # Assert
        assert response.status_code == 500
        result = response.json()
        assert "error" in result["detail"].lower()
```

## Best Practices and Anti-patterns

### Best Practices
- Write tests that are easy to understand and maintain.
- Use descriptive test names that explain the scenario.
- Test one thing per test method.
- Use appropriate assertions and error messages.
- Keep tests fast and reliable.
- Use test doubles (mocks, stubs) appropriately.
- Test user behavior, not implementation details.
- Mock external dependencies, not internal logic.
- Test error states and edge cases comprehensively.

### Anti-patterns to Avoid
- Testing implementation details instead of behavior.
- Writing tests that are too brittle (break with refactoring).
- Using shared state between tests.
- Testing multiple behaviors in a single test.
- Ignoring test failures or flaky tests.
- Writing tests that are hard to understand.
- Over-mocking internal logic.
- Only testing happy paths.
- Assuming tests pass without checking results.

## Example Patterns

### Complete Test Class Example
```python
import pytest
from unittest.mock import patch, MagicMock
from app.services.user_service import UserService
from app.models.user import User
from app.exceptions import ValidationError, DuplicateEmailError

class TestUserService:
    """Comprehensive test cases for UserService."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.user_service = UserService()
        self.valid_user_data = {
            "email": "test@example.com",
            "name": "Test User",
            "password": "secure_password"
        }

    def test_create_user_with_valid_data_returns_user(self):
        """Test successful user creation with valid data."""
        # Act
        result = self.user_service.create_user(self.valid_user_data)

        # Assert
        assert isinstance(result, User)
        assert result.email == self.valid_user_data["email"]
        assert result.name == self.valid_user_data["name"]
        assert result.id is not None

    def test_create_user_with_invalid_email_raises_error(self):
        """Test user creation with invalid email raises validation error."""
        # Arrange
        invalid_data = self.valid_user_data.copy()
        invalid_data["email"] = "invalid-email"

        # Act & Assert
        with pytest.raises(ValidationError, match="Invalid email format"):
            self.user_service.create_user(invalid_data)

    def test_create_user_with_duplicate_email_raises_error(self):
        """Test that creating user with duplicate email raises error."""
        # Arrange
        self.user_service.create_user(self.valid_user_data)

        # Act & Assert
        with pytest.raises(DuplicateEmailError):
            self.user_service.create_user(self.valid_user_data)

    @patch("app.services.user_service.EmailValidator")
    def test_create_user_validates_email_format(self, mock_validator):
        """Test that email validation is called during user creation."""
        # Arrange
        mock_validator.return_value.is_valid.return_value = True

        # Act
        self.user_service.create_user(self.valid_user_data)

        # Assert
        mock_validator.return_value.is_valid.assert_called_once_with(
            self.valid_user_data["email"]
        )

    @pytest.mark.parametrize("missing_field", ["email", "name", "password"])
    def test_create_user_missing_required_fields_raises_error(self, missing_field):
        """Test that missing required fields raise validation error."""
        # Arrange
        incomplete_data = self.valid_user_data.copy()
        del incomplete_data[missing_field]

        # Act & Assert
        with pytest.raises(ValidationError, match=f"Missing required field: {missing_field}"):
            self.user_service.create_user(incomplete_data)

    def test_get_user_by_id_when_user_exists_returns_user(self):
        """Test retrieving existing user by ID."""
        # Arrange
        created_user = self.user_service.create_user(self.valid_user_data)

        # Act
        result = self.user_service.get_user_by_id(created_user.id)

        # Assert
        assert result is not None
        assert result.id == created_user.id
        assert result.email == created_user.email

    def test_get_user_by_id_when_user_not_found_returns_none(self):
        """Test retrieving non-existent user returns None."""
        # Act
        result = self.user_service.get_user_by_id("non-existent-id")

        # Assert
        assert result is None
```

### Async Test Example
```python
import pytest
from httpx import AsyncClient

class TestUserAPI:
    """Integration tests for User API endpoints."""

    @pytest.mark.asyncio
    async def test_create_user_endpoint_success(self, async_client: AsyncClient):
        """Test successful user creation through API endpoint."""
        # Arrange
        user_data = {
            "email": "test@example.com",
            "name": "Test User",
            "password": "secure_password"
        }

        # Act
        response = await async_client.post("/users/", json=user_data)

        # Assert
        assert response.status_code == 201
        result = response.json()
        assert result["email"] == user_data["email"]
        assert result["name"] == user_data["name"]
        assert "id" in result

    @pytest.mark.asyncio
    async def test_get_user_endpoint_success(self, async_client: AsyncClient, test_user):
        """Test successful user retrieval through API endpoint."""
        # Act
        response = await async_client.get(f"/users/{test_user.id}")

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert result["id"] == test_user.id
        assert result["email"] == test_user.email

    @pytest.mark.asyncio
    async def test_get_user_endpoint_not_found(self, async_client: AsyncClient):
        """Test user retrieval for non-existent user returns 404."""
        # Act
        response = await async_client.get("/users/non-existent-id")

        # Assert
        assert response.status_code == 404
```

---

This testing style guide provides a comprehensive foundation for writing reliable, maintainable, and effective tests. Follow these patterns to ensure your code is well-tested and robust.
