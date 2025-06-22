#!/usr/bin/env python3
"""Database setup script for development environment.

This script performs a complete database reset for development:
1. Drops the development database
2. Recreates the database
3. Applies all migrations
4. Populates with fake stock data

References:
    - [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
    - [Python Type Hints](https://docs.python.org/3/library/typing.html)
    - [Python AsyncIO](https://docs.python.org/3/library/asyncio.html)
    - [Python ArgParse](https://docs.python.org/3/library/argparse.html)

### Legal
SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

import argparse
import asyncio
import logging
import os
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from cream_api.settings import get_app_settings
from cream_api.stock_data.models import StockData, TrackedStock

# Calculate project root for other script operations
script_dir = os.path.dirname(os.path.abspath(__file__))  # scripts/db/
project_root = os.path.dirname(os.path.dirname(script_dir))  # Go up 2 levels to project root

# Module-level constants
DEFAULT_RECORD_COUNT = 10
STOCK_SYMBOLS = ["TEST", "DEMO", "SAMPLE", "FAKE", "MOCK", "DUMMY", "EXAMPLE", "TRIAL", "PILOT", "PROTO"]

# Module-level variables
logger = logging.getLogger(__name__)

settings = get_app_settings()


def run_command(command: list[str], cwd: str | None = None) -> bool:
    """Run a shell command and return success status.

    Args:
        command: List of command arguments
        cwd: Working directory (optional)

    Returns:
        bool: True if command succeeded, False otherwise
    """
    try:
        subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True)
        logger.info(f"Command succeeded: {' '.join(command)}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {' '.join(command)}")
        logger.error(f"Error: {e.stderr}")
        return False


def drop_database() -> bool:
    """Drop the development database.

    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Dropping development database...")

    # Connect as postgres user to drop database
    drop_command = ["sudo", "-u", "postgres", "psql", "-c", f"DROP DATABASE IF EXISTS {settings.db_name};"]

    return run_command(drop_command, cwd=None)


def create_database() -> bool:
    """Create the development database.

    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Creating development database...")

    # Connect as postgres user to create database
    create_command = [
        "sudo",
        "-u",
        "postgres",
        "psql",
        "-c",
        f"CREATE DATABASE {settings.db_name} OWNER {settings.db_user};",
    ]

    return run_command(create_command, cwd=None)


def apply_migrations() -> bool:
    """Apply all database migrations.

    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Applying database migrations...")

    api_dir = os.path.join(project_root, "cream_api")

    # Run alembic upgrade
    migrate_command = ["poetry", "run", "alembic", "upgrade", "head"]

    return run_command(migrate_command, cwd=api_dir)


def grant_table_permissions() -> bool:
    """Grant necessary database permissions.

    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Granting database permissions...")

    # Run the grant permissions script with sudo (requires root privileges)
    grant_command = ["sudo", "bash", os.path.join(project_root, "scripts", "db", "grant_table_permissions.sh")]

    return run_command(grant_command, cwd=None)


def generate_stock_data(symbol: str, date: datetime) -> dict[str, Any]:
    """Generate realistic stock data for browsing the website.

    Args:
        symbol: Stock symbol (e.g., "TEST")
        date: Date for the stock data

    Returns:
        dict: Dictionary containing stock data fields
    """
    # Base prices for fictional stocks (realistic but fake)
    base_prices = {
        "TEST": 180.0,
        "DEMO": 140.0,
        "SAMPLE": 380.0,
        "FAKE": 150.0,
        "MOCK": 250.0,
        "DUMMY": 480.0,
        "EXAMPLE": 900.0,
        "TRIAL": 600.0,
        "PILOT": 150.0,
        "PROTO": 45.0,
    }

    base_price = base_prices.get(symbol, 100.0)

    # Add some realistic daily variation based on the date
    day_of_year = date.timetuple().tm_yday
    variation = (day_of_year % 20 - 10) / 100  # ±10% variation

    open_price = base_price * (1 + variation)
    high_price = open_price * 1.03  # 3% daily high
    low_price = open_price * 0.97  # 3% daily low
    close_price = open_price * (1 + (day_of_year % 7 - 3) / 100)  # Small close variation
    adj_close = close_price

    # Realistic volume based on stock popularity (fictional)
    base_volumes = {
        "TEST": 50000000,
        "DEMO": 30000000,
        "SAMPLE": 25000000,
        "FAKE": 40000000,
        "MOCK": 80000000,
        "DUMMY": 20000000,
        "EXAMPLE": 35000000,
        "TRIAL": 15000000,
        "PILOT": 45000000,
        "PROTO": 35000000,
    }

    volume = base_volumes.get(symbol, 20000000)
    volume += (day_of_year % 10) * 1000000  # Add some daily variation

    return {
        "symbol": symbol,
        "date": date,
        "open": round(open_price, 2),
        "high": round(high_price, 2),
        "low": round(low_price, 2),
        "close": round(close_price, 2),
        "adj_close": round(adj_close, 2),
        "volume": volume,
    }


async def populate_stock_data(record_count: int) -> None:
    """Populate database with fake stock data.

    Args:
        record_count: Number of stock symbols to create
    """
    logger.info(f"Creating {record_count} stock symbols with 30 days of data each...")

    # Debug: Check what connection string is being used
    logger.info(f"Using connection string: {settings.get_connection_string()}")

    # Create async engine and session factory with our custom settings
    engine = create_async_engine(settings.get_connection_string())
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with async_session() as session:
            # Create tracked stocks
            logger.info("Creating tracked stocks...")
            tracked_stocks = []
            for i, symbol in enumerate(STOCK_SYMBOLS[:record_count]):
                tracked_stock = TrackedStock(
                    symbol=symbol,
                    last_pull_date=datetime.now(UTC) - timedelta(hours=i + 1),
                    last_pull_status="success",
                    error_message=None,
                    is_active=False,
                )
                session.add(tracked_stock)
                tracked_stocks.append(tracked_stock)
            await session.commit()

            # Create stock data
            logger.info("Creating stock data...")
            for tracked_stock in tracked_stocks:
                # Create 30 days of historical data
                for days_ago in range(30):
                    date = datetime.now(UTC) - timedelta(days=days_ago)
                    stock_data = generate_stock_data(tracked_stock.symbol, date)
                    stock_record = StockData(**stock_data)
                    session.add(stock_record)
            await session.commit()

            logger.info("Stock data population completed successfully!")
    finally:
        await engine.dispose()


def confirm_action(message: str) -> bool:
    """Ask user for confirmation.

    Args:
        message: Message to display to the user

    Returns:
        bool: True if user confirms, False otherwise
    """
    response = input(f"{message} (y/N): ").strip().lower()
    return response in ["y", "yes"]


async def main() -> None:
    """Main function to run the database setup script."""
    parser = argparse.ArgumentParser(
        description="Complete database reset and setup for development",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/db/populate_test_data.py                    # Reset with 10 stock symbols
  python scripts/db/populate_test_data.py --count 5          # Reset with 5 stock symbols
  python scripts/db/populate_test_data.py --count 20 --force # Reset with 20 symbols, skip confirmation
        """,
    )

    parser.add_argument(
        "--count",
        "-c",
        type=int,
        default=DEFAULT_RECORD_COUNT,
        help=f"Number of stock symbols to create (default: {DEFAULT_RECORD_COUNT})",
    )

    parser.add_argument("--force", "-f", action="store_true", help="Skip confirmation prompt")

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Show what will be done
    print("🚀 Database Reset and Setup Script")
    print("=" * 50)
    print("This will:")
    print("  1. Drop the development database")
    print("  2. Recreate the database")
    print("  3. Apply all migrations")
    print(f"  4. Populate with {args.count} stock symbols (30 days each)")
    print()

    # Confirm action unless --force is used
    if not args.force:
        message = "This will completely reset the development database. Continue?"
        if not confirm_action(message):
            logger.info("Operation cancelled by user")
            sys.exit(1)

    try:
        start_time = datetime.now()

        # Step 1: Drop database
        if not drop_database():
            logger.error("Failed to drop database")
            sys.exit(1)

        # Step 2: Create database
        if not create_database():
            logger.error("Failed to create database")
            sys.exit(1)

        # Step 3: Apply migrations
        if not apply_migrations():
            logger.error("Failed to apply migrations")
            sys.exit(1)

        # Step 4: Grant table permissions
        if not grant_table_permissions():
            logger.error("Failed to grant table permissions")
            sys.exit(1)

        # Step 5: Populate with stock data
        await populate_stock_data(args.count)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print()
        print("🎉 Database setup completed successfully!")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print()
        print("📊 Summary:")
        print("  - Database reset and recreated")
        print("  - All migrations applied")
        print(f"  - {args.count} stock symbols created")
        print(f"  - {args.count * 30} stock records created (30 days each)")
        print()
        print("💡 Your development database is ready!")

    except Exception as e:
        logger.error(f"Error during database setup: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
