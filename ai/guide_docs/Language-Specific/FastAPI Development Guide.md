# FastAPI Development Guide

> **For AI Assistants**: This guide outlines best practices for developing web applications using FastAPI. All sections include specific patterns, validation rules, and implementation guidance for consistent API development.

## AI Metadata

**Template Version:** 2.0
**AI Processing Level:** High
**Required Context:** FastAPI framework, async programming, API design patterns
**Validation Required:** Yes
**Code Generation:** Supported

**Dependencies:**
- `../Core%20Principles.md` - Decision-making frameworks
- `../project_context/Common%20Patterns.md` - Project patterns
- `../project_context/Architecture%20Overview.md` - System architecture
- `Python%20Style%20Guide.md` - Python implementation patterns
- `Python%20Testing%20Guide.md` - Testing patterns

**Validation Rules:**
- All endpoints must include proper type hints and response models
- Error handling must follow established project patterns
- Async/await must be used for all I/O operations
- Pydantic models must be used for request/response validation
- Testing must include both success and error cases

## Overview

**Document Purpose:** FastAPI development standards and best practices for the CreamPie project
**Scope:** All API endpoints, routing, testing, and configuration
**Target Users:** AI assistants and developers building FastAPI applications
**Last Updated:** Current

**AI Context:** This guide provides the foundational FastAPI development patterns that must be followed for all API development in the project. It ensures consistency, performance, and maintainability across all API endpoints.

## 1. Route Handlers

### General Guidelines
- Use async/await for route handlers
- Include return type hints for all route handlers
- Group related routes using FastAPI routers
- Use descriptive route paths and HTTP methods
- Document API endpoints with clear docstrings

**Code Generation Hint**: These guidelines will inform all FastAPI endpoint implementation throughout the project.

**Validation**: All route handlers must follow these guidelines without exception.

### Example Route Handler
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ..db import get_async_db
from ..models import User
from ..schemas import UserResponse, UserCreate

router = APIRouter()

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
    try:
        user = await get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse.from_orm(user)
    except Exception as e:
        logger.error(f"Error retrieving user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

**Code Generation Hint**: This pattern will inform route handler implementation with proper error handling and response models.

**Validation**: Route handlers must include proper error handling, logging, and response model validation.

### Router Organization Pattern
```python
# In cream_api/stock_data/api.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_async_db
from ..models import TrackedStock
from ..schemas import StockRequestCreate, StockRequestResponse
from ..tasks import update_all_tracked_stocks

router = APIRouter(prefix="/stock-data", tags=["Stock Data"])

@router.post("/track", response_model=StockRequestResponse)
async def track_stock(
    request: StockRequestCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db)
) -> StockRequestResponse:
    """Add a new stock to tracking."""
    try:
        # Business logic here
        tracked_stock = await create_tracked_stock(db, request.symbol)

        # Add background task
        background_tasks.add_task(update_all_tracked_stocks)

        return StockRequestResponse.from_orm(tracked_stock)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error tracking stock {request.symbol}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

**Code Generation Hint**: This pattern will inform router organization and endpoint implementation with background tasks.

**Validation**: Routers must include proper prefixes, tags, error handling, and background task integration.

## 2. Configuration

### Settings Management
- Use Pydantic for settings management
- Implement settings as a class inheriting from BaseSettings
- Use environment variables for configuration
- Cache configuration using lru_cache decorator
- Keep configuration logic separate from application code

**Code Generation Hint**: These patterns will inform configuration management throughout the project.

**Validation**: Configuration must use Pydantic models and environment variable support.

### Example Settings Class
```python
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class AppSettings(BaseSettings):
    """Application settings."""

    # Database settings
    DATABASE_URL: str
    DATABASE_ECHO: bool = False

    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Cream API"
    VERSION: str = "1.0.0"

    # Security settings
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    # CORS settings
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # Logging settings
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> AppSettings:
    """Get cached application settings."""
    return AppSettings()
```

**Code Generation Hint**: This pattern will inform settings class structure with comprehensive configuration options.

**Validation**: Settings must include all necessary configuration options and proper environment variable support.

### Application Configuration
```python
# In cream_api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .settings import get_settings
from .db import init_db

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    await init_db()
    yield
    # Shutdown
    # Cleanup code here

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Code Generation Hint**: This pattern will inform FastAPI application configuration with proper middleware and lifespan management.

**Validation**: Application configuration must include proper middleware, lifespan management, and CORS settings.

## 3. Testing FastAPI Applications

### Test Application Setup
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from ..main import app
from ..db import get_async_db
from ..models import Base

# Test database
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture
async def async_test_db():
    """Create test database session."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def test_app(async_test_db: AsyncSession):
    """Create a test FastAPI application."""
    async def override_get_async_db():
        yield async_test_db

    app.dependency_overrides[get_async_db] = override_get_async_db
    return app

@pytest.fixture
def client(test_app):
    """Create test client."""
    return TestClient(test_app)
```

**Code Generation Hint**: This pattern will inform FastAPI testing setup with proper database fixtures and dependency overrides.

**Validation**: Test setup must include proper database fixtures, dependency overrides, and test client creation.

### Endpoint Testing
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_user_success(client: TestClient, async_test_db: AsyncSession):
    """Test successful user retrieval."""
    # Setup test data
    user = User(email="test@example.com", username="testuser")
    async_test_db.add(user)
    await async_test_db.commit()

    # Test endpoint
    response = client.get(f"/users/{user.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"

@pytest.mark.asyncio
async def test_get_user_not_found(client: TestClient):
    """Test user not found error."""
    response = client.get("/users/999")

    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_create_user_success(client: TestClient):
    """Test successful user creation."""
    user_data = {
        "email": "new@example.com",
        "username": "newuser",
        "password": "securepassword"
    }

    response = client.post("/users/", json=user_data)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
```

**Code Generation Hint**: This pattern will inform endpoint testing with comprehensive success and error case coverage.

**Validation**: Endpoint tests must include both success and error cases with proper assertions.

### Background Task Testing
```python
from unittest.mock import patch

@pytest.mark.asyncio
async def test_track_stock_with_background_task(client: TestClient):
    """Test stock tracking with background task."""
    with patch('cream_api.stock_data.api.update_all_tracked_stocks') as mock_task:
        response = client.post("/stock-data/track", json={"symbol": "AAPL"})

        assert response.status_code == 200
        mock_task.assert_called_once()

@pytest.mark.asyncio
async def test_background_task_error_handling(client: TestClient):
    """Test background task error handling."""
    with patch('cream_api.stock_data.api.update_all_tracked_stocks') as mock_task:
        mock_task.side_effect = Exception("Task failed")

        response = client.post("/stock-data/track", json={"symbol": "AAPL"})

        # Should still succeed even if background task fails
        assert response.status_code == 200
```

**Code Generation Hint**: This pattern will inform background task testing with proper mocking and error handling.

**Validation**: Background task tests must include proper mocking and error handling scenarios.

## 4. Pydantic Schema Patterns

### Request/Response Models
```python
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    """Base user model."""
    email: str = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")

class UserCreate(UserBase):
    """User creation model."""
    password: str = Field(..., min_length=8, description="User password")

    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v.lower()

class UserResponse(UserBase):
    """User response model."""
    id: int
    created_at: datetime
    is_active: bool = True

    class Config:
        from_attributes = True

class StockRequestCreate(BaseModel):
    """Stock tracking request model."""
    symbol: str = Field(..., min_length=1, max_length=10, regex=r'^[A-Z]+$')

    @validator('symbol')
    def validate_symbol(cls, v):
        return v.upper()

class StockRequestResponse(BaseModel):
    """Stock tracking response model."""
    id: int
    symbol: str
    is_active: bool
    last_pull_date: Optional[datetime] = None

    class Config:
        from_attributes = True
```

**Code Generation Hint**: This pattern will inform Pydantic model structure with proper validation and configuration.

**Validation**: Pydantic models must include proper field validation, descriptions, and ORM compatibility.

### Error Response Models
```python
from pydantic import BaseModel
from typing import Optional, Any

class ErrorResponse(BaseModel):
    """Standard error response model."""
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ValidationErrorResponse(BaseModel):
    """Validation error response model."""
    detail: list[dict[str, Any]]
    error_code: str = "VALIDATION_ERROR"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

**Code Generation Hint**: This pattern will inform error response model structure for consistent error handling.

**Validation**: Error response models must include proper error details and timestamps.

## 5. Dependency Injection Patterns

### Database Dependencies
```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_async_db

async def get_current_user(
    db: AsyncSession = Depends(get_async_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """Get current authenticated user."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require admin privileges."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user
```

**Code Generation Hint**: This pattern will inform dependency injection implementation for authentication and authorization.

**Validation**: Dependencies must include proper error handling and type hints.

### Service Dependencies
```python
from typing import Annotated

# Service dependency
async def get_stock_service(
    db: AsyncSession = Depends(get_async_db)
) -> StockService:
    """Get stock service instance."""
    return StockService(db)

# Use in endpoints
@router.get("/stocks/{symbol}")
async def get_stock(
    symbol: str,
    stock_service: Annotated[StockService, Depends(get_stock_service)]
) -> StockResponse:
    """Get stock data using service dependency."""
    return await stock_service.get_stock(symbol)
```

**Code Generation Hint**: This pattern will inform service dependency injection for business logic separation.

**Validation**: Service dependencies must include proper type hints and error handling.

## 6. Middleware and Exception Handling

### Custom Exception Handler
```python
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """Handle validation errors."""
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "error_code": "VALIDATION_ERROR",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

**Code Generation Hint**: This pattern will inform exception handler implementation for consistent error responses.

**Validation**: Exception handlers must include proper logging and consistent error response format.

### Custom Middleware
```python
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class LoggingMiddleware(BaseHTTPMiddleware):
    """Logging middleware for request/response tracking."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Log request
        logger.info(f"Request: {request.method} {request.url}")

        response = await call_next(request)

        # Log response
        process_time = time.time() - start_time
        logger.info(f"Response: {response.status_code} - {process_time:.3f}s")

        return response

# Add middleware to app
app.add_middleware(LoggingMiddleware)
```

**Code Generation Hint**: This pattern will inform custom middleware implementation for logging and monitoring.

**Validation**: Middleware must include proper logging and performance tracking.

## 7. Background Tasks Integration

### Task Definition and Usage
```python
from fastapi import BackgroundTasks
from typing import List

async def send_email_notification(user_id: int, message: str) -> None:
    """Send email notification (background task)."""
    try:
        # Email sending logic here
        logger.info(f"Email sent to user {user_id}: {message}")
    except Exception as e:
        logger.error(f"Failed to send email to user {user_id}: {e}")

async def process_data_batch(data: List[dict]) -> None:
    """Process data batch (background task)."""
    try:
        for item in data:
            await process_single_item(item)
        logger.info(f"Processed {len(data)} items")
    except Exception as e:
        logger.error(f"Failed to process data batch: {e}")

@router.post("/users/{user_id}/notify")
async def notify_user(
    user_id: int,
    message: str,
    background_tasks: BackgroundTasks
) -> dict:
    """Send notification to user with background task."""
    background_tasks.add_task(send_email_notification, user_id, message)

    return {"message": "Notification scheduled"}
```

**Code Generation Hint**: This pattern will inform background task implementation and usage in endpoints.

**Validation**: Background tasks must include proper error handling and logging.

## Implementation Guidelines

### For AI Assistants
1. **Follow this guide** for all FastAPI development
2. **Use async/await** for all route handlers
3. **Include type hints** for all functions and parameters
4. **Use Pydantic models** for request/response validation
5. **Implement proper error handling** with custom exceptions
6. **Write comprehensive tests** for all endpoints
7. **Use dependency injection** for service separation
8. **Include background tasks** for long-running operations

### For Human Developers
1. **Reference this guide** when building FastAPI applications
2. **Use async/await** for better performance
3. **Write comprehensive tests** for all endpoints
4. **Follow established patterns** for consistency
5. **Use Pydantic models** for data validation
6. **Implement proper error handling** and logging
7. **Use dependency injection** for maintainability

## Quality Assurance

### API Quality Standards
- All endpoints must include proper type hints and response models
- Error handling must be comprehensive and consistent
- Async/await must be used for all I/O operations
- Pydantic models must be used for validation
- Background tasks must include proper error handling

### Testing Requirements
- All endpoints must have unit tests
- Tests must cover both success and error cases
- Background tasks must be tested with proper mocking
- Integration tests must include database operations

### Documentation Standards
- All endpoints must include comprehensive docstrings
- API documentation must be generated with OpenAPI
- Examples must be provided for all endpoints
- Error responses must be documented

### Performance Considerations
- Use async/await for all I/O operations
- Implement proper caching strategies
- Use background tasks for long-running operations
- Monitor API performance and response times

---

**AI Quality Checklist**: Before implementing FastAPI endpoints, ensure:
- [x] Async/await is used for all route handlers
- [x] Type hints are included for all functions and parameters
- [x] Pydantic models are used for request/response validation
- [x] Error handling is comprehensive and consistent
- [x] Background tasks are used for long-running operations
- [x] Tests are written for all endpoints
- [x] Documentation is comprehensive and accurate
- [x] Performance considerations are addressed
