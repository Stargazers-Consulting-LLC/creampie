# Deployment Guide

## Overview

This guide details the deployment process for the stock historical data system. The deployment will:

1. Set up the production environment
2. Configure the database
3. Deploy the application
4. Monitor system health

## Implementation Steps

### 1. Create Deployment Scripts

Create `scripts/deploy.sh`:

```bash
#!/bin/bash

# Exit on error
set -e

# Load environment variables
source .env

# Create virtual environment
poetry install

# Create required directories
mkdir -p cache logs test_data

# Set up database
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f scripts/setup_database.sql

# Run migrations
alembic upgrade head

# Start the application
poetry run python src/main.py
```

Create `scripts/setup_database.sql`:

```sql
-- Create tables if they don't exist
CREATE TABLE IF NOT EXISTS stock_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(10,2) NOT NULL,
    high DECIMAL(10,2) NOT NULL,
    low DECIMAL(10,2) NOT NULL,
    close DECIMAL(10,2) NOT NULL,
    adj_close DECIMAL(10,2) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, date)
);

CREATE TABLE IF NOT EXISTS cache_metadata (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    cache_date DATE NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, cache_date)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_stock_data_symbol ON stock_data(symbol);
CREATE INDEX IF NOT EXISTS idx_stock_data_date ON stock_data(date);
CREATE INDEX IF NOT EXISTS idx_cache_metadata_symbol ON cache_metadata(symbol);
CREATE INDEX IF NOT EXISTS idx_cache_metadata_date ON cache_metadata(cache_date);
```

### 2. Create Environment Configuration

Create `.env.example`:

```ini
# Database settings
DB_HOST=localhost
DB_PORT=5432
DB_NAME=stock_data
DB_USER=postgres
DB_PASSWORD=your_password

# Parser settings
PARSER_USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
PARSER_TIMEOUT=30
PARSER_MAX_RETRIES=3
PARSER_RETRY_DELAY=5

# Cache settings
CACHE_EXPIRATION_DAYS=7
CACHE_MAX_SIZE=1000

# Logging settings
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5
```

### 3. Create Database Migrations

Create `alembic/versions/001_initial.py`:

```python
"""Initial migration

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Any, Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade database schema."""
    # Create stock_data table
    op.create_table(
        'stock_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(length=10), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('open', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('high', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('low', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('close', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('adj_close', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('volume', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('symbol', 'date', name='uq_stock_data_symbol_date')
    )

    # Create cache_metadata table
    op.create_table(
        'cache_metadata',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(length=10), nullable=False),
        sa.Column('cache_date', sa.Date(), nullable=False),
        sa.Column('file_path', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_accessed', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('symbol', 'cache_date', name='uq_cache_metadata_symbol_date')
    )

    # Create indexes
    op.create_index('idx_stock_data_symbol', 'stock_data', ['symbol'])
    op.create_index('idx_stock_data_date', 'stock_data', ['date'])
    op.create_index('idx_cache_metadata_symbol', 'cache_metadata', ['symbol'])
    op.create_index('idx_cache_metadata_date', 'cache_metadata', ['cache_date'])

def downgrade() -> None:
    """Downgrade database schema."""
    # Drop indexes
    op.drop_index('idx_cache_metadata_date')
    op.drop_index('idx_cache_metadata_symbol')
    op.drop_index('idx_stock_data_date')
    op.drop_index('idx_stock_data_symbol')

    # Drop tables
    op.drop_table('cache_metadata')
    op.drop_table('stock_data')
```

### 4. Create Monitoring Script

Create `scripts/monitor.py`:

```python
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict

import psutil
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.models import CacheMetadata, StockData
from config.settings import get_settings

settings = get_settings()

def get_system_stats() -> Dict[str, Any]:
    """Get system statistics."""
    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage("/").percent,
    }

def get_database_stats(db_session: Session) -> Dict[str, Any]:
    """Get database statistics."""
    # Count records
    stock_data_count = db_session.execute(
        select(StockData)
    ).scalar_one_or_none()
    cache_metadata_count = db_session.execute(
        select(CacheMetadata)
    ).scalar_one_or_none()

    # Get latest update
    latest_stock_data = db_session.execute(
        select(StockData).order_by(StockData.updated_at.desc())
    ).scalar_one_or_none()
    latest_cache = db_session.execute(
        select(CacheMetadata).order_by(CacheMetadata.last_accessed.desc())
    ).scalar_one_or_none()

    return {
        "stock_data_count": stock_data_count,
        "cache_metadata_count": cache_metadata_count,
        "latest_stock_update": latest_stock_data.updated_at if latest_stock_data else None,
        "latest_cache_access": latest_cache.last_accessed if latest_cache else None,
    }

def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    cache_dir = settings.CACHE_DIR
    total_files = len(list(cache_dir.glob("*.html")))
    total_size = sum(
        f.stat().st_size for f in cache_dir.glob("*.html")
    )

    return {
        "total_files": total_files,
        "total_size_bytes": total_size,
        "total_size_mb": total_size / (1024 * 1024),
    }

def check_system_health() -> Dict[str, Any]:
    """Check system health."""
    system_stats = get_system_stats()
    database_stats = get_database_stats()
    cache_stats = get_cache_stats()

    # Check for potential issues
    issues = []
    if system_stats["cpu_percent"] > 80:
        issues.append("High CPU usage")
    if system_stats["memory_percent"] > 80:
        issues.append("High memory usage")
    if system_stats["disk_usage"] > 80:
        issues.append("High disk usage")

    return {
        "status": "healthy" if not issues else "unhealthy",
        "issues": issues,
        "system_stats": system_stats,
        "database_stats": database_stats,
        "cache_stats": cache_stats,
        "timestamp": datetime.now(),
    }
```

## Deployment Steps

1. **Environment Setup**

   ```bash
   # Clone repository
   git clone <repository_url>
   cd stock_historical_data

   # Create and activate virtual environment
   poetry install
   poetry shell

   # Copy environment file
   cp .env.example .env
   # Edit .env with your settings
   ```

2. **Database Setup**

   ```bash
   # Create database
   createdb stock_data

   # Run migrations
   alembic upgrade head
   ```

3. **Application Deployment**

   ```bash
   # Make deployment script executable
   chmod +x scripts/deploy.sh

   # Run deployment
   ./scripts/deploy.sh
   ```

4. **Monitoring Setup**
   ```bash
   # Start monitoring
   poetry run python scripts/monitor.py
   ```

## Health Checks

1. **System Health**

   - CPU usage
   - Memory usage
   - Disk usage

2. **Database Health**

   - Connection status
   - Record counts
   - Latest updates

3. **Cache Health**
   - File counts
   - Cache size
   - Access patterns

## Backup Strategy

1. **Database Backups**

   ```bash
   # Create backup
   pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME > backup.sql

   # Restore backup
   psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME < backup.sql
   ```

2. **Cache Backups**

   ```bash
   # Create backup
   tar -czf cache_backup.tar.gz cache/

   # Restore backup
   tar -xzf cache_backup.tar.gz
   ```

## Next Steps

After deployment:

1. Monitor system health
2. Set up automated backups
3. Configure alerts
4. Document maintenance procedures
