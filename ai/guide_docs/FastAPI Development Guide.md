# FastAPI Development Guide

This guide outlines best practices for developing web applications using FastAPI.

## 1. Route Handlers

### General Guidelines
- Use async/await for route handlers
- Include return type hints for all route handlers
- Group related routes using FastAPI routers
- Use descriptive route paths and HTTP methods
- Document API endpoints with clear docstrings

### Example Route Handler
```python
@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_db)
) -> UserResponse:
    """Get a user by their ID.

    Args:
        user_id: The ID of the user to retrieve
        db: Database session dependency

    Returns:
        UserResponse: The requested user's data

    Raises:
        HTTPException: If the user is not found
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.from_orm(user)
```

## 2. Configuration

### Settings Management
- Use Pydantic for settings management
- Implement settings as a class inheriting from BaseSettings
- Use environment variables for configuration
- Cache configuration using lru_cache decorator
- Keep configuration logic separate from application code

### Example Settings Class
```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class AppSettings(BaseSettings):
    """Application settings."""

    # Database settings
    DATABASE_URL: str

    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Cream API"

    # Security settings
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> AppSettings:
    """Get cached application settings."""
    return AppSettings()
```

## 3. Testing FastAPI Applications

### Test Application Setup
```python
@pytest.fixture
def app(async_test_db: AsyncSession):
    """Create a test FastAPI application."""
    app = FastAPI()

    # Override the database dependency
    async def override_get_async_db():
        yield async_test_db

    app.dependency_overrides[get_async_db] = override_get_async_db
    app.include_router(router)
    return app
```

### Async Database Testing
- Use `pytest_asyncio` for async tests
- Create separate fixtures for sync and async databases
- Use in-memory SQLite for testing
- Ensure proper cleanup after tests

### Background Task Testing
- Mock `BackgroundTasks.add_task` instead of the task function
- Test both success and error cases
- Verify task scheduling without executing the task

### Error Handling Tests
- Test both expected and unexpected errors
- Verify correct HTTP status codes
- Check error messages and response structure
- Test database rollback behavior

### Test Isolation
- Each test should have its own database session
- Clean up resources after each test
- Don't rely on test execution order
- Use fixtures for shared setup

## 4. HTML Structure Handling

### Best Practices
- **Issue**: Initial code assumed a simpler HTML structure than what was present
- **Lesson**: Don't make assumptions about HTML structure
- **Best Practice**: Use proper semantic HTML elements (`<thead>`, `<tbody>`) when parsing tables
- **Implementation**: Write robust parsers that handle standard HTML table structures correctly

### CSS Selector Design
- **Issue**: Complex selector (`.gridLayout > div:nth-child(2)`) was fragile
- **Lesson**: Simpler, more specific selectors are more reliable
- **Best Practice**: Avoid overly complex selectors when possible
- **Implementation**: Use direct, semantic selectors (e.g., `.table`) that are less likely to break

## 5. Effective Debugging

### Best Practices
- **Issue**: Complex data parsing issues were difficult to diagnose
- **Lesson**: Strategic debug output is crucial for understanding data flow
- **Best Practice**: Add targeted debug prints to see actual data rather than making assumptions
- **Implementation**: Include debug logging at key points in data processing pipelines

### Data Ordering
- **Issue**: Data order was inconsistent
- **Lesson**: When dealing with time-series data, always consider the order
- **Best Practice**: Make data ordering explicit in the code
- **Implementation**: Add explicit sorting by date to ensure consistent data order
