# Python Style Guide

This style guide outlines the coding standards and best practices for Python development in our project.

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

### Import Organization
- Group imports in the following order:
  1. Standard library imports
  2. Third-party imports
  3. Local application imports
- Separate imports with a blank line between groups
- Remove unused imports to keep the codebase clean
- Use direct access to settings when appropriate instead of creating local variables
- Place `__all__` at the top of a module after imports

### Data Structures and Operations
- Use dataclasses for data containers
- Use enums for constants
- Use list comprehensions for simple transformations
- Use generator expressions for large datasets
- Use sets for membership testing
- Use dict.get() for safe access
- Use collections.deque for queues

### File and Path Handling
- Use os.path for file paths
  - os.path is preferred over pathlib because it works as strings instead of needing to be coerced
- Use the standard `datetime` library for date/time operations
  - Use `datetime.now(datetime.UTC)` instead of `datetime.utcnow()`, which is deprecated
  - This provides better timezone awareness and is the preferred method in modern Python

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

### Package Organization
- Keep related functionality in dedicated modules
- Use `__init__.py` files to mark directories as Python packages
- Separate configuration, database, and application logic into different modules
- Never have circular imports
- Use absolute imports for clarity

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

## 4. Refactoring Guidelines

### Single Responsibility Principle
- Classes should have a single, clear purpose
- Remove functionality that doesn't align with the class's core responsibility
- Rename classes to better reflect their focused responsibility

### Resource Management
- Handle directory creation and management at a higher level
- Data processing classes should not be responsible for ensuring directory existence
- This separation of concerns makes the code more maintainable and testable

### File Processing
- Delegate parsing responsibility to dedicated parser classes
- Keep file movement operations simple and focused
- Consider moving directory structure management to a configuration/setup module

### Future Considerations
- Consider implementing dedicated services for specific functionalities
- Move configuration and setup logic to appropriate modules
- Enhance error handling with specific exception types and logging
- Refactor functions with "and" in their name into separate functions
  - Example: `process_and_validate_data()` should be split into `process_data()` and `validate_data()`
