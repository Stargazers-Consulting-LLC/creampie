# Database Management Guide

This guide outlines best practices for database management, including SQLAlchemy usage, migrations, and permissions.

## 1. SQLAlchemy Guidelines

### General Guidelines
- Use SQLAlchemy for database operations
- Follow the declarative base pattern for models
- Use type hints for model attributes
- Keep database configuration in a separate module
- Use environment variables for sensitive database credentials
- Avoid the import `from sqlalchemy.orm.decl_api import mapped_column`

## 2. Database Permissions

### Role-Based Approach
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

## 3. Alembic Migrations

### Setup and Configuration
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

### Creating and Managing Migrations
1. Make changes to SQLAlchemy models
2. Run the migration script:
   ```bash
   ./scripts/migrate.sh
   ```
   This will:
   - Check for model changes
   - Create a new migration if needed
   - Apply pending migrations

### Migration Best Practices
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

### Common Migration Tasks

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

### Common Issues and Solutions
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

### Lessons Learned
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
