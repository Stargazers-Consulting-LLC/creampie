# Common Patterns

This document outlines the common patterns and conventions used throughout the CreamPie project, helping AI assistants understand established code patterns and make consistent suggestions.

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

### Configuration Pattern
```python
# Load configuration once at module level
config = get_module_config()

def some_function():
    # Use module-level config instead of loading again
    processor = DataProcessor(config=config)
```

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

## Database Patterns

### Session Management
```python
async with AsyncSessionLocal() as session:
    async with session.begin():
        # Database operations
        session.add(model)
        await session.commit()
```

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

### Task Scheduling
```python
# In main.py or appropriate startup location
from .background_tasks import schedule_periodic_task

def startup_event():
    # Schedule background tasks
    schedule_periodic_task(process_stock_data, interval_seconds=300)
```

## Testing Patterns

### Test Structure
```python
import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import StockData
from ..processor import StockDataProcessor

class TestStockDataProcessor:
    """Test class for StockDataProcessor."""

    @pytest.fixture
    async def processor(self):
        """Create processor instance for testing."""
        config = {"test": True}
        return StockDataProcessor(config)

    @pytest.fixture
    async def mock_session(self):
        """Create mock database session."""
        session = AsyncMock(spec=AsyncSession)
        return session

    async def test_process_file_success(self, processor, mock_session):
        """Test successful file processing."""
        # Arrange
        test_file = "test_file.html"

        # Act
        result = await processor.process_file(test_file, mock_session)

        # Assert
        assert result is not None
        mock_session.add.assert_called()
        mock_session.commit.assert_called()

    async def test_process_file_not_found(self, processor, mock_session):
        """Test file not found error handling."""
        # Arrange
        non_existent_file = "non_existent.html"

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            await processor.process_file(non_existent_file, mock_session)
```

### Fixture Pattern
```python
@pytest.fixture
def sample_stock_data():
    """Sample stock data for testing."""
    return {
        "symbol": "AAPL",
        "date": "2024-01-01",
        "price": 15000  # $150.00 in cents
    }

@pytest.fixture
def sample_html_file(tmp_path):
    """Create a sample HTML file for testing."""
    html_content = """
    <html>
        <body>
            <div class="price">$150.00</div>
        </body>
    </html>
    """
    file_path = os.path.join(tmp_path, "test.html")
    with open(file_path, 'w') as f:
        f.write(html_content)
    return file_path
```

## Frontend Patterns

### React Component
```typescript
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface StockDataProps {
  symbol: string;
  onRefresh?: () => void;
}

export const StockDataCard: React.FC<StockDataProps> = ({
  symbol,
  onRefresh
}) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/stock-data/${symbol}`);
      if (!response.ok) {
        throw new Error('Failed to fetch data');
      }
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [symbol]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>{symbol} Stock Data</CardTitle>
      </CardHeader>
      <CardContent>
        {loading && <div>Loading...</div>}
        {error && <div className="text-red-500">{error}</div>}
        {data && (
          <div>
            <p>Price: ${(data.price / 100).toFixed(2)}</p>
            <p>Date: {new Date(data.date).toLocaleDateString()}</p>
          </div>
        )}
        <Button onClick={fetchData} disabled={loading}>
          Refresh
        </Button>
      </CardContent>
    </Card>
  );
};
```

### Custom Hook
```typescript
import { useState, useEffect } from 'react';

interface UseApiOptions {
  immediate?: boolean;
  onSuccess?: (data: any) => void;
  onError?: (error: string) => void;
}

export const useApi = <T>(
  url: string,
  options: UseApiOptions = {}
) => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error('API request failed');
      }
      const result = await response.json();
      setData(result);
      options.onSuccess?.(result);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      options.onError?.(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (options.immediate !== false) {
      fetchData();
    }
  }, [url]);

  return { data, loading, error, refetch: fetchData };
};
```

## File Processing Patterns

### File Discovery
```python
import os

def discover_files(directory: str, pattern: str = "*.html") -> list[str]:
    """Discover files matching pattern in directory."""
    try:
        if not os.path.exists(directory):
            logger.warning(f"Directory does not exist: {directory}")
            return []

        files = []
        for filename in os.listdir(directory):
            if filename.endswith('.html'):
                file_path = os.path.join(directory, filename)
                files.append(file_path)

        return files
    except Exception as e:
        logger.error(f"Error discovering files: {e}")
        return []
```

### File Processing Pipeline
```python
async def process_files(files: list[str], session: AsyncSession) -> dict:
    """Process multiple files with error handling."""
    results = {
        "processed": 0,
        "failed": 0,
        "errors": []
    }

    for file_path in files:
        try:
            await process_single_file(file_path, session)
            results["processed"] += 1
        except Exception as e:
            logger.error(f"Failed to process {file_path}: {e}")
            results["failed"] += 1
            results["errors"].append(f"{file_path}: {str(e)}")

    return results
```

## Logging Patterns

### Structured Logging
```python
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

def log_operation(operation: str, details: dict, level: str = "info"):
    """Log operation with structured details."""
    log_entry = {
        "timestamp": datetime.now(datetime.UTC).isoformat(),
        "operation": operation,
        "details": details
    }

    log_method = getattr(logger, level)
    log_method(json.dumps(log_entry))
```

### Error Logging
```python
def log_error(operation: str, error: Exception, context: dict = None):
    """Log error with context."""
    error_details = {
        "operation": operation,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context or {}
    }

    logger.error(json.dumps(error_details))
```

These patterns ensure consistency across the codebase and help AI assistants make suggestions that align with established conventions.
