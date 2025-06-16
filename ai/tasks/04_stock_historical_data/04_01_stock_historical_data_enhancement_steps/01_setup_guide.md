# Project Setup Guide

## Virtual Environment Setup

1. Create and activate virtual environment:

   ```bash
   poetry install
   poetry shell
   ```

2. Required dependencies are already in pyproject.toml:
   ```toml
   [tool.poetry.dependencies]
   beautifulsoup4 = "^4.13.4"
   requests = "^2.32.4"
   pandas = "^2.3.0"
   whenever = "^0.8.5"
   sqlalchemy = "^2.0.41"
   pydantic-settings = "^2.9.1"
   psycopg = "^3.2.9"
   fastapi = "^0.110.0"
   alembic = "^1.13.1"
   stargazer-utils = "^1.0.0"
   ```

## Project Structure

1. Create the following directory structure:
   ```
   cream_api/
   ├── __init__.py
   ├── stock_data/
   │   ├── __init__.py
   │   ├── models.py
   │   ├── exceptions.py
   │   ├── retriever.py
   │   └── parser.py
   ├── tests/
   │   ├── __init__.py
   │   ├── conftest.py
   │   ├── test_parser.py
   │   ├── test_retriever.py
   │   └── test_error_handling.py
   ├── migrations/
   │   ├── versions/
   │   ├── env.py
   │   └── script.py.mako
   ├── README.md
   └── pyproject.toml
   ```

## Configuration

The project uses the existing settings module at `cream_api/settings.py`. Add the following settings to your `.env` file:

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
```

## Database Setup

1. Create `stock_data/models.py`:

   ```python
   from datetime import datetime
   from typing import Any

   from sqlalchemy import DateTime, Float, Integer, String, UniqueConstraint
   from sqlalchemy.orm import Mapped, mapped_column

   from cream_api.db import ModelBase

   class StockData(ModelBase):
       """Stock historical data model."""
       __tablename__ = "stock_data"

       id: Mapped[int] = mapped_column(Integer, primary_key=True)
       symbol: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
       date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
       open: Mapped[float] = mapped_column(Float, nullable=False)
       high: Mapped[float] = mapped_column(Float, nullable=False)
       low: Mapped[float] = mapped_column(Float, nullable=False)
       close: Mapped[float] = mapped_column(Float, nullable=False)
       adj_close: Mapped[float] = mapped_column(Float, nullable=False)
       volume: Mapped[int] = mapped_column(Integer, nullable=False)

       __table_args__ = (
           UniqueConstraint("symbol", "date", name="uix_symbol_date"),
       )
   ```

2. Create database:

   ```sql
   CREATE DATABASE stock_data;
   ```

3. Initialize Alembic for migrations:

   ```bash
   alembic init migrations
   ```

4. Update `alembic.ini` with database URL:
   ```ini
   sqlalchemy.url = postgresql+psycopg://postgres:password@localhost/stock_data
   ```

## Initial Testing Setup

1. Create `tests/conftest.py`:

   ```python
   from pathlib import Path
   from typing import Any, Generator

   import pytest
   from sqlalchemy import create_engine
   from sqlalchemy.orm import Session, sessionmaker

   from cream_api.db import ModelBase, get_db
   from cream_api.settings import get_app_settings

   settings = get_app_settings()

   @pytest.fixture
   def test_data_dir() -> Path:
       """Get test data directory."""
       return settings.TEST_DATA_DIR

   @pytest.fixture
   def sample_html() -> str:
       """Get sample HTML for testing."""
       return """
       <table>
           <tr>
               <th>Date</th>
               <th>Open</th>
               <th>High</th>
               <th>Low</th>
               <th>Close</th>
               <th>Adj Close</th>
               <th>Volume</th>
           </tr>
           <tr>
               <td>2024-01-01</td>
               <td>100.00</td>
               <td>101.00</td>
               <td>99.00</td>
               <td>100.50</td>
               <td>100.50</td>
               <td>1000000</td>
           </tr>
       </table>
       """

   @pytest.fixture
   def db_session() -> Generator[Session, Any, None]:
       """Create a test database session."""
       engine = create_engine("sqlite:///:memory:")
       Base.metadata.create_all(engine)
       TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
       session = TestingSessionLocal()
       try:
           yield session
       finally:
           session.close()
   ```

## Next Steps

After completing this setup:

1. Verify all directories are created correctly
2. Test database connection
3. Run initial test suite to ensure testing environment is working
4. Create initial database migration:
   ```bash
   alembic revision --autogenerate -m "Initial stock data tables"
   alembic upgrade head
   ```
5. Proceed to HTML Parser Implementation
