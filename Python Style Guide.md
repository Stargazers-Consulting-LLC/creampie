# Python Style Guide

## General Guidelines

1. Follow PEP 8 style guide
2. Use type hints for all function parameters and return values
3. Use docstrings for all modules, classes, and functions
4. Use meaningful variable and function names
5. Keep functions small and focused
6. Use list comprehensions for simple transformations
7. Use generator expressions for large datasets
8. Use context managers for resource management
9. Use dataclasses for data containers
10. Use enums for constants
11. Use os.path for file paths
12. Use the standard `datetime` library for date/time operations
13. Do not use magic numbers that are not 1, 2, -1 or 0.

## Code Organization

1. Group related functionality into modules
2. Use `__init__.py` files to expose public API
3. Never have a circular import
4. Use absolute imports

## Testing

1. Write unit tests for all functions
2. Use pytest for testing
3. Use fixtures for test setup
4. Use parametrize for multiple test cases
5. Use mock for external dependencies

## Error Handling

1. Use custom exceptions for domain-specific errors
2. Use context managers for cleanup
3. Use try/except blocks for expected errors
4. Use raise from for exception chaining
5. Use logging for error tracking

## Performance

1. Use generators for large datasets
2. Use sets for membership testing
3. Use dict.get() for safe access
4. Use list comprehension for simple transformations
5. Use collections.deque for queues

## Security

1. Use secrets module for random values
2. Use hashlib for hashing
3. Use ssl for secure connections
4. Use hmac for message authentication
5. Use cryptography for encryption

## Documentation

1. Use docstrings for all modules, classes, and functions
2. Use type hints for all function parameters and return values
3. Use comments for complex logic
4. Use README.md for project documentation
5. Use CHANGELOG.md for version history

## General Python Style

- Follow PEP 8 guidelines for general Python code style
- Use type hints consistently throughout the codebase
- Keep line length reasonable (aim for under 100 characters)
- Use meaningful variable and function names that are descriptive
- Use `typing.TYPE_CHECKING` when appropriate to avoid circular imports while type checking.

## Project Structure

- Keep related functionality in dedicated modules
- Use `__init__.py` files to mark directories as Python packages
- Separate configuration, database, and application logic into different modules

## FastAPI Specific Guidelines

- Use async/await for route handlers
- Include return type hints for all route handlers
- Group related routes using FastAPI routers
- Use descriptive route paths and HTTP methods
- Document API endpoints with clear docstrings

## Database Guidelines

- Use SQLAlchemy for database operations
- Follow the declarative base pattern for models
- Use type hints for model attributes
- Keep database configuration in a separate module
- Use environment variables for sensitive database credentials
- Avoid the import `from sqlalchemy.orm.decl_api import mapped_column`

## Configuration Management

- Use Pydantic for settings management
- Implement settings as a class inheriting from BaseSettings
- Use environment variables for configuration
- Cache configuration using lru_cache decorator
- Keep configuration logic separate from application code

## Code Organization

- Group imports in the following order:
  1. Standard library imports
  2. Third-party imports
  3. Local application imports
- Separate imports with a blank line between groups
- Use absolute imports for clarity

## Error Handling

- Use explicit error handling with try/except blocks
- Raise specific exceptions with meaningful messages
- Reraise an exception to preserve traceback (`raise from` syntax) when appropriate.
- Validate input data using Pydantic models
- Use type assertions when necessary for type safety

## Documentation

- Include docstrings for all functions and classes
- Document API endpoints with clear descriptions
- Use type hints as a form of documentation
- Comments should ONLY explain "why" something is done, never "what" is done
- If a comment only describes what the code does, it should be removed
- Commented out code should be removed

## Security

- Never hardcode sensitive information
- Use environment variables for secrets
- Implement proper CORS configuration
- Validate all input data
- Use secure database connection strings

## Testing

- Write unit tests for all new functionality
- Use pytest for testing
- Mock external dependencies in tests
- Include both positive and negative test cases

## Best Practices

- Keep functions small and focused
- Use meaningful variable names
- Implement proper error handling
- Use type hints consistently
- Follow the principle of least surprise
- Keep the code DRY (Don't Repeat Yourself)
- Use constants for configuration values
- Implement proper logging

## Example Code Structure

```python
from typing import Any, Dict

from fastapi import FastAPI
from pydantic import BaseModel

# Type definitions
class ResponseModel(BaseModel):
    field: str

# Route handlers
@app.get("/endpoint")
async def handler() -> Dict[str, Any]:
    return {"status": "success"}

# Configuration
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

# Database models
class User(ModelBase):
    __tablename__ = "users"
    id: int = Column(Integer, primary_key=True)
```

This style guide should be used as a reference for maintaining consistency across the codebase and for generating new code that matches the existing patterns and practices.
