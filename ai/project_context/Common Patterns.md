# Common Patterns

> **For AI Assistants**: This document outlines established patterns and conventions used throughout the CreamPie project. All sections include specific code examples, validation rules, and implementation guidance for consistent pattern application.

## AI Metadata

**Template Version:** 2.0
**AI Processing Level:** High
**Required Context:** Project architecture, existing codebase, implementation requirements
**Validation Required:** Yes
**Code Generation:** Supported

**Dependencies:**
- `../guide_docs/Core%20Principles.md` - Decision-making frameworks
- `Architecture%20Overview.md` - System architecture
- `Development%20Workflow.md` - Development process
- `../guide_docs/Language-Specific/Python%20Style%20Guide.md` - Python implementation patterns
- `../guide_docs/Language-Specific/FastAPI%20Development%20Guide.md` - API development patterns

**Validation Rules:**
- All patterns must reference actual project structure and files
- Code examples must follow established project conventions
- Pattern application must be consistent across the codebase
- Implementation must align with project architecture
- Error handling must follow established patterns

## Overview

**Document Purpose:** Established patterns and conventions for the CreamPie project
**Scope:** All code organization, database operations, API development, and background tasks
**Target Users:** AI assistants and developers implementing project features
**Last Updated:** Current

**AI Context:** This document provides the foundational patterns that must be followed when implementing any feature in the CreamPie project. It ensures consistency, maintainability, and alignment with the established architecture.

## Code Organization Patterns

### Module Structure
```python
# Standard module organization
"""
Module docstring explaining purpose and usage.
"""

# Imports organized by type
import os
import logging
from typing import Optional

import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession

from .config import get_module_config
from .exceptions import ModuleSpecificException

# Module-level configuration
config = get_module_config()
logger = logging.getLogger(__name__)

# Constants
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3

# Main classes and functions
class MainClass:
    """Primary class for this module."""

    def __init__(self, config: dict):
        self.config = config

    async def main_method(self) -> dict:
        """Main method with proper error handling."""
        try:
            result = await self._internal_method()
            return result
        except Exception as e:
            logger.error(f"Main method failed: {e}")
            raise ModuleSpecificException("User-friendly message") from e

    async def _internal_method(self) -> dict:
        """Internal method for implementation details."""
        pass
```

**Code Generation Hint**: This pattern will inform the structure of all new modules and classes in the project.

**Validation**: Module structure must follow this exact organization with proper imports, configuration, and error handling.

### Configuration Pattern
```python
# Load configuration once at module level
config = get_module_config()

def some_function():
    # Use module-level config instead of loading again
    processor = DataProcessor(config=config)
```

**Code Generation Hint**: This pattern will inform how to handle configuration loading and usage throughout the project.

**Validation**: Configuration must be loaded once at module level and reused, not loaded multiple times.

### Error Handling Pattern
```python
try:
    # Operation that might fail
    result = await some_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    raise CustomException("User-friendly message") from e
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise CustomException("An unexpected error occurred") from e
```

**Code Generation Hint**: This pattern will inform error handling implementation for all async operations and external calls.

**Validation**: Error handling must include specific exception types, proper logging, and user-friendly error messages.

## Database Patterns

### Session Management
```python
async with AsyncSessionLocal() as session:
    async with session.begin():
        # Database operations
        session.add(model)
        await session.commit()
```

**Code Generation Hint**: This pattern will inform database session management for all database operations.

**Validation**: Database sessions must use proper async context managers and transaction management.

### Model Definition
```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class StockData(Base):
    __tablename__ = "stock_data"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    date = Column(DateTime, nullable=False)
    price = Column(Integer, nullable=False)
```

**Code Generation Hint**: This pattern will inform SQLAlchemy model definitions with proper indexing and constraints.

**Validation**: Models must include proper indexes, constraints, and follow naming conventions.

### Migration Pattern
```python
"""Add stock data table

Revision ID: abc123def456
Revises: previous_revision
Create Date: 2024-01-01 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'stock_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('price', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stock_data_symbol'), 'stock_data', ['symbol'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_stock_data_symbol'), table_name='stock_data')
    op.drop_table('stock_data')
```

**Code Generation Hint**: This pattern will inform Alembic migration file structure and database schema changes.

**Validation**: Migrations must include proper upgrade and downgrade functions with descriptive docstrings.

## API Patterns

### FastAPI Endpoint
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..models import StockData
from ..schemas import StockDataResponse

router = APIRouter()

@router.get("/stock-data/{symbol}", response_model=StockDataResponse)
async def get_stock_data(
    symbol: str,
    session: AsyncSession = Depends(get_session)
) -> StockDataResponse:
    """Get stock data for a specific symbol."""
    try:
        # Business logic here
        data = await get_stock_data_from_db(session, symbol)
        return StockDataResponse.from_orm(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get stock data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

**Code Generation Hint**: This pattern will inform FastAPI endpoint implementation with proper error handling and response models.

**Validation**: Endpoints must include proper error handling, logging, and response model validation.

### Pydantic Schema
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class StockDataResponse(BaseModel):
    id: int
    symbol: str = Field(..., description="Stock symbol")
    date: datetime
    price: int = Field(..., description="Price in cents")

    class Config:
        from_attributes = True
```

**Code Generation Hint**: This pattern will inform Pydantic schema definitions with proper field validation and descriptions.

**Validation**: Schemas must include proper field types, descriptions, and configuration for ORM compatibility.

## Background Task Patterns

### Task Definition
```python
from .background_tasks import background_task

@background_task
async def process_stock_data():
    """Background task for processing stock data."""
    try:
        config = get_stock_data_config()
        processor = StockDataProcessor(config)
        await processor.process_all_files()
    except Exception as e:
        logger.error(f"Stock data processing failed: {e}")
        # Don't re-raise - background tasks should handle errors gracefully
```

**Code Generation Hint**: This pattern will inform background task implementation with proper error handling and logging.

**Validation**: Background tasks must handle errors gracefully and not re-raise exceptions.

### Task Scheduling
```python
# In main.py or appropriate startup location
from .background_tasks import schedule_periodic_task

# Schedule periodic tasks
schedule_periodic_task(
    task_name="process_stock_data",
    interval_seconds=300,  # 5 minutes
    task_function=process_stock_data
)
```

**Code Generation Hint**: This pattern will inform how to schedule and configure background tasks.

**Validation**: Task scheduling must include proper intervals and error handling.

## File Processing Patterns

### File Organization
```python
# Standard file organization structure
cream_api/
├── files/
│   ├── raw_responses/      # Raw data files
│   └── parsed_responses/   # Processed data files
├── stock_data/
│   ├── config.py          # Configuration
│   ├── models.py          # Database models
│   ├── retriever.py       # Data retrieval
│   ├── parser.py          # Data parsing
│   ├── loader.py          # Data loading
│   ├── processor.py       # File processing
│   ├── tasks.py           # Background tasks
│   └── api.py             # API endpoints
```

**Code Generation Hint**: This pattern will inform file organization and module structure for new features.

**Validation**: File organization must follow this structure for consistency and maintainability.

### File Processing Workflow
```python
class FileProcessor:
    """Orchestrates file processing workflow."""

    def __init__(self, config: dict):
        self.config = config
        self.parser = DataParser(config)
        self.loader = DataLoader(config)

    async def process_file(self, file_path: str) -> bool:
        """Process a single file through the complete pipeline."""
        try:
            # Parse the file
            data = await self.parser.parse_file(file_path)

            # Load data to database
            await self.loader.load_data(data)

            # Move file to processed directory
            await self._move_to_processed(file_path)

            return True
        except Exception as e:
            logger.error(f"File processing failed for {file_path}: {e}")
            return False
```

**Code Generation Hint**: This pattern will inform file processing workflow implementation with proper error handling.

**Validation**: File processing must include proper error handling, logging, and file movement operations.

## Testing Patterns

### Unit Test Structure
```python
import pytest
from unittest.mock import AsyncMock, patch
from .models import StockData
from .processor import FileProcessor

class TestFileProcessor:
    """Test cases for FileProcessor class."""

    @pytest.fixture
    def processor(self):
        """Create processor instance for testing."""
        config = {"test": True}
        return FileProcessor(config)

    @pytest.mark.asyncio
    async def test_process_file_success(self, processor):
        """Test successful file processing."""
        with patch.object(processor.parser, 'parse_file') as mock_parse:
            mock_parse.return_value = [{"symbol": "AAPL", "price": 150}]

            result = await processor.process_file("test_file.txt")

            assert result is True
            mock_parse.assert_called_once_with("test_file.txt")

    @pytest.mark.asyncio
    async def test_process_file_failure(self, processor):
        """Test file processing failure."""
        with patch.object(processor.parser, 'parse_file') as mock_parse:
            mock_parse.side_effect = Exception("Parse failed")

            result = await processor.process_file("test_file.txt")

            assert result is False
```

**Code Generation Hint**: This pattern will inform unit test structure with proper fixtures and async testing.

**Validation**: Tests must include proper fixtures, async testing, and comprehensive error case coverage.

### Integration Test Structure
```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from .models import StockData
from .api import get_stock_data

@pytest.mark.asyncio
async def test_get_stock_data_integration(async_session: AsyncSession):
    """Test stock data retrieval integration."""
    # Setup test data
    test_data = StockData(
        symbol="AAPL",
        date=datetime.now(),
        price=15000
    )
    async_session.add(test_data)
    await async_session.commit()

    # Test the endpoint
    result = await get_stock_data("AAPL", async_session)

    assert result.symbol == "AAPL"
    assert result.price == 15000
```

**Code Generation Hint**: This pattern will inform integration test structure with database setup and teardown.

**Validation**: Integration tests must include proper database setup, test data creation, and cleanup.

## Configuration Patterns

### Environment-Based Configuration
```python
import os
from pydantic import BaseSettings

class StockDataConfig(BaseSettings):
    """Configuration for stock data processing."""

    # File paths
    raw_responses_dir: str = "cream_api/files/raw_responses"
    parsed_responses_dir: str = "cream_api/files/parsed_responses"

    # HTTP settings
    timeout_seconds: int = 30
    max_retries: int = 3
    retry_delay_seconds: int = 5

    # Processing settings
    batch_size: int = 100
    max_concurrent_files: int = 5

    class Config:
        env_prefix = "STOCK_DATA_"
```

**Code Generation Hint**: This pattern will inform configuration class structure with environment variable support.

**Validation**: Configuration must use Pydantic for validation and support environment variable overrides.

### Configuration Loading
```python
def get_stock_data_config() -> StockDataConfig:
    """Get stock data configuration."""
    return StockDataConfig()

# Load once at module level
config = get_stock_data_config()
```

**Code Generation Hint**: This pattern will inform configuration loading and usage throughout modules.

**Validation**: Configuration must be loaded once at module level and reused, not loaded multiple times.

## Logging Patterns

### Structured Logging
```python
import logging
import json
from datetime import datetime

class StructuredFormatter(logging.Formatter):
    """Structured JSON logging formatter."""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage()
        }

        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)

        return json.dumps(log_entry)

# Configure logging
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(StructuredFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

**Code Generation Hint**: This pattern will inform structured logging implementation with JSON formatting.

**Validation**: Logging must include structured format with timestamps, levels, and contextual information.

### Logging Usage
```python
# Standard logging patterns
logger.info("Processing started", extra={"file_count": 10})
logger.warning("Retry attempt", extra={"attempt": 3, "max_retries": 5})
logger.error("Processing failed", extra={"file": "data.txt", "error": str(e)})
logger.debug("Debug information", extra={"data_size": len(data)})
```

**Code Generation Hint**: This pattern will inform logging usage with proper levels and contextual information.

**Validation**: Logging must use appropriate levels and include relevant contextual information.

## Error Handling Patterns

### Custom Exceptions
```python
class StockDataException(Exception):
    """Base exception for stock data operations."""
    pass

class StockDataRetrievalError(StockDataException):
    """Raised when stock data retrieval fails."""
    pass

class StockDataParsingError(StockDataException):
    """Raised when stock data parsing fails."""
    pass

class StockDataLoadingError(StockDataException):
    """Raised when stock data loading fails."""
    pass
```

**Code Generation Hint**: This pattern will inform custom exception hierarchy for domain-specific error handling.

**Validation**: Custom exceptions must inherit from appropriate base classes and provide meaningful error messages.

### Error Recovery
```python
async def process_with_retry(operation, max_retries: int = 3):
    """Execute operation with retry logic."""
    for attempt in range(max_retries):
        try:
            return await operation()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            logger.warning(f"Attempt {attempt + 1} failed, retrying: {e}")
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

**Code Generation Hint**: This pattern will inform retry logic implementation with exponential backoff.

**Validation**: Retry logic must include proper backoff strategies and maximum retry limits.

## Performance Patterns

### Async Operations
```python
async def process_files_concurrently(files: list[str], max_concurrent: int = 5):
    """Process multiple files concurrently with semaphore limiting."""
    semaphore = asyncio.Semaphore(max_concurrent)

    async def process_single_file(file_path: str):
        async with semaphore:
            return await process_file(file_path)

    tasks = [process_single_file(file) for file in files]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    return results
```

**Code Generation Hint**: This pattern will inform concurrent processing implementation with proper resource limiting.

**Validation**: Concurrent operations must include proper resource limiting and error handling.

### Database Optimization
```python
async def batch_insert_data(session: AsyncSession, data: list[dict]):
    """Insert data in batches for better performance."""
    batch_size = 1000

    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        models = [StockData(**item) for item in batch]
        session.add_all(models)
        await session.commit()
```

**Code Generation Hint**: This pattern will inform batch database operations for improved performance.

**Validation**: Batch operations must include proper batch sizes and transaction management.

## Security Patterns

### Input Validation
```python
from pydantic import BaseModel, validator
import re

class StockSymbolRequest(BaseModel):
    symbol: str

    @validator('symbol')
    def validate_symbol(cls, v):
        if not re.match(r'^[A-Z]{1,10}$', v):
            raise ValueError('Symbol must be 1-10 uppercase letters')
        return v.upper()
```

**Code Generation Hint**: This pattern will inform input validation implementation with Pydantic validators.

**Validation**: Input validation must include proper regex patterns and meaningful error messages.

### Authentication and Authorization
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)):
    """Validate user authentication."""
    try:
        # Validate token and return user
        user = validate_token(token.credentials)
        return user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

async def require_admin(user = Depends(get_current_user)):
    """Require admin privileges."""
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return user
```

**Code Generation Hint**: This pattern will inform authentication and authorization implementation.

**Validation**: Authentication must include proper token validation and role-based access control.

## Implementation Guidelines

### For AI Assistants
1. **Reference this document** for all pattern implementations
2. **Follow established conventions** for consistency
3. **Apply patterns consistently** across similar functionality
4. **Validate implementations** against pattern requirements
5. **Update patterns** when new best practices emerge

### For Human Developers
1. **Follow these patterns** for all new implementations
2. **Reference patterns** when reviewing code
3. **Suggest pattern improvements** when better approaches are found
4. **Maintain consistency** with established conventions
5. **Document deviations** when patterns cannot be followed

## Quality Assurance

### Pattern Compliance
- All implementations must follow established patterns
- Deviations must be justified and documented
- Pattern updates must be reviewed and approved
- Consistency must be maintained across the codebase

### Code Quality
- All code must follow project style guidelines
- Error handling must be comprehensive
- Performance must meet established requirements
- Security must follow established patterns

### Documentation
- All patterns must be documented with examples
- Implementation guidelines must be clear
- Validation rules must be specific
- Updates must be communicated to the team

---

**AI Quality Checklist**: Before implementing patterns, ensure:
- [x] Pattern is appropriate for the specific use case
- [x] Implementation follows established conventions
- [x] Error handling is comprehensive
- [x] Performance requirements are met
- [x] Security patterns are followed
- [x] Code quality standards are maintained
- [x] Documentation is updated
- [x] Tests are implemented
