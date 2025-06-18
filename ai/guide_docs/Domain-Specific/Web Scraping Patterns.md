# Web Scraping Patterns

This guide outlines project-specific patterns for web scraping and data processing, including HTML parsing, background task integration, and file processing patterns specific to the CreamPie project.

## 1. HTML Structure Handling

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

### HTML Parsing Patterns
```python
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

def parse_stock_table(html_content: str) -> list[dict]:
    """Parse stock data from HTML table."""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # Use semantic selectors
        table = soup.find('table', class_='stock-table')
        if not table:
            logger.warning("Stock table not found in HTML")
            return []

        # Parse table structure
        rows = table.find_all('tr')
        if len(rows) < 2:  # Need header + at least one data row
            logger.warning("Insufficient table rows")
            return []

        # Extract headers
        headers = [th.get_text(strip=True) for th in rows[0].find_all('th')]

        # Parse data rows
        data = []
        for row in rows[1:]:
            cells = row.find_all('td')
            if len(cells) == len(headers):
                row_data = {}
                for header, cell in zip(headers, cells):
                    row_data[header] = cell.get_text(strip=True)
                data.append(row_data)

        return data
    except Exception as e:
        logger.error(f"Error parsing HTML: {e}")
        return []
```

## 2. Background Task Integration

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

## 3. Router Organization

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

### Router Configuration
```python
# In main.py
from fastapi import FastAPI
from cream_api.users.routes.auth import router as auth_router
from cream_api.stock_data.api import router as stock_data_router

app = FastAPI(title="Cream API")

# Include routers with prefixes
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(stock_data_router, prefix="/stock-data", tags=["Stock Data"])
```

## 4. Data Ordering and Time Series

### Best Practices
- **Make data ordering explicit**: When dealing with time-series data, always consider the order
- **Add explicit sorting**: Use `sort_values("date")` to ensure consistent data order
- **Document ordering requirements**: Explain why specific ordering is important
- **Test ordering edge cases**: Verify behavior with different data orderings

### Time Series Data Patterns
```python
import pandas as pd
from datetime import datetime

def process_time_series_data(data: list[dict]) -> pd.DataFrame:
    """Process time series data with proper ordering."""
    df = pd.DataFrame(data)

    # Ensure date column exists and is properly formatted
    if 'date' not in df.columns:
        raise ValueError("Date column not found in data")

    # Convert date strings to datetime
    df['date'] = pd.to_datetime(df['date'])

    # Sort by date to ensure chronological order
    df = df.sort_values('date')

    # Reset index after sorting
    df = df.reset_index(drop=True)

    return df
```

### Data Validation Patterns
```python
from pydantic import BaseModel, validator
from datetime import datetime
from typing import List

class StockDataPoint(BaseModel):
    symbol: str
    date: datetime
    price: float

    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v

    @validator('date')
    def validate_date(cls, v):
        if v > datetime.now():
            raise ValueError('Date cannot be in the future')
        return v

class StockDataResponse(BaseModel):
    data: List[StockDataPoint]
    total_count: int
    date_range: str
```

## 5. File Processing Integration

### File Discovery Patterns
```python
import os
import logging

logger = logging.getLogger(__name__)

def discover_html_files(directory: str) -> list[str]:
    """Discover HTML files in directory for processing."""
    try:
        if not os.path.exists(directory):
            logger.warning(f"Directory does not exist: {directory}")
            return []

        # Find all HTML files
        html_files = []
        for filename in os.listdir(directory):
            if filename.endswith('.html'):
                file_path = os.path.join(directory, filename)
                html_files.append(file_path)

        # Validate files are actually HTML
        valid_files = []
        for file_path in html_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(100)  # Read first 100 chars
                    if '<html' in content.lower() or '<!doctype' in content.lower():
                        valid_files.append(file_path)
                    else:
                        logger.warning(f"File {file_path} does not appear to be HTML")
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")

        return valid_files
    except Exception as e:
        logger.error(f"Error discovering files: {e}")
        return []
```

### File Processing Pipeline
```python
async def process_files_pipeline(files: list[str], session: AsyncSession) -> dict:
    """Process multiple files with comprehensive error handling."""
    results = {
        "processed": 0,
        "failed": 0,
        "errors": [],
        "total_files": len(files)
    }

    for file_path in files:
        try:
            # Validate file is HTML
            if not is_valid_html_file(file_path):
                raise ValueError(f"File {file_path} is not a valid HTML file")

            # Process the file
            await process_single_file(file_path, session)
            results["processed"] += 1

        except Exception as e:
            logger.error(f"Failed to process {file_path}: {e}")
            results["failed"] += 1
            results["errors"].append(f"{file_path}: {str(e)}")

    return results
```

## 6. Effective Debugging

### Best Practices
- **Add strategic debug output**: Include logging at key points in data processing pipelines
- **Make data flow visible**: Use debug prints to see actual data rather than making assumptions
- **Log at appropriate levels**: Use debug, info, warning, and error levels appropriately
- **Include context in logs**: Add relevant data to log messages for better debugging

### Debugging Patterns
```python
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

def log_data_processing_step(step: str, data: dict, level: str = "debug"):
    """Log data processing step with structured data."""
    log_entry = {
        "timestamp": datetime.now(datetime.UTC).isoformat(),
        "step": step,
        "data_sample": {k: str(v)[:100] for k, v in data.items()},  # Truncate long values
        "data_keys": list(data.keys())
    }

    log_method = getattr(logger, level)
    log_method(json.dumps(log_entry))

def log_parsing_result(html_file: str, parsed_data: list, success: bool):
    """Log HTML parsing results."""
    log_entry = {
        "file": html_file,
        "success": success,
        "records_parsed": len(parsed_data) if success else 0,
        "timestamp": datetime.now(datetime.UTC).isoformat()
    }

    if success:
        logger.info(json.dumps(log_entry))
    else:
        logger.error(json.dumps(log_entry))
```

## 7. API Response Patterns

### Standardized Response Format
```python
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    message: Optional[str] = None
    error_code: Optional[str] = None

class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    total: int
    page: int
    per_page: int
    total_pages: int
```

### Error Response Patterns
```python
from fastapi import HTTPException, status

class StockDataException(Exception):
    """Base exception for stock data operations."""
    pass

class FileProcessingError(StockDataException):
    """Exception for file processing errors."""
    pass

class DataValidationError(StockDataException):
    """Exception for data validation errors."""
    pass

def handle_stock_data_error(error: StockDataException) -> HTTPException:
    """Convert stock data exceptions to HTTP exceptions."""
    if isinstance(error, FileProcessingError):
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"File processing error: {str(error)}"
        )
    elif isinstance(error, DataValidationError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Data validation error: {str(error)}"
        )
    else:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
```

These patterns are specific to the CreamPie project's web scraping and data processing needs, including HTML parsing, background task management, and file processing workflows.
