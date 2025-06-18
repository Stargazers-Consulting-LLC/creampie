# Database Management Guide

> **For AI Assistants**: This guide outlines best practices for database management, including SQLAlchemy usage, migrations, and permissions. All patterns include validation rules and implementation guidance for robust database operations.

## AI Metadata

**Template Version:** 2.0
**AI Processing Level:** High
**Required Context:** SQLAlchemy, Alembic, PostgreSQL, database design, migrations
**Validation Required:** Yes
**Code Generation:** Supported

**Dependencies:**
- `../Core%20Principles.md` - Decision-making frameworks
- `../Language-Specific/Python%20Style%20Guide.md` - Python implementation patterns
- `../Language-Specific/Python%20Testing%20Guide.md` - Database testing patterns
- `../../project_context/Architecture%20Overview.md` - System architecture
- `../../project_context/Common%20Patterns.md` - Project-specific patterns

**Validation Rules:**
- All database operations must use proper session management
- Migrations must be atomic and reversible
- Model imports must be explicit in env.py
- Database permissions must follow role-based approach
- All models must include proper type hints and validation

## Overview

**Document Purpose:** Database management standards and best practices for the CreamPie project
**Scope:** SQLAlchemy models, Alembic migrations, database permissions, and testing
**Target Users:** AI assistants and developers working with database operations
**Last Updated:** Current

**AI Context:** This guide provides the foundational database patterns that must be followed for all database operations in the project. It ensures data integrity, proper migration management, and secure database access.

## 1. SQLAlchemy Guidelines

### General Guidelines
- Use SQLAlchemy for database operations
- Follow the declarative base pattern for models
- Use type hints for model attributes
- Keep database configuration in a separate module
- Use environment variables for sensitive database credentials
- Avoid the import `from sqlalchemy.orm.decl_api import mapped_column`

**Code Generation Hint**: These guidelines will inform all SQLAlchemy model and operation implementation.

**Validation**: All database models must follow these guidelines and include proper type hints.

### Model Definition Patterns
```python
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Optional
from datetime import datetime

Base = declarative_base()

class AppUser(Base):
    """User model for authentication and session management."""
    __tablename__ = "app_users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    sessions = relationship("AppUserSession", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<AppUser(id={self.id}, email='{self.email}', username='{self.username}')>"

class AppUserSession(Base):
    """User session model for authentication tracking."""
    __tablename__ = "app_user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("app_users.id"), nullable=False)
    session_token = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("AppUser", back_populates="sessions")

    def __repr__(self) -> str:
        return f"<AppUserSession(id={self.id}, user_id={self.user_id}, expires_at='{self.expires_at}')>"

class TrackedStock(Base):
    """Model for tracking stock symbols."""
    __tablename__ = "tracked_stock"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_pull_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    stock_data = relationship("StockData", back_populates="tracked_stock", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<TrackedStock(id={self.id}, symbol='{self.symbol}', is_active={self.is_active})>"

class StockData(Base):
    """Model for storing stock price data."""
    __tablename__ = "stock_data"

    id = Column(Integer, primary_key=True, index=True)
    tracked_stock_id = Column(Integer, ForeignKey("tracked_stock.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    open_price = Column(Float, nullable=True)
    high_price = Column(Float, nullable=True)
    low_price = Column(Float, nullable=True)
    close_price = Column(Float, nullable=False)
    volume = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    tracked_stock = relationship("TrackedStock", back_populates="stock_data")

    def __repr__(self) -> str:
        return f"<StockData(id={self.id}, symbol_id={self.tracked_stock_id}, date='{self.date}', close_price={self.close_price})>"
```

**Code Generation Hint**: This model pattern will inform all SQLAlchemy model implementation with proper relationships and validation.

**Validation**: All models must include proper type hints, relationships, and validation constraints.

### Database Configuration Patterns
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./cream_api.db")
ASYNC_DATABASE_URL = DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://").replace("postgresql://", "postgresql+asyncpg://")

# Sync engine for migrations
engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("DATABASE_ECHO", "false").lower() == "true",
    pool_pre_ping=True,
    pool_recycle=300
)

# Async engine for application
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=os.getenv("DATABASE_ECHO", "false").lower() == "true",
    pool_pre_ping=True,
    pool_recycle=300
)

# Session factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

def get_sync_db():
    """Get sync database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Code Generation Hint**: This configuration pattern will inform all database connection and session management implementation.

**Validation**: All database configuration must include proper connection pooling and session management.

## 2. Database Operations

### CRUD Operation Patterns
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime

class DatabaseOperations:
    """Database operation patterns for common CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user_data: Dict[str, Any]) -> AppUser:
        """Create a new user."""
        try:
            user = AppUser(**user_data)
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except Exception as e:
            await self.session.rollback()
            raise ValueError(f"Failed to create user: {e}")

    async def get_user_by_id(self, user_id: int) -> Optional[AppUser]:
        """Get user by ID."""
        stmt = select(AppUser).where(AppUser.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[AppUser]:
        """Get user by email."""
        stmt = select(AppUser).where(AppUser.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_user(self, user_id: int, update_data: Dict[str, Any]) -> Optional[AppUser]:
        """Update user data."""
        try:
            stmt = update(AppUser).where(AppUser.id == user_id).values(**update_data)
            result = await self.session.execute(stmt)
            await self.session.commit()

            if result.rowcount > 0:
                return await self.get_user_by_id(user_id)
            return None
        except Exception as e:
            await self.session.rollback()
            raise ValueError(f"Failed to update user: {e}")

    async def delete_user(self, user_id: int) -> bool:
        """Delete user by ID."""
        try:
            stmt = delete(AppUser).where(AppUser.id == user_id)
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.rowcount > 0
        except Exception as e:
            await self.session.rollback()
            raise ValueError(f"Failed to delete user: {e}")

    async def get_users_with_sessions(self, limit: int = 10) -> List[AppUser]:
        """Get users with their sessions loaded."""
        stmt = (
            select(AppUser)
            .options(selectinload(AppUser.sessions))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_stock_data_by_symbol(self, symbol: str, limit: int = 100) -> List[StockData]:
        """Get stock data for a specific symbol."""
        stmt = (
            select(StockData)
            .join(TrackedStock)
            .where(TrackedStock.symbol == symbol)
            .order_by(StockData.date.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
```

**Code Generation Hint**: This CRUD pattern will inform all database operation implementation with proper error handling.

**Validation**: All database operations must include proper error handling and transaction management.

### Transaction Management Patterns
```python
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any

@asynccontextmanager
async def database_transaction(session: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
    """Context manager for database transactions."""
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise e

async def execute_in_transaction(session: AsyncSession, operation: callable, *args, **kwargs) -> Any:
    """Execute operation within a transaction."""
    async with database_transaction(session):
        return await operation(*args, **kwargs)

# Usage example
async def create_user_with_session(session: AsyncSession, user_data: Dict[str, Any], session_data: Dict[str, Any]) -> AppUser:
    """Create user and session in a single transaction."""
    async def _create_user_and_session():
        # Create user
        user = AppUser(**user_data)
        session.add(user)
        await session.flush()  # Get user ID

        # Create session
        user_session = AppUserSession(user_id=user.id, **session_data)
        session.add(user_session)

        return user

    return await execute_in_transaction(session, _create_user_and_session)
```

**Code Generation Hint**: This transaction pattern will inform all complex database operation implementation.

**Validation**: All complex operations must use proper transaction management.

## 3. Database Permissions

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

**Code Generation Hint**: This permission pattern will inform all database security implementation.

**Validation**: All database permissions must follow role-based approach for security.

### Permission Management Scripts
```bash
#!/bin/bash
# grant_table_permissions.sh

set -e

DB_NAME="${DB_NAME:-cream_api}"
DB_USER="${DB_USER:-creamapp}"
ROLE_NAME="${ROLE_NAME:-creamapp_role}"

echo "🔐 Setting up database permissions..."

# Create role if it doesn't exist
psql -d "$DB_NAME" -c "
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '$ROLE_NAME') THEN
        CREATE ROLE $ROLE_NAME;
    END IF;
END
\$\$;
"

# Grant permissions on existing tables
psql -d "$DB_NAME" -c "
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $ROLE_NAME;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $ROLE_NAME;
"

# Set default privileges for future tables
psql -d "$DB_NAME" -c "
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL PRIVILEGES ON TABLES TO $ROLE_NAME;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL PRIVILEGES ON SEQUENCES TO $ROLE_NAME;
"

# Grant role to application user
psql -d "$DB_NAME" -c "
GRANT $ROLE_NAME TO $DB_USER;
"

echo "✅ Database permissions configured successfully"
```

**Code Generation Hint**: This script pattern will inform all database permission management implementation.

**Validation**: All permission scripts must include proper error handling and validation.

## 4. Alembic Migrations

### Setup and Configuration
- The project uses Alembic for database migrations
- Configuration is located in `cream_api/migrations/`
- All SQLAlchemy models must be imported in `env.py` for autogenerate feature
- Use `__all__` to explicitly declare model exports for static analysis tools

**Code Generation Hint**: This migration setup will inform all database migration implementation.

**Validation**: All migrations must include proper model imports and configuration.

### Migration Configuration
```python
# cream_api/migrations/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import all models
from cream_api.stock_data.models import StockData, TrackedStock
from cream_api.users.models.app_user import AppUser
from cream_api.users.models.app_user_session import AppUserSession

# Explicit model exports for static analysis
__all__ = [
    "AppUser",
    "AppUserSession",
    "StockData",
    "TrackedStock",
]

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

**Code Generation Hint**: This migration configuration will inform all Alembic setup implementation.

**Validation**: All migration configurations must include proper model imports and metadata setup.

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

**Code Generation Hint**: This migration workflow will inform all database schema change implementation.

**Validation**: All schema changes must go through proper migration workflow.

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

**Code Generation Hint**: This migration pattern will inform all complex migration implementation.

**Validation**: All migrations must consider dependencies and include proper documentation.

### Migration Scripts
```bash
#!/bin/bash
# migrate.sh

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

source "$SCRIPT_DIR/common.sh"

print_status "🔄 Running database migrations..."

pushd "$PROJECT_ROOT/cream_api" > /dev/null

# Check for model changes and create migration if needed
if alembic check; then
    print_status "📝 Creating new migration..."
    alembic revision --autogenerate -m "Auto-generated migration"
fi

# Apply pending migrations
print_status "🚀 Applying migrations..."
alembic upgrade head

popd > /dev/null

print_success "✅ Database migrations completed successfully"
```

**Code Generation Hint**: This migration script will inform all migration automation implementation.

**Validation**: All migration scripts must include proper error handling and status reporting.

## 5. Database Testing

### Test Database Setup
```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

@pytest.fixture
async def test_db_engine():
    """Create test database engine."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        pool_pre_ping=True
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()

@pytest.fixture
async def test_db_session(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    TestingSessionLocal = sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture
async def sample_user(test_db_session: AsyncSession) -> AppUser:
    """Create sample user for testing."""
    user = AppUser(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password"
    )
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)
    return user
```

**Code Generation Hint**: This test setup pattern will inform all database testing implementation.

**Validation**: All database tests must use proper test database setup and cleanup.

## Implementation Guidelines

### For AI Assistants
1. **Follow these patterns** for all database implementation
2. **Use proper session management** with async/await
3. **Include comprehensive error handling** in all operations
4. **Use transactions** for complex operations
5. **Follow migration best practices** for schema changes
6. **Implement proper testing** with isolated test databases
7. **Use role-based permissions** for security
8. **Include proper model relationships** and validation

### For Human Developers
1. **Reference these patterns** when working with databases
2. **Use async operations** for better performance
3. **Follow migration workflow** for schema changes
4. **Test database operations** thoroughly
5. **Use proper error handling** and transactions
6. **Follow security best practices** for permissions
7. **Maintain model relationships** and constraints

## Quality Assurance

### Database Standards
- All models must include proper type hints and validation
- Database operations must use proper session management
- Migrations must be atomic and reversible
- Test databases must be isolated from production
- Permissions must follow role-based approach

### Performance Standards
- Database queries must be optimized and indexed
- Connection pooling must be properly configured
- Transactions must be kept as short as possible
- Bulk operations must be used for large datasets
- Database monitoring must be implemented

### Security Standards
- Database credentials must be stored securely
- Role-based permissions must be implemented
- SQL injection must be prevented through ORM usage
- Database access must be logged and monitored
- Sensitive data must be encrypted

### Maintenance Standards
- Migrations must be tested before deployment
- Database backups must be performed regularly
- Performance must be monitored and optimized
- Schema changes must be documented
- Test data must be kept current and relevant

---

**AI Quality Checklist**: Before implementing database operations, ensure:
- [x] Models include proper type hints and relationships
- [x] Database operations use proper session management
- [x] Error handling is comprehensive and includes rollback
- [x] Migrations are atomic and include proper dependencies
- [x] Test databases are isolated and properly configured
- [x] Permissions follow role-based security approach
- [x] Performance considerations are addressed
- [x] Security measures are implemented
