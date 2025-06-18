# Web Scraping Patterns

> **For AI Assistants**: This guide outlines project-specific patterns for web scraping and data processing, including HTML parsing, background task integration, and file processing patterns specific to the CreamPie project. All patterns include validation rules and implementation guidance.

## AI Metadata

**Template Version:** 2.0
**AI Processing Level:** High
**Required Context:** Web scraping, HTML parsing, async programming, data processing
**Validation Required:** Yes
**Code Generation:** Supported

**Dependencies:**
- `../Core%20Principles.md` - Decision-making frameworks
- `../Language-Specific/Python%20Style%20Guide.md` - Python implementation patterns
- `../Language-Specific/FastAPI%20Development%20Guide.md` - Background task patterns
- `../../project_context/Common%20Patterns.md` - Project-specific patterns
- `../../features/summaries/[COMPLETED]-stock_data_processing_pipeline_summary.md` - Stock data implementation

**Validation Rules:**
- All HTML parsing must use semantic selectors and proper error handling
- Background tasks must include proper lifecycle management
- Data ordering must be explicit and consistent
- Error handling must distinguish between critical and recoverable errors
- All selectors must be documented with reasoning

## Overview

**Document Purpose:** Web scraping and data processing patterns specific to the CreamPie project
**Scope:** HTML parsing, background tasks, data ordering, error handling, and file processing
**Target Users:** AI assistants and developers implementing web scraping functionality
**Last Updated:** Current

**AI Context:** This guide provides the foundational patterns for all web scraping and data processing in the project. It ensures robust, maintainable, and error-resistant scraping implementations.

## 1. HTML Structure Handling

### Best Practices
- **Use proper semantic HTML elements**: Leverage `<thead>`, `<tbody>` when parsing tables
- **Write robust parsers**: Handle standard HTML table structures correctly
- **Avoid assumptions about structure**: Don't assume HTML will always have a specific format
- **Use semantic selectors**: Prefer direct, semantic selectors (e.g., `.table`) over complex ones

**Code Generation Hint**: These practices will inform all HTML parsing implementation throughout the project.

**Validation**: All HTML parsing must follow these practices and include proper error handling.

### CSS Selector Design
- **Keep selectors simple and specific**: Avoid overly complex selectors that are fragile
- **Use direct, semantic selectors**: Prefer `.table` over `.gridLayout > div:nth-child(2)`
- **Make selectors resilient**: Choose selectors that are less likely to break with HTML changes
- **Document selector assumptions**: Explain why specific selectors were chosen

**Code Generation Hint**: This selector strategy will inform all CSS selector design and documentation.

**Validation**: All selectors must be documented with reasoning and tested for resilience.

### HTML Parsing Patterns
```python
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

def parse_stock_table(html_content: str) -> List[Dict[str, str]]:
    """Parse stock data from HTML table.

    Args:
        html_content: Raw HTML content to parse

    Returns:
        List of dictionaries containing parsed stock data

    Raises:
        ValueError: If HTML structure is invalid
        Exception: For other parsing errors
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # Use semantic selectors - prefer direct table selection
        table = soup.find('table', class_='stock-table')
        if not table:
            logger.warning("Stock table not found in HTML")
            return []

        # Parse table structure with proper error handling
        rows = table.find_all('tr')
        if len(rows) < 2:  # Need header + at least one data row
            logger.warning("Insufficient table rows found")
            return []

        # Extract headers with validation
        header_row = rows[0]
        headers = []
        for th in header_row.find_all('th'):
            header_text = th.get_text(strip=True)
            if header_text:  # Only include non-empty headers
                headers.append(header_text)

        if not headers:
            logger.error("No valid headers found in table")
            return []

        # Parse data rows with validation
        data = []
        for row in rows[1:]:
            cells = row.find_all('td')
            if len(cells) == len(headers):
                row_data = {}
                for header, cell in zip(headers, cells):
                    cell_text = cell.get_text(strip=True)
                    row_data[header] = cell_text
                data.append(row_data)
            else:
                logger.warning(f"Row has {len(cells)} cells, expected {len(headers)}")

        logger.info(f"Successfully parsed {len(data)} rows from stock table")
        return data

    except Exception as e:
        logger.error(f"Error parsing HTML: {e}")
        raise ValueError(f"Failed to parse HTML table: {e}")
```

**Code Generation Hint**: This parsing pattern will inform all HTML table parsing implementation with proper error handling and logging.

**Validation**: All HTML parsing must include comprehensive error handling, logging, and data validation.

### Robust Selector Patterns
```python
def find_table_with_fallback(soup: BeautifulSoup, selectors: List[str]) -> Optional[BeautifulSoup]:
    """Find table using multiple selector fallbacks.

    Args:
        soup: BeautifulSoup object
        selectors: List of CSS selectors to try in order

    Returns:
        Table element if found, None otherwise
    """
    for selector in selectors:
        table = soup.select_one(selector)
        if table:
            logger.info(f"Found table using selector: {selector}")
            return table

    logger.warning(f"No table found with any selector: {selectors}")
    return None

# Usage example
def parse_stock_data_robust(html_content: str) -> List[Dict[str, str]]:
    """Parse stock data with multiple selector fallbacks."""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Try multiple selectors in order of preference
    selectors = [
        'table.stock-table',
        'table.data-table',
        'table',
        '.stock-data table'
    ]

    table = find_table_with_fallback(soup, selectors)
    if not table:
        return []

    # Continue with parsing logic...
    return parse_table_data(table)
```

**Code Generation Hint**: This fallback pattern will inform robust selector implementation for handling HTML structure variations.

**Validation**: All selector implementations must include fallback strategies and proper logging.

## 2. Background Task Integration

### Task Organization
- **Keep tasks independent and focused**: Separate different operations into independent tasks
- **Use single responsibility principle**: Each task should have one clear purpose
- **Implement proper task lifecycle**: Create tasks with clear start/stop conditions

**Code Generation Hint**: This task organization will inform all background task implementation and lifecycle management.

**Validation**: All background tasks must follow single responsibility principle and include proper lifecycle management.

### Task Implementation Patterns
```python
import asyncio
import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class TaskLifecycleManager:
    """Manages background task lifecycle and error handling."""

    def __init__(self, task_name: str):
        self.task_name = task_name
        self.is_running = False
        self.last_run = None
        self.error_count = 0
        self.max_errors = 3

    async def run_with_lifecycle(self, task_func, *args, **kwargs):
        """Run task with proper lifecycle management."""
        self.is_running = True
        self.last_run = datetime.utcnow()

        try:
            logger.info(f"Starting {self.task_name}")
            await task_func(*args, **kwargs)
            self.error_count = 0  # Reset error count on success
            logger.info(f"Completed {self.task_name}")

        except Exception as e:
            self.error_count += 1
            logger.error(f"Error in {self.task_name}: {e}")

            if self.error_count >= self.max_errors:
                logger.critical(f"Too many errors in {self.task_name}, stopping task")
                self.is_running = False
                return False

        return True

# Good - independent, focused tasks with lifecycle management
async def run_periodic_updates() -> None:
    """Run periodic updates of tracked stocks."""
    lifecycle_manager = TaskLifecycleManager("stock_updates")

    while lifecycle_manager.is_running:
        try:
            success = await lifecycle_manager.run_with_lifecycle(update_all_tracked_stocks)
            if not success:
                break

        except Exception as e:
            logger.error(f"Critical error in stock updates: {e}")
            break

        await asyncio.sleep(RETRIEVAL_INTERVAL_SECONDS)

async def run_periodic_file_processing() -> None:
    """Run periodic processing of raw HTML files."""
    lifecycle_manager = TaskLifecycleManager("file_processing")

    while lifecycle_manager.is_running:
        try:
            success = await lifecycle_manager.run_with_lifecycle(process_raw_files_task)
            if not success:
                break

        except RuntimeError as e:
            logger.critical(f"Critical error in file processing: {e}")
            break
        except Exception as e:
            logger.error(f"Error in file processing: {e}")
            # Continue on non-critical errors

        await asyncio.sleep(PROCESSING_INTERVAL_SECONDS)
```

**Code Generation Hint**: This lifecycle management pattern will inform all background task implementation with proper error handling and monitoring.

**Validation**: All background tasks must include lifecycle management and proper error handling strategies.

### Error Handling Strategy
- **Distinguish error types**: Use different exception types for different error categories
- **Implement appropriate responses**: Handle critical errors (stop task) and recoverable errors (continue) differently
- **Use proper logging levels**: Log critical errors with `logger.critical()` and regular errors with `logger.error()`
- **Provide clear error context**: Include relevant information in error messages

**Code Generation Hint**: This error handling strategy will inform all background task error handling implementation.

**Validation**: All background tasks must implement proper error categorization and appropriate responses.

### Task Health Monitoring
```python
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Any

@dataclass
class TaskHealth:
    """Task health monitoring data."""
    task_name: str
    is_running: bool
    last_run: Optional[datetime]
    error_count: int
    success_count: int
    avg_duration: float

    def is_healthy(self) -> bool:
        """Check if task is healthy."""
        if not self.is_running:
            return False

        # Check if task has run recently (within expected interval)
        if self.last_run and datetime.utcnow() - self.last_run > timedelta(minutes=30):
            return False

        # Check error rate
        total_runs = self.success_count + self.error_count
        if total_runs > 0 and self.error_count / total_runs > 0.5:
            return False

        return True

class TaskMonitor:
    """Monitor background task health."""

    def __init__(self):
        self.tasks: Dict[str, TaskHealth] = {}

    def register_task(self, task_name: str) -> TaskHealth:
        """Register a new task for monitoring."""
        health = TaskHealth(
            task_name=task_name,
            is_running=True,
            last_run=None,
            error_count=0,
            success_count=0,
            avg_duration=0.0
        )
        self.tasks[task_name] = health
        return health

    def update_task_health(self, task_name: str, success: bool, duration: float):
        """Update task health metrics."""
        if task_name not in self.tasks:
            return

        health = self.tasks[task_name]
        health.last_run = datetime.utcnow()

        if success:
            health.success_count += 1
        else:
            health.error_count += 1

        # Update average duration
        total_runs = health.success_count + health.error_count
        health.avg_duration = (health.avg_duration * (total_runs - 1) + duration) / total_runs

    def get_unhealthy_tasks(self) -> List[str]:
        """Get list of unhealthy tasks."""
        return [name for name, health in self.tasks.items() if not health.is_healthy()]
```

**Code Generation Hint**: This monitoring pattern will inform all background task health monitoring implementation.

**Validation**: All background tasks must include health monitoring and metrics collection.

## 3. Data Ordering and Time Series

### Best Practices
- **Make data ordering explicit**: When dealing with time-series data, always consider the order
- **Add explicit sorting**: Use `sort_values("date")` to ensure consistent data order
- **Document ordering requirements**: Explain why specific ordering is important
- **Test ordering edge cases**: Verify behavior with different data orderings

**Code Generation Hint**: These practices will inform all time series data processing implementation.

**Validation**: All time series data must include explicit ordering and proper validation.

### Time Series Data Patterns
```python
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any

def process_time_series_data(data: List[Dict[str, Any]]) -> pd.DataFrame:
    """Process time series data with proper ordering and validation.

    Args:
        data: List of dictionaries containing time series data

    Returns:
        Processed DataFrame with proper time ordering

    Raises:
        ValueError: If data is invalid or missing required fields
    """
    if not data:
        raise ValueError("No data provided for processing")

    df = pd.DataFrame(data)

    # Validate required columns
    required_columns = ['date', 'symbol']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    # Ensure date column exists and is properly formatted
    try:
        df['date'] = pd.to_datetime(df['date'])
    except Exception as e:
        raise ValueError(f"Invalid date format: {e}")

    # Validate date range
    current_time = pd.Timestamp.now()
    future_dates = df[df['date'] > current_time]
    if not future_dates.empty:
        logger.warning(f"Found {len(future_dates)} records with future dates")
        df = df[df['date'] <= current_time]

    # Sort by date to ensure chronological order
    df = df.sort_values('date')

    # Reset index after sorting
    df = df.reset_index(drop=True)

    # Validate data integrity
    if df.empty:
        raise ValueError("No valid data after processing")

    # Check for duplicate date-symbol combinations
    duplicates = df.duplicated(subset=['date', 'symbol']).sum()
    if duplicates > 0:
        logger.warning(f"Found {duplicates} duplicate date-symbol combinations")
        df = df.drop_duplicates(subset=['date', 'symbol'], keep='last')

    logger.info(f"Processed {len(df)} time series records")
    return df
```

**Code Generation Hint**: This time series pattern will inform all time series data processing with proper validation and ordering.

**Validation**: All time series processing must include date validation, ordering, and duplicate handling.

### Data Validation Patterns
```python
from pydantic import BaseModel, validator, Field
from datetime import datetime
from typing import List, Optional
from enum import Enum

class DataQuality(Enum):
    """Data quality levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class StockDataPoint(BaseModel):
    """Validated stock data point."""
    symbol: str = Field(..., min_length=1, max_length=10, regex=r'^[A-Z]+$')
    date: datetime
    price: float = Field(..., gt=0)
    volume: Optional[int] = Field(None, ge=0)
    quality: DataQuality = DataQuality.MEDIUM

    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        if v > 1000000:  # Reasonable upper limit
            raise ValueError('Price seems unreasonably high')
        return v

    @validator('date')
    def validate_date(cls, v):
        if v > datetime.now():
            raise ValueError('Date cannot be in the future')
        if v < datetime(1990, 1, 1):  # Reasonable lower limit
            raise ValueError('Date seems unreasonably old')
        return v

    @validator('symbol')
    def validate_symbol(cls, v):
        return v.upper()

class StockDataValidator:
    """Validate stock data quality and consistency."""

    def __init__(self):
        self.validation_errors = []

    def validate_dataset(self, data: List[Dict[str, Any]]) -> List[StockDataPoint]:
        """Validate entire dataset."""
        validated_data = []

        for i, item in enumerate(data):
            try:
                validated_item = StockDataPoint(**item)
                validated_data.append(validated_item)
            except Exception as e:
                self.validation_errors.append(f"Row {i}: {e}")
                logger.warning(f"Validation error in row {i}: {e}")

        if self.validation_errors:
            logger.warning(f"Found {len(self.validation_errors)} validation errors")

        return validated_data

    def get_validation_report(self) -> Dict[str, Any]:
        """Get validation report."""
        return {
            "total_errors": len(self.validation_errors),
            "errors": self.validation_errors,
            "error_rate": len(self.validation_errors) / max(len(self.validation_errors), 1)
        }
```

**Code Generation Hint**: This validation pattern will inform all data validation implementation with comprehensive error reporting.

**Validation**: All data validation must include comprehensive error reporting and quality assessment.

## 4. File Processing Patterns

### File Organization
```python
import os
from pathlib import Path
from datetime import datetime
from typing import List, Optional

class FileProcessor:
    """Manages file processing with proper organization and error handling."""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.raw_path = self.base_path / "raw_responses"
        self.parsed_path = self.base_path / "parsed_responses"
        self.processed_path = self.base_path / "processed_data"

        # Ensure directories exist
        for path in [self.raw_path, self.parsed_path, self.processed_path]:
            path.mkdir(parents=True, exist_ok=True)

    def get_raw_files(self, pattern: str = "*.html") -> List[Path]:
        """Get list of raw files to process."""
        return list(self.raw_path.glob(pattern))

    def move_to_processed(self, file_path: Path, success: bool = True) -> None:
        """Move file to processed directory with status indication."""
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return

        # Create processed subdirectory based on success
        status_dir = "success" if success else "failed"
        processed_dir = self.processed_path / status_dir
        processed_dir.mkdir(exist_ok=True)

        # Move file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        new_path = processed_dir / new_name

        try:
            file_path.rename(new_path)
            logger.info(f"Moved {file_path} to {new_path}")
        except Exception as e:
            logger.error(f"Failed to move {file_path}: {e}")

    def save_parsed_data(self, data: List[Dict[str, Any]], filename: str) -> None:
        """Save parsed data to file."""
        import json

        file_path = self.parsed_path / f"{filename}.json"
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            logger.info(f"Saved parsed data to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save parsed data: {e}")
```

**Code Generation Hint**: This file processing pattern will inform all file organization and processing implementation.

**Validation**: All file processing must include proper organization, error handling, and status tracking.

### Batch Processing
```python
import asyncio
from typing import List, Callable, Any

class BatchProcessor:
    """Process files in batches with proper error handling."""

    def __init__(self, batch_size: int = 10, max_workers: int = 5):
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.processed_count = 0
        self.error_count = 0

    async def process_batch(
        self,
        files: List[Path],
        processor_func: Callable[[Path], Any]
    ) -> Dict[str, Any]:
        """Process a batch of files."""
        results = {
            "processed": 0,
            "errors": 0,
            "errors_details": []
        }

        # Process files with semaphore to limit concurrency
        semaphore = asyncio.Semaphore(self.max_workers)

        async def process_single_file(file_path: Path):
            async with semaphore:
                try:
                    await processor_func(file_path)
                    results["processed"] += 1
                    self.processed_count += 1
                except Exception as e:
                    results["errors"] += 1
                    results["errors_details"].append(f"{file_path}: {e}")
                    self.error_count += 1
                    logger.error(f"Error processing {file_path}: {e}")

        # Create tasks for all files
        tasks = [process_single_file(file) for file in files]

        # Execute tasks
        await asyncio.gather(*tasks, return_exceptions=True)

        return results

    async def process_all_files(
        self,
        file_list: List[Path],
        processor_func: Callable[[Path], Any]
    ) -> Dict[str, Any]:
        """Process all files in batches."""
        total_files = len(file_list)
        logger.info(f"Starting batch processing of {total_files} files")

        all_results = {
            "total_files": total_files,
            "total_processed": 0,
            "total_errors": 0,
            "batch_results": []
        }

        # Process in batches
        for i in range(0, total_files, self.batch_size):
            batch = file_list[i:i + self.batch_size]
            batch_num = i // self.batch_size + 1

            logger.info(f"Processing batch {batch_num} ({len(batch)} files)")

            batch_results = await self.process_batch(batch, processor_func)
            all_results["batch_results"].append(batch_results)
            all_results["total_processed"] += batch_results["processed"]
            all_results["total_errors"] += batch_results["errors"]

        logger.info(f"Batch processing completed: {all_results['total_processed']} processed, {all_results['total_errors']} errors")
        return all_results
```

**Code Generation Hint**: This batch processing pattern will inform all batch file processing implementation with proper concurrency control.

**Validation**: All batch processing must include proper concurrency control, error handling, and progress tracking.

## Implementation Guidelines

### For AI Assistants
1. **Follow these patterns** for all web scraping implementation
2. **Use semantic selectors** and document selector reasoning
3. **Implement proper error handling** with error categorization
4. **Include comprehensive logging** at all stages
5. **Validate data quality** and handle edge cases
6. **Use background tasks** for long-running operations
7. **Implement proper file organization** and status tracking
8. **Test with various HTML structures** and error conditions

### For Human Developers
1. **Reference these patterns** when implementing web scraping
2. **Use robust selectors** that can handle HTML changes
3. **Implement comprehensive error handling** and logging
4. **Validate data quality** before processing
5. **Use background tasks** for performance
6. **Organize files properly** with clear status tracking
7. **Test thoroughly** with various scenarios

## Quality Assurance

### Scraping Quality Standards
- All selectors must be documented with reasoning
- Error handling must be comprehensive and categorized
- Data validation must include quality assessment
- File processing must include proper organization

### Performance Standards
- Batch processing must use appropriate concurrency limits
- Background tasks must not block main application flow
- File operations must be efficient and non-blocking
- Memory usage must be optimized for large datasets

### Reliability Standards
- Scraping must handle HTML structure changes gracefully
- Error recovery must be implemented for transient failures
- Data integrity must be maintained throughout processing
- File status must be properly tracked and reported

### Monitoring Standards
- Task health must be monitored continuously
- Error rates must be tracked and reported
- Performance metrics must be collected
- Data quality metrics must be assessed

---

**AI Quality Checklist**: Before implementing web scraping functionality, ensure:
- [x] Selectors are semantic and well-documented
- [x] Error handling is comprehensive and categorized
- [x] Data validation includes quality assessment
- [x] Background tasks include proper lifecycle management
- [x] File processing includes proper organization
- [x] Batch processing includes concurrency control
- [x] Monitoring and health checks are implemented
- [x] Testing covers various scenarios and edge cases
