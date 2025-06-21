# Database Debugging Guide

This guide covers common database issues and their debugging steps, based on real-world troubleshooting experience.

## Table of Contents

1. [Permission Issues](#permission-issues)
2. [Migration Problems](#migration-problems)
3. [Connection Issues](#connection-issues)
4. [Schema Problems](#schema-problems)
5. [Data Type Issues](#data-type-issues)
6. [Debugging Tools](#debugging-tools)
7. [Emergency Procedures](#emergency-procedures)

## Permission Issues

### Problem: "relation does not exist" but table exists

**Symptoms:**
- Error: `psycopg.errors.UndefinedTable: relation "table_name" does not exist`
- Table exists when checked as postgres user
- Application can't see the table

**Root Cause:**
- User lacks `USAGE` permission on the schema
- User lacks `SELECT` permission on the table
- Tables recreated without proper permissions

**Debugging Steps:**
```bash
# 1. Check if table exists as postgres user
sudo -u postgres psql -d database_name -c "\dt"

# 2. Check table ownership
sudo -u postgres psql -d database_name -c "SELECT tablename, tableowner FROM pg_tables WHERE schemaname = 'public';"

# 3. Check if application user can see tables
psql -U application_user -d database_name -h localhost -c "\dt"

# 4. Check user permissions
sudo -u postgres psql -d database_name -c "\du application_user"
```

**Solution:**
```bash
# Grant schema and table permissions
sudo -u postgres psql -d database_name << 'EOF'
GRANT USAGE ON SCHEMA public TO application_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE table_name TO application_user;
EOF

# Or use the permissions script
sudo ./scripts/grant_table_permissions.sh
```

## Migration Problems

### Problem: Missing migration revision

**Symptoms:**
- Error: `Can't locate revision identified by 'abc123def456'`
- Alembic can't find a specific migration file
- Migration history is out of sync

**Root Cause:**
- Migration files deleted or moved
- Database state doesn't match migration files
- Corrupted migration history

**Debugging Steps:**
```bash
# 1. Check current migration state
cd cream_api && poetry run alembic current

# 2. Check migration history
poetry run alembic history --verbose

# 3. Check what's in alembic_version table
sudo -u postgres psql -d database_name -c "SELECT version_num FROM alembic_version;"

# 4. List migration files
ls -la migrations/versions/
```

**Solutions:**

**Option 1: Reset migration state (Development)**
```bash
# Drop alembic_version table
sudo -u postgres psql -d database_name -c "DROP TABLE IF EXISTS alembic_version;"

# Run migrations from scratch
./scripts/migrate.sh
```

**Option 2: Fix specific revision**
```bash
# Stamp database at a known good revision
poetry run alembic stamp revision_id
```

### Problem: Data type conversion errors

**Symptoms:**
- Error: `column "id" cannot be cast automatically to type uuid`
- Error: `integer out of range`
- Migration fails on column type changes

**Root Cause:**
- PostgreSQL can't automatically convert between incompatible types
- Large numbers exceed column limits

**Solution:**
```bash
# 1. Create a new migration that drops and recreates the table
poetry run alembic revision --autogenerate -m "recreate table with new schema"

# 2. Edit the migration to drop and recreate instead of alter
# Example:
op.drop_table('table_name')
op.create_table('table_name', ...)
```

## Connection Issues

### Problem: Application connects to wrong database

**Symptoms:**
- Tables don't exist in expected database
- Different data than expected
- Connection string issues

**Debugging Steps:**
```bash
# 1. Check connection string
cd cream_api && poetry run python -c "
from cream_api.settings import get_app_settings
print('Connection string:', get_app_settings().get_connection_string())
"

# 2. Check environment variables
echo $DB_NAME
echo $DB_HOST
echo $DB_USER

# 3. Check .env file (if exists)
cat .env
```

**Solution:**
- Set correct environment variables
- Update `.env` file with proper database credentials
- Ensure database exists and is accessible

## Schema Problems

### Problem: Tables in wrong schema

**Symptoms:**
- Tables exist but application can't find them
- Search path issues
- Schema permission problems

**Debugging Steps:**
```bash
# 1. Check search path
sudo -u postgres psql -d database_name -c "SHOW search_path;"

# 2. Check tables in all schemas
sudo -u postgres psql -d database_name -c "\dt *.*"

# 3. Check schema permissions
sudo -u postgres psql -d database_name -c "\dn+"
```

**Solution:**
```bash
# Grant schema permissions
sudo -u postgres psql -d database_name -c "GRANT USAGE ON SCHEMA public TO application_user;"
```

## Data Type Issues

### Problem: Integer overflow

**Symptoms:**
- Error: `integer out of range`
- Large numbers causing database errors
- Stock volume data too large

**Root Cause:**
- Column type too small for data
- PostgreSQL INTEGER limit (2,147,483,647)

**Solution:**
```python
# Change column type in model
from sqlalchemy import BigInteger

class StockData(ModelBase):
    volume: Mapped[int] = mapped_column(BigInteger, nullable=False)
```

## Debugging Tools

### Database Inspection Commands

```bash
# List all tables
sudo -u postgres psql -d database_name -c "\dt"

# Show table structure
sudo -u postgres psql -d database_name -c "\d table_name"

# Check table ownership
sudo -u postgres psql -d database_name -c "SELECT tablename, tableowner FROM pg_tables WHERE schemaname = 'public';"

# Check user permissions
sudo -u postgres psql -d database_name -c "\du"

# Check active connections
sudo -u postgres psql -d database_name -c "SELECT * FROM pg_stat_activity;"
```

### Application Debugging

```bash
# Check connection string
poetry run python -c "from cream_api.settings import get_app_settings; print(get_app_settings().get_connection_string())"

# Test database connection
poetry run python -c "
import asyncio
from cream_api.db import async_engine
async def test():
    async with async_engine.begin() as conn:
        result = await conn.execute('SELECT 1')
        print('Connection successful')
asyncio.run(test())
"

# Run specific tests
poetry run pytest tests/stock_data/test_models.py -v
```

## Emergency Procedures

### Complete Database Reset (Development Only)

```bash
# 1. Drop and recreate database
sudo -u postgres psql -c "DROP DATABASE IF EXISTS cream;"
sudo -u postgres psql -c "CREATE DATABASE cream OWNER creamapp;"

# 2. Reset migration state
cd cream_api
rm -rf migrations/versions/*
poetry run alembic init migrations

# 3. Create initial migration
poetry run alembic revision --autogenerate -m "initial"

# 4. Apply migrations
poetry run alembic upgrade head

# 5. Grant permissions
sudo ./scripts/grant_table_permissions.sh
```

### Quick Permission Fix

```bash
# Grant all necessary permissions
sudo -u postgres psql -d cream << 'EOF'
GRANT USAGE ON SCHEMA public TO creamapp;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO creamapp;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO creamapp;
EOF
```

## Common Error Messages and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `relation "table" does not exist` | Missing permissions or wrong schema | Grant USAGE on schema and SELECT on table |
| `Can't locate revision` | Migration history mismatch | Reset alembic_version table |
| `integer out of range` | Column type too small | Change to BigInteger |
| `cannot be cast automatically` | Incompatible type conversion | Drop and recreate table |
| `permission denied` | User lacks permissions | Grant appropriate permissions |

## Prevention Tips

1. **Always run migrations in order**
2. **Test permissions after schema changes**
3. **Use appropriate data types from the start**
4. **Keep migration files in version control**
5. **Test database operations in development first**
6. **Document database changes**
7. **Use the provided scripts for common operations**

## Scripts Reference

- `./scripts/migrate.sh` - Run migrations
- `./scripts/rollback_migration.sh` - Rollback migrations
- `./scripts/grant_table_permissions.sh` - Fix permissions
- `./scripts/fix_migration_state.sh` - Reset migration state

---

**Remember**: Always backup your database before making schema changes in production!
