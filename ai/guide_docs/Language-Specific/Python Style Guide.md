# Python Style Guide

> **For AI Assistants**: This guide outlines coding standards and best practices for Python development. All sections include specific examples, validation rules, and implementation guidance for consistent Python code generation.

## AI Metadata

**Template Version:** 2.0
**AI Processing Level:** High
**Required Context:** Python language features, project architecture, existing codebase
**Validation Required:** Yes
**Code Generation:** Supported

**Dependencies:**
- `../Core%20Principles.md` - Decision-making frameworks
- `../project_context/Common%20Patterns.md` - Project patterns
- `../project_context/Architecture%20Overview.md` - System architecture
- `FastAPI%20Development%20Guide.md` - API development patterns
- `Python%20Testing%20Guide.md` - Testing patterns

**Validation Rules:**
- All code must follow PEP 8 style guidelines
- Type hints must be used for all function parameters and return values
- Docstrings must be included for all modules, classes, and functions
- Import organization must follow established patterns
- Error handling must follow project conventions

## Overview

**Document Purpose:** Python coding standards and best practices for the CreamPie project
**Scope:** All Python code, including backend APIs, data processing, and utilities
**Target Users:** AI assistants and developers writing Python code
**Last Updated:** Current

**AI Context:** This guide provides the foundational Python coding standards that must be followed for all Python code in the project. It ensures consistency, readability, and maintainability across the codebase.

## 1. Code Style and Best Practices

### General Guidelines
- Follow PEP 8 style guide
- Use type hints for all function parameters and return values
  - Use `|` for union types in Python 3.10+
  - Use built-in types (`dict`, `list`, `set`, etc.) instead of `typing.Dict`, `typing.List`, etc.
  - Only import from `typing` for types that don't have built-in equivalents
- Use docstrings for all modules, classes, and functions
- Use meaningful variable and function names
- Keep functions small and focused
- Do not use magic numbers that are not 1, 2, -1 or 0

**Code Generation Hint**: These guidelines will inform all Python code generation and review activities.

**Validation**: All generated code must follow these guidelines without exception.

### Import Organization
- Group imports in the following order:
  1. Standard library imports
  2. Third-party imports
  3. Local application imports
- Separate imports with a blank line between groups
- Remove unused imports to keep the codebase clean
- Use direct access to settings when appropriate instead of creating local variables
- Place `__all__` at the top of a module after imports

**Code Generation Hint**: This organization will inform import structure for all Python modules.

**Validation**: Import organization must follow this exact order and grouping.

### Data Structures and Operations
- Use dataclasses for data containers
- Use enums for constants
- Use list comprehensions for simple transformations
- Use generator expressions for large datasets
- Use sets for membership testing
- Use dict.get() for safe access
- Use collections.deque for queues

**Code Generation Hint**: These patterns will inform data structure selection and usage throughout the codebase.

**Validation**: Data structure usage must be appropriate for the specific use case and performance requirements.

### File and Path Handling
- Use os.path for file paths
  - os.path is preferred over pathlib because it works as strings instead of needing to be coerced
- Use the standard `datetime` library for date/time operations
  - Use `datetime.now(datetime.UTC)` instead of `datetime.utcnow()`, which is deprecated
  - This provides better timezone awareness and is the preferred method in modern Python

**Code Generation Hint**: These patterns will inform file and path handling implementation throughout the project.

**Validation**: File and path handling must use the specified libraries and methods.

### Resource Management
- Split context manager creation into separate statements when the constructor has many parameters or is difficult to read
- Simple context managers with few or no parameters can remain inline
- Factory functions (like `AsyncSessionLocal()`) are simple enough to use inline

```python
# Good - complex constructor with many parameters
session = aiohttp.ClientSession(
    timeout=timeout,
    headers=headers,
    skip_auto_headers=['Accept-Encoding']
)
async with session:
    # use session

# Avoid - complex constructor inline makes it hard to read
async with aiohttp.ClientSession(
    timeout=timeout,
    headers=headers,
    skip_auto_headers=['Accept-Encoding']
) as session:
    # use session

# Good - simple constructor can remain inline
async with ClientSession() as session:
    # use session

# Good - factory functions can remain inline
async with AsyncSessionLocal() as session:
    # use session

# Good - simple context managers with few parameters
with open('file.txt', 'r') as f:
    # use file
```

**Code Generation Hint**: These patterns will inform context manager usage and resource management throughout the codebase.

**Validation**: Context manager usage must follow these readability guidelines.

### Configuration Management
- Load configuration once at module level to avoid redundant calls
- Use module-level variables for configuration that doesn't change during runtime
- Avoid calling configuration functions multiple times in the same module

```python
# Good - load once at module level
config = get_stock_data_config()

def some_function():
    retriever = StockDataRetriever(config=config)  # Use module-level config

# Avoid - loading config multiple times
def some_function():
    config = get_stock_data_config()  # Redundant call
    retriever = StockDataRetriever(config=config)
```

**Code Generation Hint**: This pattern will inform configuration loading and usage throughout the project.

**Validation**: Configuration must be loaded once at module level and reused, not loaded multiple times.

### Constants and Magic Numbers
- Define constants at module level for configuration values
- Use descriptive names for time intervals and other magic numbers
- Group related constants together

```python
# Good - named constants
RETRIEVAL_INTERVAL_SECONDS = 5 * 60
PROCESSING_INTERVAL_SECONDS = 10 * 60

# Avoid - magic numbers in code
await asyncio.sleep(5 * 60)  # What does 300 seconds mean?
```

**Code Generation Hint**: This pattern will inform constant definition and usage throughout the codebase.

**Validation**: Magic numbers must be replaced with named constants unless they are 1, 2, -1, or 0.

## 2. Project Structure and Organization

### Directory Structure
```
cream_api/
├── __init__.py
├── migrations/
│   ├── __init__.py      # Required for proper package structure
│   ├── env.py           # Import all models here
│   └── versions/        # Migration files
├── models/
│   └── __init__.py
└── ...
```

**Code Generation Hint**: This structure will inform package organization and module placement throughout the project.

**Validation**: Directory structure must follow this organization for consistency and maintainability.

### Package Organization
- Keep related functionality in dedicated modules
- Use `__init__.py` files to mark directories as Python packages
- Separate configuration, database, and application logic into different modules
- Never have circular imports
- Use absolute imports for clarity

**Code Generation Hint**: This organization will inform module structure and import patterns throughout the project.

**Validation**: Package organization must avoid circular imports and maintain clear separation of concerns.

## 3. Error Handling and Security

### Error Handling
- Use custom exceptions for domain-specific errors
- Use context managers for cleanup
- Use try/except blocks for expected errors
- Use raise from for exception chaining
- Use logging for error tracking
- Maintain error handling at the appropriate level
- Consider implementing more specific exception types
- Validate input data using Pydantic models
- Use type assertions when necessary for type safety

**Code Generation Hint**: These patterns will inform error handling implementation throughout the codebase.

**Validation**: Error handling must be comprehensive and follow established patterns.

### Security
- Never hardcode sensitive information
- Use environment variables for secrets
- Use secrets module for random values
- Use hashlib for hashing
- Use ssl for secure connections
- Use hmac for message authentication
- Use cryptography for encryption
- Implement proper CORS configuration
- Validate all input data
- Use secure database connection strings

**Code Generation Hint**: These security practices will inform all code generation and review activities.

**Validation**: Security practices must be followed without exception for all sensitive operations.

## 4. Refactoring Guidelines

### Single Responsibility Principle
- Classes should have a single, clear purpose
- Remove functionality that doesn't align with the class's core responsibility
- Rename classes to better reflect their focused responsibility

**Code Generation Hint**: This principle will inform class design and refactoring decisions throughout the project.

**Validation**: Classes must have a single, clear responsibility and be appropriately named.

### Resource Management
- Handle directory creation and management at a higher level
- Data processing classes should not be responsible for ensuring directory existence
- This separation of concerns makes the code more maintainable and testable

**Code Generation Hint**: This pattern will inform resource management and separation of concerns.

**Validation**: Resource management must be handled at appropriate levels with clear separation of concerns.

### File Processing
- Delegate parsing responsibility to dedicated parser classes
- Keep file movement operations simple and focused
- Consider moving directory structure management to a configuration/setup module

**Code Generation Hint**: This pattern will inform file processing architecture and responsibility separation.

**Validation**: File processing must follow established patterns with clear responsibility separation.

### Future Considerations
- Consider implementing dedicated services for specific functionalities
- Move configuration and setup logic to appropriate modules
- Enhance error handling with specific exception types and logging
- Refactor functions with "and" in their name into separate functions
  - Example: `process_and_validate_data()` should be split into `process_data()` and `validate_data()`

**Code Generation Hint**: These considerations will inform future refactoring and improvement decisions.

**Validation**: Future improvements must maintain code quality and follow established patterns.

## 5. Type Hints and Annotations

### Function Type Hints
```python
from typing import Optional, List, Dict, Any
from datetime import datetime

def process_stock_data(
    symbol: str,
    start_date: datetime,
    end_date: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """Process stock data for a given symbol and date range."""
    pass

async def fetch_stock_data(
    symbol: str,
    session: AsyncSession
) -> Optional[StockData]:
    """Fetch stock data from database."""
    pass
```

**Code Generation Hint**: These patterns will inform type hint usage throughout the codebase.

**Validation**: All functions must include proper type hints for parameters and return values.

### Class Type Hints
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class StockData:
    symbol: str
    date: datetime
    price: int
    volume: Optional[int] = None

class StockDataProcessor:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config

    async def process(self, data: List[StockData]) -> bool:
        """Process a list of stock data."""
        pass
```

**Code Generation Hint**: These patterns will inform class type hint usage and dataclass implementation.

**Validation**: All classes must include proper type hints and use dataclasses where appropriate.

## 6. Async/Await Patterns

### Async Function Structure
```python
import asyncio
import aiohttp
from typing import List, Dict, Any

async def fetch_multiple_stocks(
    symbols: List[str],
    session: aiohttp.ClientSession
) -> Dict[str, Any]:
    """Fetch data for multiple stock symbols concurrently."""
    tasks = [
        fetch_single_stock(symbol, session)
        for symbol in symbols
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    return {
        symbol: result
        for symbol, result in zip(symbols, results)
        if not isinstance(result, Exception)
    }

async def fetch_single_stock(
    symbol: str,
    session: aiohttp.ClientSession
) -> Dict[str, Any]:
    """Fetch data for a single stock symbol."""
    try:
        async with session.get(f"/api/stocks/{symbol}") as response:
            if response.status == 200:
                return await response.json()
            else:
                raise ValueError(f"Failed to fetch {symbol}")
    except Exception as e:
        logger.error(f"Error fetching {symbol}: {e}")
        raise
```

**Code Generation Hint**: These patterns will inform async/await implementation throughout the codebase.

**Validation**: Async functions must include proper error handling and follow established patterns.

### Database Operations
```python
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

async def get_stock_data(
    symbol: str,
    session: AsyncSession
) -> Optional[StockData]:
    """Get stock data from database."""
    try:
        result = await session.execute(
            select(StockData).where(StockData.symbol == symbol)
        )
        return result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Database error for {symbol}: {e}")
        raise

async def save_stock_data(
    data: StockData,
    session: AsyncSession
) -> bool:
    """Save stock data to database."""
    try:
        session.add(data)
        await session.commit()
        return True
    except Exception as e:
        await session.rollback()
        logger.error(f"Failed to save stock data: {e}")
        return False
```

**Code Generation Hint**: These patterns will inform database operation implementation throughout the project.

**Validation**: Database operations must include proper error handling, transaction management, and logging.

## 7. Testing Patterns

### Unit Test Structure
```python
import pytest
from unittest.mock import AsyncMock, patch
from typing import List

class TestStockDataProcessor:
    """Test cases for StockDataProcessor."""

    @pytest.fixture
    def processor(self) -> StockDataProcessor:
        """Create processor instance for testing."""
        config = {"test": True, "timeout": 30}
        return StockDataProcessor(config)

    @pytest.fixture
    def sample_data(self) -> List[StockData]:
        """Create sample stock data for testing."""
        return [
            StockData(symbol="AAPL", date=datetime.now(), price=15000),
            StockData(symbol="GOOGL", date=datetime.now(), price=25000)
        ]

    @pytest.mark.asyncio
    async def test_process_data_success(
        self,
        processor: StockDataProcessor,
        sample_data: List[StockData]
    ) -> None:
        """Test successful data processing."""
        with patch.object(processor, '_validate_data') as mock_validate:
            mock_validate.return_value = True

            result = await processor.process_data(sample_data)

            assert result is True
            mock_validate.assert_called_once_with(sample_data)

    @pytest.mark.asyncio
    async def test_process_data_validation_failure(
        self,
        processor: StockDataProcessor,
        sample_data: List[StockData]
    ) -> None:
        """Test data processing with validation failure."""
        with patch.object(processor, '_validate_data') as mock_validate:
            mock_validate.return_value = False

            result = await processor.process_data(sample_data)

            assert result is False
```

**Code Generation Hint**: These patterns will inform unit test structure and implementation throughout the project.

**Validation**: Unit tests must include proper fixtures, async testing, and comprehensive error case coverage.

## 8. Documentation Patterns

### Module Docstrings
```python
"""
Stock Data Processing Module

This module provides functionality for retrieving, processing, and storing
stock market data from various sources. It includes data validation,
transformation, and database operations.

Key Components:
- StockDataRetriever: Handles data retrieval from external APIs
- StockDataProcessor: Processes and validates stock data
- StockDataLoader: Manages database operations for stock data

Dependencies:
- aiohttp: For async HTTP requests
- sqlalchemy: For database operations
- pydantic: For data validation

Example Usage:
    processor = StockDataProcessor(config)
    data = await processor.process_symbol("AAPL")
"""

import asyncio
import logging
from typing import List, Dict, Any
```

**Code Generation Hint**: These patterns will inform module documentation throughout the project.

**Validation**: All modules must include comprehensive docstrings with purpose, components, and usage examples.

### Function Docstrings
```python
async def process_stock_data(
    symbol: str,
    start_date: datetime,
    end_date: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """
    Process stock data for a given symbol and date range.

    Args:
        symbol: Stock symbol (e.g., 'AAPL', 'GOOGL')
        start_date: Start date for data retrieval
        end_date: End date for data retrieval (defaults to current date)

    Returns:
        List of processed stock data dictionaries

    Raises:
        ValueError: If symbol is invalid or date range is invalid
        ConnectionError: If unable to connect to data source

    Example:
        data = await process_stock_data("AAPL", datetime(2024, 1, 1))
    """
    pass
```

**Code Generation Hint**: These patterns will inform function documentation throughout the project.

**Validation**: All functions must include comprehensive docstrings with parameters, return values, exceptions, and examples.

## Implementation Guidelines

### For AI Assistants
1. **Follow this guide** for all Python code generation
2. **Use type hints** for all functions and classes
3. **Include docstrings** for all modules, classes, and functions
4. **Follow PEP 8** for code formatting and style
5. **Apply error handling** patterns consistently
6. **Use async/await** for I/O operations
7. **Validate inputs** using Pydantic models
8. **Write tests** for all new functionality

### For Human Developers
1. **Reference this guide** when writing Python code
2. **Use type hints** to improve code clarity and IDE support
3. **Write comprehensive docstrings** for maintainability
4. **Follow established patterns** for consistency
5. **Test your code** thoroughly
6. **Review code** against these standards
7. **Suggest improvements** when better patterns are found

## Quality Assurance

### Code Quality Standards
- All code must follow PEP 8 style guidelines
- Type hints must be used consistently
- Docstrings must be comprehensive and accurate
- Error handling must be appropriate and comprehensive
- Security practices must be followed without exception

### Testing Requirements
- All new functionality must include unit tests
- Tests must cover both success and failure cases
- Async functions must be tested with proper async testing
- Mocking must be used appropriately for external dependencies

### Documentation Standards
- All modules must include comprehensive docstrings
- Function docstrings must include parameters, return values, and examples
- Complex logic must be documented with comments
- Architecture decisions must be documented

### Performance Considerations
- Use async/await for I/O operations
- Use appropriate data structures for performance
- Avoid unnecessary object creation
- Profile code when performance issues arise

---

**AI Quality Checklist**: Before generating Python code, ensure:
- [x] Code follows PEP 8 style guidelines
- [x] Type hints are used for all functions and classes
- [x] Docstrings are comprehensive and accurate
- [x] Error handling follows established patterns
- [x] Security practices are implemented
- [x] Async/await is used for I/O operations
- [x] Input validation is implemented
- [x] Tests are included for new functionality
