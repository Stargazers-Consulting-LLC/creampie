# Backend Style Guide

This style guide should be used as a reference for maintaining consistency across the codebase and for generating new code that matches the existing patterns and practices.

## 1. Python Development

### Code Style and Best Practices

1. **General Guidelines**
   - Follow PEP 8 style guide
   - Use type hints for all function parameters and return values
     - Use `|` for union types in Python 3.10+
     - Use built-in types (`dict`, `list`, `set`, etc.) instead of `typing.Dict`, `typing.List`, etc.
     - Only import from `typing` for types that don't have built-in equivalents
   - Use docstrings for all modules, classes, and functions
   - Use meaningful variable and function names
   - Keep functions small and focused
   - Do not use magic numbers that are not 1, 2, -1 or 0

2. **Data Structures and Operations**
   - Use dataclasses for data containers
   - Use enums for constants
   - Use list comprehensions for simple transformations
   - Use generator expressions for large datasets
   - Use sets for membership testing
   - Use dict.get() for safe access
   - Use collections.deque for queues

3. **Resource Management**
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

4. **File and Path Handling**
   - Use os.path for file paths
   - Use the standard `datetime` library for date/time operations
     - Use `datetime.now(datetime.UTC)` instead of `datetime.utcnow()`, which is deprecated
     - This provides better timezone awareness and is the preferred method in modern Python

### Project Structure and Organization

1. **Directory Structure**
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

2. **Package Organization**
   - Keep related functionality in dedicated modules
   - Use `__init__.py` files to mark directories as Python packages
   - Separate configuration, database, and application logic into different modules
   - Never have circular imports
   - Use absolute imports for clarity

3. **Import Organization**
   - Group imports in the following order:
     1. Standard library imports
     2. Third-party imports
     3. Local application imports
   - Separate imports with a blank line between groups
   - Remove unused imports to keep the codebase clean
   - Use direct access to settings when appropriate instead of creating local variables

### Error Handling and Security

1. **Error Handling**
   - Use custom exceptions for domain-specific errors
   - Use context managers for cleanup
   - Use try/except blocks for expected errors
   - Use raise from for exception chaining
   - Use logging for error tracking
   - Maintain error handling at the appropriate level
   - Consider implementing more specific exception types
   - Validate input data using Pydantic models
   - Use type assertions when necessary for type safety

2. **Security**
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

## 2. Database Development

### SQLAlchemy Guidelines
- Use SQLAlchemy for database operations
- Follow the declarative base pattern for models
- Use type hints for model attributes
- Keep database configuration in a separate module
- Use environment variables for sensitive database credentials
- Avoid the import `from sqlalchemy.orm.decl_api import mapped_column`

### Database Permissions
The project uses a role-based approach for database permissions:

1. Create a role with necessary permissions:
   ```sql
   CREATE ROLE creamapp_role;
   GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO creamapp_role;
   GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO creamapp_role;
   ```

2. Grant the role to the application user:
   ```sql
   GRANT creamapp_role TO creamapp;
   ```

3. Set default privileges for future tables:
   ```sql
   ALTER DEFAULT PRIVILEGES IN SCHEMA public
   GRANT ALL PRIVILEGES ON TABLES TO creamapp_role;

   ALTER DEFAULT PRIVILEGES IN SCHEMA public
   GRANT ALL PRIVILEGES ON SEQUENCES TO creamapp_role;
   ```

### Alembic Migrations

#### Setup and Configuration
- The project uses Alembic for database migrations
- Configuration is located in `cream_api/migrations/`
- All SQLAlchemy models must be imported in `env.py` for autogenerate feature
- Use `__all__` to explicitly declare model exports for static analysis tools:

```python
from cream_api.stock_data.models import StockData, TrackedStock
from cream_api.users.models.app_user import AppUser
from cream_api.users.models.app_user_session import AppUserSession

__all__ = [
    "AppUser",
    "AppUserSession",
    "StockData",
    "TrackedStock",
]
```

> **Note**: While `# noqa: F401` comments can be used as an alternative to silence unused import warnings, the `__all__` approach is preferred because it:
> - Makes exports explicit
> - Follows Python's standard module export pattern
> - Is more maintainable and clearer in intent
> - Doesn't require special comments that might be missed

#### Creating and Managing Migrations
1. Make changes to SQLAlchemy models
2. Run the migration script:
   ```bash
   ./scripts/migrate.sh
   ```
   This will:
   - Check for model changes
   - Create a new migration if needed
   - Apply pending migrations

#### Migration Best Practices
1. **Dependencies**: Consider foreign key dependencies when writing migrations:
   ```python
   def upgrade() -> None:
       # Drop tables with foreign key constraints first
       op.drop_table('sessions')  # Has foreign key to app_users
       op.drop_table('app_users')
       # Then drop other tables
       op.drop_table('stock_data')
       op.drop_table('tracked_stock')
   ```

2. **Atomic Changes**: Keep migrations focused and atomic
3. **Documentation**: Add comments explaining complex migrations
4. **Testing**: Test migrations both up and down
5. **Permissions**: Ensure database user has necessary permissions

#### Common Migration Tasks

1. **Downgrading to Base**
   To revert all migrations while keeping migration files:
   ```bash
   cd cream_api && alembic downgrade base
   ```

2. **Checking Migration Status**
   To see current migration state:
   ```bash
   cd cream_api && alembic current
   ```

3. **Creating a New Migration**
   To create a new migration without applying it:
   ```bash
   cd cream_api && alembic revision --autogenerate -m "description"
   ```

#### Common Issues and Solutions
1. **Model Detection**
   - All models must be imported in `env.py`
   - Models must inherit from the correct base class
   - Use proper package structure with `__init__.py` files
   - Avoid over-complicated path resolution

2. **Troubleshooting**
   - Model changes not detected: Check imports and Python path
   - Import errors: Verify package structure and path setup
   - Path resolution: Use simple, direct path manipulation
   - Package structure: Ensure proper `__init__.py` files

#### Lessons Learned
1. **Model Imports**
   - Always import all models in `env.py` to ensure Alembic can detect changes
   - Use `__all__` to explicitly declare model exports
   - Avoid using `# noqa: F401` comments as they can be missed and are less maintainable

2. **Migration Dependencies**
   - Always consider foreign key dependencies when creating migrations
   - Drop tables in the correct order:
     1. Tables with foreign key constraints first
     2. Referenced tables after
     3. Indexes and other objects last

3. **Database Permissions**
   - Ensure the database user has sufficient permissions to create/drop tables
   - Verify permissions on all schemas being modified
   - Use a role-based approach for consistent permissions

4. **Best Practices**
   - Keep migrations atomic and focused on specific changes
   - Document complex migrations with comments explaining the reasoning
   - Test migrations both up and down
   - Consider table dependencies when writing migrations
   - Always import all models in `env.py`

## 3. Tooling and Infrastructure

### Web Framework (FastAPI)

#### Route Handlers
- Use async/await for route handlers
- Include return type hints for all route handlers
- Group related routes using FastAPI routers
- Use descriptive route paths and HTTP methods
- Document API endpoints with clear docstrings

#### Configuration
- Use Pydantic for settings management
- Implement settings as a class inheriting from BaseSettings
- Use environment variables for configuration
- Cache configuration using lru_cache decorator
- Keep configuration logic separate from application code

### Testing and Documentation

#### Testing
1. Write unit tests for all functions
2. Use pytest for testing
3. Use fixtures for test setup
4. Use parametrize for multiple test cases
5. Use mock for external dependencies
6. Include both positive and negative test cases
7. Mock external dependencies in tests

#### FastAPI Testing Best Practices
1. **Test Application Setup**
   ```python
   @pytest.fixture
   def app(async_test_db: AsyncSession):
       """Create a test FastAPI application."""
       app = FastAPI()

       # Override the database dependency
       async def override_get_async_db():
           yield async_test_db

       app.dependency_overrides[get_async_db] = override_get_async_db
       app.include_router(router)
       return app
   ```

2. **Async Database Testing**
   - Use `pytest_asyncio` for async tests
   - Create separate fixtures for sync and async databases
   - Use in-memory SQLite for testing
   - Ensure proper cleanup after tests

3. **Background Task Testing**
   - Mock `BackgroundTasks.add_task` instead of the task function
   - Test both success and error cases
   - Verify task scheduling without executing the task

4. **Error Handling Tests**
   - Test both expected and unexpected errors
   - Verify correct HTTP status codes
   - Check error messages and response structure
   - Test database rollback behavior

5. **Test Isolation**
   - Each test should have its own database session
   - Clean up resources after each test
   - Don't rely on test execution order
   - Use fixtures for shared setup

#### Documentation
1. Use docstrings for all modules, classes, and functions
2. Use type hints for all function parameters and return values
3. Use comments for complex logic
4. Use README.md for project documentation
5. Use CHANGELOG.md for version history
6. Keep method documentation accurate and up-to-date
7. Comments should ONLY explain "why" something is done, never "what" is done
8. If a comment only describes what the code does, it should be removed
9. Commented out code should be removed

### Refactoring Guidelines

#### Single Responsibility Principle
- Classes should have a single, clear purpose
- Remove functionality that doesn't align with the class's core responsibility
- Rename classes to better reflect their focused responsibility

#### Resource Management
- Handle directory creation and management at a higher level
- Data processing classes should not be responsible for ensuring directory existence
- This separation of concerns makes the code more maintainable and testable

#### File Processing
- Delegate parsing responsibility to dedicated parser classes
- Keep file movement operations simple and focused
- Consider moving directory structure management to a configuration/setup module

#### Future Considerations
- Consider implementing dedicated services for specific functionalities
- Move configuration and setup logic to appropriate modules
- Enhance error handling with specific exception types and logging
- Refactor functions with "and" in their name into separate functions
  - Example: `process_and_validate_data()` should be split into `process_data()` and `validate_data()`
