# Cream API Style Guide

## General Python Style

- Follow PEP 8 guidelines for general Python code style
- Use type hints consistently throughout the codebase
- Keep line length reasonable (aim for under 100 characters)
- Use meaningful variable and function names that are descriptive
- Use `typing.TYPE_CHECKING` when appropriate to avoid circular imports while type checking.

## Specific Substitutions

- Prefer the 3rd party `whenever` library over the built-in `datetime`

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
- Validate input data using Pydantic models
- Use type assertions when necessary for type safety

## Documentation

- Include docstrings for all functions and classes
- Document API endpoints with clear descriptions
- Use type hints as a form of documentation
- Keep comments focused on explaining "why" rather than "what"
- A comment that only has "what" should not exist.

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
