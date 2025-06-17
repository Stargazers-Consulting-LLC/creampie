# Python Style Guide

This style guide should be used as a reference for maintaining consistency across the codebase and for generating new code that matches the existing patterns and practices.

## 1. Project Structure and Organization

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

### Import Organization
1. Group imports in the following order:
   - Standard library imports
   - Third-party imports
   - Local application imports
2. Separate imports with a blank line between groups
3. Remove unused imports to keep the codebase clean
4. Use direct access to settings when appropriate instead of creating local variables

## 2. Code Style and Best Practices

### General Guidelines
1. Follow PEP 8 style guide
2. Use type hints for all function parameters and return values
   - Use `|` for union types in Python 3.10+
   - Use built-in types (`dict`, `list`, `set`, etc.) instead of `typing.Dict`, `typing.List`, etc.
   - Only import from `typing` for types that don't have built-in equivalents
3. Use docstrings for all modules, classes, and functions
4. Use meaningful variable and function names
5. Keep functions small and focused
6. Do not use magic numbers that are not 1, 2, -1 or 0

### Data Structures and Operations
1. Use dataclasses for data containers
2. Use enums for constants
3. Use list comprehensions for simple transformations
4. Use generator expressions for large datasets
5. Use sets for membership testing
6. Use dict.get() for safe access
7. Use collections.deque for queues

### Resource Management
1. Use context managers for resource management
   ```python
   # Good
   session = aiohttp.ClientSession(
       timeout=timeout,
       headers=headers,
       skip_auto_headers=['Accept-Encoding']
   )
   async with session:
       # use session

   # Avoid
   async with aiohttp.ClientSession(
       timeout=timeout,
       headers=headers,
       skip_auto_headers=['Accept-Encoding']
   ) as session:
       # use session
   ```

### File and Path Handling
1. Use os.path for file paths
2. Use the standard `datetime` library for date/time operations
   - Use `datetime.now(datetime.UTC)` instead of `datetime.utcnow()`, which is deprecated.
   - This provides better timezone awareness and is the preferred method in modern Python

## 3. Database and Migrations

### SQLAlchemy Guidelines
- Use SQLAlchemy for database operations
- Follow the declarative base pattern for models
- Use type hints for model attributes
- Keep database configuration in a separate module
- Use environment variables for sensitive database credentials
- Avoid the import `from sqlalchemy.orm.decl_api import mapped_column`

### Alembic Migrations
1. Python Path and Imports
   - Keep path resolution simple and direct
   - Use `os.path` for path manipulation
   - Import all models explicitly in `env.py`
   - Set `target_metadata` to the base model's metadata

2. Model Detection
   - All models must be imported in `env.py`
   - Models must inherit from the correct base class
   - Use proper package structure with `__init__.py` files
   - Avoid over-complicated path resolution

3. Best Practices
   - Run migrations from the correct directory (where `alembic.ini` is located)
   - Use `poetry run` to ensure correct Python environment
   - Check for model changes before applying migrations
   - Keep migration scripts focused and atomic

4. Common Issues
   - Model changes not detected: Check imports and Python path
   - Import errors: Verify package structure and path setup
   - Path resolution: Use simple, direct path manipulation
   - Package structure: Ensure proper `__init__.py` files

## 4. Web Framework (FastAPI)

### Route Handlers
- Use async/await for route handlers
- Include return type hints for all route handlers
- Group related routes using FastAPI routers
- Use descriptive route paths and HTTP methods
- Document API endpoints with clear docstrings

### Configuration
- Use Pydantic for settings management
- Implement settings as a class inheriting from BaseSettings
- Use environment variables for configuration
- Cache configuration using lru_cache decorator
- Keep configuration logic separate from application code

## 5. Error Handling and Security

### Error Handling
1. Use custom exceptions for domain-specific errors
2. Use context managers for cleanup
3. Use try/except blocks for expected errors
4. Use raise from for exception chaining
5. Use logging for error tracking
6. Maintain error handling at the appropriate level
7. Consider implementing more specific exception types
8. Validate input data using Pydantic models
9. Use type assertions when necessary for type safety

### Security
1. Never hardcode sensitive information
2. Use environment variables for secrets
3. Use secrets module for random values
4. Use hashlib for hashing
5. Use ssl for secure connections
6. Use hmac for message authentication
7. Use cryptography for encryption
8. Implement proper CORS configuration
9. Validate all input data
10. Use secure database connection strings

## 6. Testing and Documentation

### Testing
1. Write unit tests for all functions
2. Use pytest for testing
3. Use fixtures for test setup
4. Use parametrize for multiple test cases
5. Use mock for external dependencies
6. Include both positive and negative test cases
7. Mock external dependencies in tests

### Documentation
1. Use docstrings for all modules, classes, and functions
2. Use type hints for all function parameters and return values
3. Use comments for complex logic
4. Use README.md for project documentation
5. Use CHANGELOG.md for version history
6. Keep method documentation accurate and up-to-date
7. Comments should ONLY explain "why" something is done, never "what" is done
8. If a comment only describes what the code does, it should be removed
9. Commented out code should be removed

## 7. Refactoring Guidelines

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
