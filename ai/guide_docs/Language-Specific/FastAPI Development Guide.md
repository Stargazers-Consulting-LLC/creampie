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
- **Use proper semantic HTML elements**: Leverage `<thead>`, `<tbody>` when parsing tables
- **Write robust parsers**: Handle standard HTML table structures correctly
- **Avoid assumptions about structure**: Don't assume HTML will always have a specific format
- **Use semantic selectors**: Prefer direct, semantic selectors (e.g., `.table`) over complex ones

### CSS Selector Design
- **Keep selectors simple and specific**: Avoid overly complex selectors that are fragile
- **Use direct, semantic selectors**: Prefer `.table` over `.gridLayout > div:nth-child(2)`
- **Make selectors resilient**: Choose selectors that are less likely to break with HTML changes
- **Document selector assumptions**: Explain why specific selectors were chosen

## 5. Effective Debugging

### Best Practices
- **Add strategic debug output**: Include logging at key points in data processing pipelines
- **Make data flow visible**: Use debug prints to see actual data rather than making assumptions
- **Log at appropriate levels**: Use debug, info, warning, and error levels appropriately
- **Include context in logs**: Add relevant data to log messages for better debugging

### Data Ordering
- **Make data ordering explicit**: When dealing with time-series data, always consider the order
- **Add explicit sorting**: Use `sort_values("date")` to ensure consistent data order
- **Document ordering requirements**: Explain why specific ordering is important
- **Test ordering edge cases**: Verify behavior with different data orderings

## 6. Router Organization

### Import Patterns
- **Use direct imports with descriptive aliases**: Import routers directly from their source modules
- **Avoid re-export patterns**: Keep router imports direct and explicit
- **Use consistent naming**: Apply descriptive aliases for all routers

```python
# Good - direct imports with descriptive aliases
from cream_api.users.routes.auth import router as auth_router
from cream_api.stock_data.api import router as stock_data_router

app.include_router(auth_router)
app.include_router(stock_data_router)

# Avoid - module imports with attribute access
from cream_api.users.routes import auth
app.include_router(auth.router)  # Less explicit
```

### Router Structure
- **Import routers directly**: Avoid re-exporting routers in `__init__.py` files
- **Keep imports explicit**: Make it clear where each router comes from
- **Use consistent patterns**: Apply the same import pattern across all routers

## 7. Background Task Integration

### Task Organization
- **Keep tasks independent and focused**: Separate different operations into independent tasks
- **Use single responsibility principle**: Each task should have one clear purpose
- **Implement proper task lifecycle**: Create tasks with clear start/stop conditions

```python
# Good - independent, focused tasks
async def run_periodic_updates() -> None:
    """Run periodic updates of tracked stocks."""
    while True:
        try:
            await update_all_tracked_stocks()
        except Exception as e:
            logger.error("Error updating stocks: %s", str(e))
            return  # Stop task on error
        await asyncio.sleep(RETRIEVAL_INTERVAL_SECONDS)

async def run_periodic_file_processing() -> None:
    """Run periodic processing of raw HTML files."""
    while True:
        try:
            await process_raw_files_task()
        except RuntimeError as e:
            logger.critical("Critical error: %s", str(e))
            return  # Stop task on critical error
        except Exception as e:
            logger.error("Error processing files: %s", str(e))
            # Continue on non-critical errors
        await asyncio.sleep(PROCESSING_INTERVAL_SECONDS)
```

### Error Handling Strategy
- **Distinguish error types**: Use different exception types for different error categories
- **Implement appropriate responses**: Handle critical errors (stop task) and recoverable errors (continue) differently
- **Use proper logging levels**: Log critical errors with `logger.critical()` and regular errors with `logger.error()`
- **Provide clear error context**: Include relevant information in error messages

### Task Lifecycle Management
- **Use descriptive task names**: Make it clear what each task does
- **Implement consistent error handling**: Apply the same error handling patterns across tasks
- **Create clear start/stop conditions**: Define when tasks should start and stop
- **Monitor task health**: Include heartbeat logging and health checks
