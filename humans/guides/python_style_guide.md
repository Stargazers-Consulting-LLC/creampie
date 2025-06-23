# Python Style Guide

> This guide provides comprehensive Python coding standards and best practices for the CreamPie project. Use these patterns to ensure consistent, readable, and maintainable Python code.

## Table of Contents

1. [Code Style and Formatting](#code-style-and-formatting)
2. [Project Structure](#project-structure)
3. [Import Organization](#import-organization)
4. [Type Hints](#type-hints)
5. [Documentation](#documentation)
   - [Module Docstrings](#module-docstrings)
   - [Legal Notice Requirements](#legal-notice-requirements)
   - [External Documentation Links](#external-documentation-links)
   - [Function Docstrings](#function-docstrings)
   - [Class Docstrings](#class-docstrings)
6. [Error Handling](#error-handling)
7. [Database Patterns](#database-patterns)
8. [FastAPI Patterns](#fastapi-patterns)
9. [Testing](#testing)
10. [Configuration Management](#configuration-management)
11. [Security Best Practices](#security-best-practices)
12. [Performance Considerations](#performance-considerations)
13. [File Operations](#file-operations)
14. [File Naming Conventions](#file-naming-conventions)
15. [Team Collaboration](#team-collaboration)
16. [Debugging and Troubleshooting](#debugging-and-troubleshooting)

## Code Style and Formatting

### General Guidelines

- **Follow PEP 8** style guide with project-specific modifications
- **Use type hints** for all function parameters and return values
- **Use docstrings** for all modules, classes, and functions
- **Use meaningful variable and function names**
- **Keep functions small and focused** (ideally under 50 lines)
- **Use descriptive names** that clearly indicate purpose
- **Prefer composition over inheritance**

### Line Length and Formatting

- **Long strings** can be broken into multiple lines by wrapping them in parentheses:

```python
long_message = (
    "This is a very long string that spans multiple lines "
    "by being wrapped in parentheses, which is the preferred "
    "way to handle long strings in Python."
)
```

- **Use 120 character line length (configured in pyproject.toml)
- **Break long lines at logical points
- **Use double quotes for strings (configured in ruff)
- **Use 4 spaces for indentation

```python
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException
)

# Use double quotes for strings (configured in ruff)
message = "This is the preferred string style"

# Use 4 spaces for indentation
def example_function():
    if condition:
        do_something()
    else:
        do_something_else()
```

### Variable and Function Naming

```python
# Use snake_case for variables and functions
user_name = "john_doe"
def get_user_by_id(user_id: int) -> User:
    pass

# Use PascalCase for classes
class UserService:
    pass

# Use UPPER_CASE for constants
MAX_RETRY_ATTEMPTS = 3
DEFAULT_TIMEOUT = 30

# Use descriptive names that indicate purpose
# Good
def calculate_total_price_with_tax(items: list[Item]) -> float:
    pass

# Avoid
def calc(items: list) -> float:
    pass
```

## Project Structure

### Directory Organization

- Organize code by feature or domain when possible (e.g., `users/`, `data/`, `api/`).
- Group related modules into packages (folders with `__init__.py`).
- Separate application code, tests, configuration, and documentation:
  - `src/` or main package directory: core application code
  - `tests/`: all test code and fixtures
  - `scripts/`: utility or management scripts
  - `config/` or configuration files at the root
  - `docs/` or `humans/guides/`: documentation and guides
- Use clear, descriptive names for all directories and files.
- Avoid deeply nested directory structures; keep the hierarchy as flat as practical.
- Place reusable utilities or shared code in a `common/` or `utils/` package.
- Keep each module focused on a single responsibility.
- For larger projects, consider splitting into sub-packages by domain or service.
- Always include an `__init__.py` file in each package directory to ensure it is recognized as a Python package.
- Store tests close to the code they test (e.g., `tests/feature/test_feature.py`) or in a top-level `tests/` directory, depending on project size and complexity.
- Place configuration and environment files (e.g., `.env`, `settings.py`, `pyproject.toml`) at the project root.

### Module Organization

Each module should follow this structure:

```python
"""Module docstring explaining the module's purpose.

References:
    - [FastAPI Documentation](https://fastapi.tiangolo.com/)
    - [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
    - [Pydantic Documentation](https://docs.pydantic.dev/)

### Legal
SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

# Standard library imports
import logging
from datetime import datetime
from typing import Annotated

# Third-party imports
from fastapi import APIRouter, Depends
from pydantic import BaseModel

# Local imports
from cream_api.db import get_async_db
from cream_api.settings import get_app_settings

# Module-level constants
DEFAULT_TIMEOUT = 30

# Module-level variables
logger = logging.getLogger(__name__)

# Classes
class ExampleModel(BaseModel):
    """Example model class."""
    pass

# Functions
def example_function() -> None:
    """Example function."""
    pass
```

## Import Organization

### Import Order

1. **Standard library imports**
2. **Third-party imports**
3. **Local application imports**

```python
import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated

from fastapi import FastAPI, APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cream_api.db import get_async_db
from cream_api.settings import get_app_settings
from cream_api.stock_data.models import TrackedStock
```

### Import Guidelines

- **Use absolute imports** for clarity
- **Group imports** with a blank line between groups
- **Remove unused imports** to keep code clean
- **Use specific imports** rather than wildcard imports
- **Use `from` imports** for commonly used items
- **Do not add comments** to delimit import groups - the blank lines provide sufficient visual separation

```python
# Good
from fastapi import APIRouter, Depends
from sqlalchemy import select

# Avoid
from fastapi import *
from sqlalchemy import *

# Avoid unnecessary import grouping comments
# # Standard library imports
# import logging
# # Third-party imports
# from fastapi import APIRouter
```

## Type Hints

### Function Type Hints

```python
from typing import Annotated, Optional
from datetime import datetime

def get_user_by_id(user_id: int) -> Optional[User]:
    """Get user by ID."""
    pass

async def create_user(
    name: str,
    email: str,
    created_at: Annotated[datetime, Field(default_factory=datetime.now)]
) -> User:
    """Create a new user."""
    pass
```

### Variable Type Hints

```python
from typing import List, Dict, Optional

# Simple types
user_id: int = 123
user_name: str = "john_doe"
is_active: bool = True

# Complex types
user_ids: List[int] = [1, 2, 3]
user_data: Dict[str, str] = {"name": "John", "email": "john@example.com"}
optional_user: Optional[User] = None

# Use built-in types for Python 3.9+
user_ids: list[int] = [1, 2, 3]
user_data: dict[str, str] = {"name": "John", "email": "john@example.com"}
```

### Type Hints for FastAPI

```python
from typing import Annotated
from fastapi import Depends

# Dependency injection
async def get_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_async_db)]
) -> User:
    pass

# Request/Response models
class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
```

## Documentation

### Docstrings vs. Comments

- **Docstrings** (`""" ... """`):
  - Used for modules, classes, and functions.
  - Should be **verbose** and describe **WHAT** the code does, its purpose, usage, and any relevant details.
  - Example:
    ```python
    def calculate_total(items: list[Item]) -> float:
        """
        Calculate the total price for a list of items, including tax.

        Args:
            items: List of Item objects.

        Returns:
            The total price as a float.
        """
        ...
    ```

- **Comments** (`# ...`):
  - Used within code to clarify **WHY** something is implemented a certain way, especially if it's not obvious.
  - Should only explain rationale, intent, or non-obvious decisions.
  - Example:
    ```python
    # Use a set for O(1) lookups (performance critical)
    seen_ids = set()
    ```

**Rule of thumb:**
- Use docstrings for documentation and explanation of WHAT the code does.
- Use comments only for explaining WHY the code is written a certain way.

**Avoid useless comments:**
- Comments that just repeat what the code obviously shows
- Comments that label variables, functions, or classes without adding context
- Comments that state the obvious

```python
# ❌ Avoid - Useless comments that just label what's obvious
# Test constants
EXPECTED_STOCK_COUNT = 2

# Database connection
db = get_database()

# Function to calculate total
def calculate_total(items):
    pass

# ✅ Good - Comments that explain WHY or non-obvious decisions
# Use a set for O(1) lookups (performance critical)
seen_ids = set()

# Skip validation for admin users to avoid circular dependency
if user.is_admin:
    return True

# Retry up to 3 times with exponential backoff
for attempt in range(3):
    try:
        result = api_call()
        break
    except TimeoutError:
        if attempt == 2:  # Last attempt
            raise
        time.sleep(2 ** attempt)  # Exponential backoff
```

### Module Docstrings

All file and module level docstrings must include:
1. A clear description of the module's purpose
2. Links to relevant external documentation
3. The required legal notice

```python
"""Stock data processing module.

This module provides functionality for processing and managing stock data,
including data validation, storage, and retrieval operations.

References:
    - [FastAPI Documentation](https://fastapi.tiangolo.com/)
    - [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
    - [Pydantic Documentation](https://docs.pydantic.dev/)
    - [Python Type Hints](https://docs.python.org/3/library/typing.html)

### Legal
SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

import logging
from datetime import datetime
```

### Legal Notice Requirements

All Python files and modules must include the following legal notice in their docstring:

```python
### Legal
SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
```

This notice must be placed at the end of the module docstring, after any references section.

### External Documentation Links

Module docstrings should include relevant external documentation links to help developers understand the technologies and libraries being used. Common references include:

- **[FastAPI](https://fastapi.tiangolo.com/)**
- **[SQLAlchemy](https://docs.sqlalchemy.org/)**
- **[Pydantic](https://docs.pydantic.dev/)**
- **[Python Type Hints](https://docs.python.org/3/library/typing.html)**
- **[Alembic](https://alembic.sqlalchemy.org/)**
- **[Pytest](https://docs.pytest.org/)**
- **[PostgreSQL](https://www.postgresql.org/docs/)**

Include only the references that are actually used in the module.

### Function Docstrings

```python
async def track_stock(
    request: TrackStockRequest,
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> dict:
    """Start tracking a new stock symbol.

    Args:
        request: TrackStockRequest containing the symbol to track
        background_tasks: FastAPI background tasks manager
        db: Database session

    Returns:
        dict: Response indicating the stock is now being tracked

    Raises:
        HTTPException: If there's an error starting tracking
    """
    pass
```

### Class Docstrings

```python
class StockData(ModelBase):
    """Model for storing historical stock data.

    This model represents the core stock data table with OHLCV data
    and supports efficient querying by symbol and date.
    """

    __tablename__ = "stock_data"
```

## Error Handling

### Exception Handling Patterns

```python
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

async def create_stock_data(data: StockDataCreate) -> StockData:
    """Create new stock data with proper error handling."""
    try:
        stock_data = StockData(**data.dict())
        db.add(stock_data)
        await db.commit()
        await db.refresh(stock_data)
        return stock_data
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error creating stock data: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        await db.rollback()
        logger.error(f"Unexpected error creating stock data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### Custom Exceptions

```python
class StockDataError(Exception):
    """Base exception for stock data operations."""
    pass

class StockNotFoundError(StockDataError):
    """Raised when a stock is not found."""
    pass

class InvalidStockSymbolError(StockDataError):
    """Raised when an invalid stock symbol is provided."""
    pass
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

def process_stock_data(symbol: str) -> None:
    """Process stock data with comprehensive logging."""
    logger.info(f"Starting to process stock data for {symbol}")

    try:
        # Process data
        logger.debug(f"Processing data for {symbol}")
        # ... processing logic
        logger.info(f"Successfully processed stock data for {symbol}")
    except Exception as e:
        logger.error(f"Error processing stock data for {symbol}: {e}")
        raise
```

### Error Message Cleaning

For production systems, clean error messages to remove verbose details and reduce log noise:

```python
def clean_error_message(error_msg: str) -> str:
    """Clean error message by removing verbose details."""
    # Remove SQL parameter dumps
    if "%(id_m" in error_msg:
        parts = error_msg.split("%(id_m")
        if len(parts) > 1:
            error_msg = parts[0].strip()

    return error_msg

# Usage in exception handling
try:
    # Database operation
    await db.execute(stmt)
except Exception as e:
    error_msg = clean_error_message(str(e))
    logger.error(f"Database error: {error_msg}")
    raise
```

**Error Message Cleaning Guidelines:**
- Remove SQL parameter dumps that clutter logs
- Keep background URLs and stack traces for debugging
- Maintain essential error information for debugging
- Use consistent error message format across the application
- Consider log storage costs and readability

## Database Patterns

### SQLAlchemy Models

```python
from datetime import UTC, datetime
from sqlalchemy import Boolean, DateTime, Float, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
import uuid

from cream_api.db import ModelBase

class StockData(ModelBase):
    """Model for storing historical stock data."""

    __tablename__ = "stock_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String, nullable=False, index=True)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    adj_close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (UniqueConstraint("symbol", "date", name="uix_symbol_date"),)
```

### Database Operations

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

async def get_stock_data(
    symbol: str,
    db: AsyncSession
) -> list[StockData]:
    """Get stock data for a symbol."""
    stmt = select(StockData).where(StockData.symbol == symbol)
    result = await db.execute(stmt)
    return result.scalars().all()

async def create_stock_data(
    stock_data: StockData,
    db: AsyncSession
) -> StockData:
    """Create new stock data."""
    db.add(stock_data)
    await db.commit()
    await db.refresh(stock_data)
    return stock_data
```

### Database Configuration

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Configuration for database and application settings."""

    # Database configuration
    db_user: str = "creamapp"
    db_host: str = ""
    db_name: str = ""
    db_password: str = ""

    def get_connection_string(self) -> str:
        """Get database connection string."""
        if not self.db_host or not self.db_name:
            return "sqlite+aiosqlite:///:memory:"
        return f"postgresql+psycopg://{self.db_user}:{self.db_password}@{self.db_host}/{self.db_name}"

    model_config = SettingsConfigDict(env_file=".env")
```

## FastAPI Patterns

### Router Organization

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/stock-data", tags=["stock-data"])

class TrackStockRequest(BaseModel):
    """Request model for tracking a new stock."""
    symbol: str = Field(..., min_length=1, description="Stock symbol to track")

@router.post("/track")
async def track_stock(
    request: StockRequestCreate,
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> dict:
    """Start tracking a new stock symbol."""
    pass
```

### Dependency Injection

```python
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from cream_api.db import get_async_db
from cream_api.settings import get_app_settings

async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    settings: Annotated[Settings, Depends(get_app_settings)]
) -> User:
    """Get current authenticated user."""
    pass
```

### Request/Response Models

```python
from pydantic import BaseModel, Field, ConfigDict, model_serializer
from datetime import datetime
from typing import Any

class StockDataCreate(BaseModel):
    """Model for creating stock data."""
    symbol: str = Field(..., min_length=1, max_length=10)
    date: datetime
    open: float = Field(..., gt=0)
    high: float = Field(..., gt=0)
    low: float = Field(..., gt=0)
    close: float = Field(..., gt=0)
    volume: int = Field(..., ge=0)

class StockDataResponse(BaseModel):
    """Model for stock data responses."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    symbol: str
    date: datetime
    close: float
    volume: int

    @model_serializer
    def ser_model(self, info) -> dict[str, Any]:
        """Custom serializer to handle datetime fields."""
        data = self.model_dump()
        # Convert datetime fields to ISO format
        if data.get('date'):
            data['date'] = data['date'].isoformat()
        return data
```

### Pydantic v2 Migration Patterns

**Important**: Always use Pydantic v2 patterns to avoid deprecation warnings and ensure future compatibility.

#### Configuration Patterns

```python
# ✅ Modern Pydantic v2 (Preferred)
from pydantic import BaseModel, ConfigDict

class StockDataResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    symbol: str
    # ... other fields

# ❌ Deprecated Pydantic v1 (Avoid)
class StockDataResponse(BaseModel):
    class Config:
        from_attributes = True

    id: int
    symbol: str
    # ... other fields
```

#### Serialization Patterns

```python
# ✅ Modern Pydantic v2 (Preferred)
from pydantic import BaseModel, ConfigDict, model_serializer
from typing import Any

class StockDataResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    symbol: str
    date: datetime

    @model_serializer
    def ser_model(self, info) -> dict[str, Any]:
        """Custom serializer to handle datetime fields."""
        data = self.model_dump()
        if data.get('date'):
            data['date'] = data['date'].isoformat()
        return data

# ❌ Deprecated Pydantic v1 (Avoid)
class StockDataResponse(BaseModel):
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

#### Model Validation Patterns

```python
# ✅ Modern Pydantic v2 (Preferred)
# For ORM objects
response = StockDataResponse.model_validate(orm_object)

# For dictionaries
response = StockDataResponse.model_validate(data_dict)

# ❌ Deprecated Pydantic v1 (Avoid)
response = StockDataResponse.from_orm(orm_object)
response = StockDataResponse.parse_obj(data_dict)
```

#### Data Export Patterns

```python
# ✅ Modern Pydantic v2 (Preferred)
data_dict = model.model_dump()
json_data = model.model_dump_json()

# ❌ Deprecated Pydantic v1 (Avoid)
data_dict = model.dict()
json_data = model.json()
```

#### Field Validation Patterns

```python
# ✅ Modern Pydantic v2 (Preferred)
from pydantic import BaseModel, Field, field_validator

class StockRequestCreate(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10)

    @field_validator('symbol')
    @classmethod
    def validate_symbol_format(cls, v: str) -> str:
        # Validation logic
        return v.upper()

# ❌ Deprecated Pydantic v1 (Avoid)
from pydantic import BaseModel, Field, validator

class StockRequestCreate(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10)

    @validator('symbol')
    def validate_symbol_format(cls, v: str) -> str:
        # Validation logic
        return v.upper()
```

**Migration Checklist:**
- [ ] Replace `class Config` with `model_config = ConfigDict()`
- [ ] Replace `@validator` with `@field_validator`
- [ ] Replace `from_orm()` with `model_validate()`
- [ ] Replace `dict()` with `model_dump()`
- [ ] Replace `json()` with `model_dump_json()`
- [ ] Replace `json_encoders` with `@model_serializer`
- [ ] Update all imports to include new Pydantic v2 classes

## Testing

### Test Structure

```python
"""Test configuration and fixtures."""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from cream_api.main import app
from cream_api.tests.conftest import async_test_db

class TestStockDataAPI:
    """Test cases for stock data API endpoints."""

    @pytest_asyncio.fixture
    async def test_db(self) -> AsyncSession:
        """Create test database session."""
        async with async_test_db() as session:
            yield session

    async def test_track_stock_success(self, test_db: AsyncSession):
        """Test successful stock tracking."""
        # Test implementation
        pass

    async def test_track_stock_invalid_symbol(self, test_db: AsyncSession):
        """Test stock tracking with invalid symbol."""
        # Test implementation
        pass
```

### Test Fixtures

```python
@pytest.fixture
def test_settings() -> Settings:
    """Test settings with in-memory SQLite database."""
    return Settings(
        db_user="test",
        db_host="localhost",
        db_name="test",
        db_password="test",
    )

@pytest_asyncio.fixture
async def async_test_db(test_settings: Settings) -> AsyncGenerator[AsyncSession, None]:
    """Create an async test database session."""
    # Create SQLite in-memory database
    test_db_url = "sqlite+aiosqlite:///:memory:"
    engine = create_async_engine(test_db_url)

    async with engine.begin() as conn:
        await conn.run_sync(ModelBase.metadata.create_all)

    async with async_sessionmaker(engine)() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(ModelBase.metadata.drop_all)
```

### Test Patterns

```python
import pytest
from unittest.mock import AsyncMock, patch

class TestStockDataService:
    """Test cases for stock data service."""

    @pytest.mark.asyncio
    async def test_process_stock_data_success(self):
        """Test successful stock data processing."""
        with patch.object(self.service, '_validate_data') as mock_validate:
            mock_validate.return_value = True

            result = await self.service.process_data(sample_data)

            assert result is True
            mock_validate.assert_called_once_with(sample_data)

    @pytest.mark.asyncio
    async def test_process_stock_data_validation_failure(self):
        """Test stock data processing with validation failure."""
        with patch.object(self.service, '_validate_data') as mock_validate:
            mock_validate.return_value = False

            result = await self.service.process_data(sample_data)

            assert result is False
```

## Configuration Management

### Settings Pattern

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application configuration settings."""

    # Database settings
    db_user: str = "creamapp"
    db_host: str = ""
    db_name: str = ""
    db_password: str = ""

    # Application settings
    enable_background_tasks: bool = True
    frontend_url: str = ""

    def get_connection_string(self) -> str:
        """Get database connection string."""
        if not self.db_host or not self.db_name:
            return "sqlite+aiosqlite:///:memory:"
        return f"postgresql+psycopg://{self.db_user}:{self.db_password}@{self.db_host}/{self.db_name}"

    model_config = SettingsConfigDict(env_file=".env")
```

### Environment Variables

```python
# .env file
DB_USER=creamapp
DB_HOST=localhost
DB_NAME=creamdb
DB_PASSWORD=secure_password
ENABLE_BACKGROUND_TASKS=true
FRONTEND_URL=http://localhost:5173
```

## Security Best Practices

### Input Validation

```python
from pydantic import BaseModel, Field, validator
import re

class StockSymbolRequest(BaseModel):
    """Request model with input validation."""
    symbol: str = Field(..., min_length=1, max_length=10)

    @validator('symbol')
    def validate_symbol(cls, v):
        """Validate stock symbol format."""
        if not re.match(r'^[A-Z]{1,5}$', v):
            raise ValueError('Symbol must be 1-5 uppercase letters')
        return v.upper()
```

### Authentication and Authorization

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> User:
    """Get current authenticated user."""
    try:
        # Validate JWT token
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user
```

### SQL Injection Prevention

```python
# Use SQLAlchemy ORM (prevents SQL injection)
async def get_stock_by_symbol(symbol: str, db: AsyncSession) -> StockData:
    """Get stock by symbol using safe ORM query."""
    stmt = select(StockData).where(StockData.symbol == symbol)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

# Avoid raw SQL (unless absolutely necessary)
# BAD: f"SELECT * FROM stocks WHERE symbol = '{symbol}'"
```

### Data Retention Policy

- **Never actually delete data by user request** - use soft deletion with status flags for compliance and recovery purposes
- Implement soft deletion using `is_deleted` or `status` fields instead of DELETE operations
- Always filter out deleted records in user-facing queries
- Maintain data for legal compliance (account recovery, subpoenas, regulatory audits)

## Performance Considerations

### Database Optimization

```python
# Use indexes for frequently queried columns
class StockData(ModelBase):
    __tablename__ = "stock_data"

    symbol: Mapped[str] = mapped_column(String, nullable=False, index=True)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

# Use select() for efficient queries
async def get_recent_stocks(symbol: str, limit: int = 100) -> list[StockData]:
    """Get recent stock data efficiently."""
    stmt = (
        select(StockData)
        .where(StockData.symbol == symbol)
        .order_by(StockData.date.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()
```

### Async/Await Patterns

```python
import asyncio
from typing import List

async def process_multiple_stocks(symbols: List[str]) -> List[dict]:
    """Process multiple stocks concurrently."""
    tasks = [process_single_stock(symbol) for symbol in symbols]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [r for r in results if not isinstance(r, Exception)]

async def process_single_stock(symbol: str) -> dict:
    """Process a single stock."""
    # Async processing logic
    pass
```

### Caching

```python
from functools import lru_cache
from typing import Optional

@lru_cache(maxsize=128)
def get_stock_config(symbol: str) -> Optional[dict]:
    """Get stock configuration with caching."""
    # Expensive operation
    pass
```

### Batch Processing for Large Datasets

When processing large datasets, use batch processing to optimize performance and avoid database limits:

```python
from itertools import batched

async def process_large_dataset(data_list: list[dict]) -> None:
    """Process large dataset in batches for optimal performance."""
    # Process in batches to avoid PostgreSQL parameter limit (65,535 max)
    batch_size = 1000  # 1000 records * 8 parameters = 8000 parameters per batch

    for batch_num, batch in enumerate(batched(data_list, batch_size), 1):
        try:
            # Prepare batch data
            batch_data = [{"field1": item["field1"], "field2": item["field2"]} for item in batch]

            # Execute batch operation
            stmt = pg_insert(Model).values(batch_data)
            await session.execute(stmt)
            await session.commit()

            logger.info(f"Processed batch {batch_num}")
        except Exception as e:
            await session.rollback()
            logger.error(f"Error in batch {batch_num}: {e}")
            raise
```

**Batch Processing Guidelines:**
- Use Python 3.12's `itertools.batched()` for efficient iteration
- Keep batch sizes well under database parameter limits
- Implement per-batch error handling and rollback
- Monitor memory usage during batch processing
- Consider parallel processing for independent batches
- Use appropriate batch sizes based on data characteristics and system resources

## File Operations

### Path Handling

**Use `os.path` functions exclusively, NOT `pathlib`**

#### Preferred Functions
- `os.path.join()` - for path construction
- `os.path.dirname()` - for getting directory name
- `os.path.basename()` - for getting filename
- `os.path.exists()` - for checking if path exists
- `os.path.isfile()` - for checking if path is a file
- `os.path.isdir()` - for checking if path is a directory
- `os.makedirs()` - for creating directories
- `os.path.abspath()` - for getting absolute paths
- `os.path.commonpath()` - for finding common parent directory of multiple paths

#### Avoid
- `pathlib.Path`
- `Path()`
- `pathlib.joinpath()`
- `pathlib.mkdir()`
- **Chained `dirname()` calls** (e.g., `os.path.dirname(os.path.dirname())`)

#### Path Navigation Best Practices

**Use `os.path.abspath()` and string manipulation for multi-level path navigation**

```python
# Good: Use os.path.abspath for clear path navigation
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
scripts_dir = os.path.join(project_root, 'scripts')
config_path = os.path.join(project_root, 'config', 'settings.json')

# Bad: Chained dirname calls are error-prone and hard to read
project_root = os.path.dirname(os.path.dirname(__file__))
scripts_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
```

#### Advanced Path Operations

**Use `os.path.commonpath()` for finding common parent directories**

The [os.path.commonpath()](https://docs.python.org/3/library/os.path.html#os.path.commonpath) function returns the longest common sub-path of multiple pathnames. This is useful for finding the common parent directory of multiple files or directories.

```python
# Find common parent directory of multiple paths
paths = [
    '/home/user/project/src/main.py',
    '/home/user/project/src/utils.py',
    '/home/user/project/tests/test_main.py'
]
common_parent = os.path.commonpath(paths)
# Result: '/home/user/project'

# Useful for determining project root from multiple file locations
project_files = [
    os.path.abspath('src/main.py'),
    os.path.abspath('tests/test_main.py'),
    os.path.abspath('config/settings.py')
]
project_root = os.path.commonpath(project_files)
```

**Note**: `os.path.commonpath()` raises `ValueError` if paths contain both absolute and relative pathnames, if paths are on different drives, or if the paths list is empty.

#### Guidelines
- Use `os.path.abspath()` to get absolute paths from relative ones
- Use `os.path.join()` for path construction
- Define path constants at module level for clarity
- **Avoid chaining multiple `dirname()` calls** - it's error-prone and hard to read
- Use string manipulation with `'..'` for going up directories

#### Examples

```python
# Good examples
os.path.join(dir_path, filename)
os.path.dirname(file_path)
os.makedirs(dir_path, exist_ok=True)
if os.path.exists(file_path):
    pass
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Bad examples
Path(dir_path) / filename
pathlib.Path(file_path).parent
Path(dir_path).mkdir(exist_ok=True)
if Path(file_path).exists():
    pass
project_root = os.path.dirname(os.path.dirname(__file__))  # Chained dirname calls
```

## File Naming Conventions

### Python Files
- Use lowercase with underscores for all Python files
- Example: `main.py`, `stock_data.py`, `user_service.py`
- No spaces, hyphens, or special characters in filenames
- This ensures cross-platform compatibility and consistent imports

### Module Files
- Use descriptive names that indicate the module's purpose
- Example: `api.py`, `models.py`, `config.py`, `tasks.py`
- Keep names short but descriptive

### Test Files
- Prefix test files with `test_`
- Example: `test_api.py`, `test_models.py`, `test_services.py`
- Use descriptive names that indicate what is being tested

### Configuration Files
- Use lowercase with underscores for config files
- Example: `settings.py`, `config.py`, `alembic.ini`
- Be consistent within each project

## Implementation Guidelines

### For Developers
1. **Follow these patterns** for all Python code implementation
2. **Use type hints** for all function parameters and return values
3. **Include comprehensive docstrings** for all modules, classes, and functions
4. **Write tests** for all new functionality
5. **Use proper error handling** with specific exception types
6. **Follow FastAPI best practices** for API development
7. **Use SQLAlchemy ORM** for database operations
8. **Implement proper logging** for debugging and monitoring

### Quality Checklist
Before implementing Python code, ensure:
- [ ] Type hints are used for all functions and variables
- [ ] Docstrings are included for all modules, classes, and functions
- [ ] Module-level docstrings include external documentation links
- [ ] Module-level docstrings include the required legal notice
- [ ] Error handling is implemented with specific exceptions
- [ ] Tests are written for new functionality
- [ ] Code follows PEP 8 style guidelines
- [ ] Imports are properly organized
- [ ] Security best practices are followed
- [ ] Performance considerations are addressed

### Code Review Standards
- **Type Safety**: All code must have proper type hints
- **Documentation**: All public APIs must be documented with external links and legal notices
- **Testing**: All new features must have corresponding tests
- **Error Handling**: Proper exception handling must be implemented
- **Security**: Input validation and authentication must be in place
- **Performance**: Database queries and async operations must be optimized

## Examples

### Complete Module Example

```python
"""Stock data processing module.

This module provides functionality for processing and managing stock data,
including data validation, storage, and retrieval operations.

References:
    - [FastAPI Documentation](https://fastapi.tiangolo.com/)
    - [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
    - [Pydantic Documentation](https://docs.pydantic.dev/)
    - [Python Type Hints](https://docs.python.org/3/library/typing.html)

### Legal
SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

import logging
from datetime import datetime
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, ConfigDict, model_serializer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cream_api.db import get_async_db
from cream_api.stock_data.models import StockData
from cream_api.settings import get_app_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stock-data", tags=["stock-data"])

class StockDataCreate(BaseModel):
    """Model for creating stock data."""
    symbol: str = Field(..., min_length=1, max_length=10)
    date: datetime
    open: float = Field(..., gt=0)
    high: float = Field(..., gt=0)
    low: float = Field(..., gt=0)
    close: float = Field(..., gt=0)
    volume: int = Field(..., ge=0)

class StockDataResponse(BaseModel):
    """Model for stock data responses."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    symbol: str
    date: datetime
    close: float
    volume: int

    @model_serializer
    def ser_model(self, info) -> dict[str, Any]:
        """Custom serializer to handle datetime fields."""
        data = self.model_dump()
        # Convert datetime fields to ISO format
        if data.get('date'):
            data['date'] = data['date'].isoformat()
        return data

@router.post("/", response_model=StockDataResponse)
async def create_stock_data(
    data: StockDataCreate,
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> StockDataResponse:
    """Create new stock data entry.

    Args:
        data: Stock data to create
        db: Database session

    Returns:
        StockDataResponse: Created stock data

    Raises:
        HTTPException: If there's an error creating the data
    """
    try:
        logger.info(f"Creating stock data for {data.symbol}")

        stock_data = StockData(**data.model_dump())
        db.add(stock_data)
        await db.commit()
        await db.refresh(stock_data)

        logger.info(f"Successfully created stock data for {data.symbol}")
        return StockDataResponse.model_validate(stock_data)

    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating stock data for {data.symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create stock data")

@router.get("/{symbol}", response_model=List[StockDataResponse])
async def get_stock_data(
    symbol: str,
    limit: int = 100,
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> List[StockDataResponse]:
    """Get stock data for a symbol.

    Args:
        symbol: Stock symbol to retrieve data for
        limit: Maximum number of records to return
        db: Database session

    Returns:
        List[StockDataResponse]: List of stock data records
    """
    logger.info(f"Retrieving stock data for {symbol}")

    stmt = (
        select(StockData)
        .where(StockData.symbol == symbol.upper())
        .order_by(StockData.date.desc())
        .limit(limit)
    )

    result = await db.execute(stmt)
    stock_data = result.scalars().all()

    logger.info(f"Retrieved {len(stock_data)} records for {symbol}")
    return [StockDataResponse.model_validate(data) for data in stock_data]
```

This style guide provides a comprehensive foundation for writing reliable, maintainable Python code. Follow these patterns consistently to ensure your code is robust, secure, and easy to maintain.

## Team Collaboration

### Document Decisions and Rationale

**Problem**: Team members don't understand why certain decisions were made.

**Solution**: Document important decisions:
- **Why** certain patterns were chosen
- **What** alternatives were considered
- **How** decisions impact future development
- **When** decisions should be revisited

**Key Insight**: Good documentation helps team members make consistent decisions.

### Review Code for Patterns, Not Just Bugs

**Problem**: Code reviews focus only on finding bugs, not improving patterns.

**Solution**: Review for patterns and consistency:
- **Consistency** - Does this follow established patterns?
- **Maintainability** - Is this code easy to understand and modify?
- **Testability** - Is this code easy to test?
- **Performance** - Are there obvious performance issues?

**Key Insight**: Code reviews should improve code quality, not just find bugs.

### Share Knowledge Proactively

**Problem**: Team members learn the same lessons independently.

**Solution**: Share knowledge systematically:
- **Document lessons learned** in guides like this one
- **Share debugging strategies** with the team
- **Create reusable patterns** for common problems
- **Review and update** documentation regularly

**Key Insight**: Shared knowledge improves team efficiency and code quality.

## Debugging and Troubleshooting

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

**Problem**: Making rapid changes without understanding the root cause leads to breaking more functionality.

**Solution**: Pause and analyze before making changes:
1. Understand what the code is actually doing
2. Identify the root cause of the issue
3. Consider the impact of changes on other parts of the system
4. Make targeted, minimal changes
5. Verify the fix doesn't break other functionality

**Key Insight**: Slow down to speed up - understanding the problem saves time in the long run.

### Use Systematic Debugging Approach

**Problem**: Random debugging attempts are inefficient and frustrating.

**Solution**: Use a systematic approach:
1. **Reproduce the issue** - Run the failing code to see the exact error
2. **Understand the context** - What is the code trying to do?
3. **Identify the root cause** - Why is the code failing?
4. **Make minimal changes** - Fix only what's broken
5. **Verify the fix** - Ensure the fix works and doesn't break other functionality

**Key Insight**: Systematic debugging is faster than trial and error.

### Don't Ignore Test Failures

**Problem**: Assuming tests pass just because a script executes leads to false confidence.

**Solution**: Always verify test results:
- **NEVER** assume tests pass just because a script executes
- **ALWAYS** check test result files for actual outcomes
- **ALWAYS** read test failure messages and error details
- **ALWAYS** verify test outcomes through actual result files

**Key Insight**: Test results are the source of truth, not assumptions.

### Keep It Simple

**Problem**: Over-engineering solutions makes code hard to debug and maintain.

**Solution**: Prefer simple solutions:
- Use built-in language features when possible
- Avoid complex abstractions unless necessary
- Keep functions small and focused
- Use clear, descriptive names
- Document non-obvious logic

**Key Insight**: Simple solutions are easier to debug and maintain.

### Work With Frameworks, Not Against Them

**Problem**: Trying to override framework behavior causes conflicts and bugs.

**Solution**: Work with the framework, not against it:
- Use framework features as intended
- Don't override framework behavior unless absolutely necessary
- Leverage framework best practices
- Follow framework conventions

**Key Insight**: Frameworks are designed to solve common problems - use them as intended.
