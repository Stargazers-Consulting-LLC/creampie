"""Shared test fixtures for stock data tests."""

import os
import shutil

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from cream_api.stock_data.config import StockDataConfig, create_stock_data_config
from cream_api.stock_data.loader import StockDataLoader
from cream_api.stock_data.parser import StockDataParser
from cream_api.tests.stock_data.stock_data_test_constants import (
    DEFAULT_TEST_SYMBOL,
    TEST_DATE,
    TEST_DEADLETTER_RESPONSES_DIR,
    TEST_FIXTURE_PATH,
    TEST_PARSED_RESPONSES_DIR,
    TEST_RAW_RESPONSES_DIR,
)


@pytest.fixture
def test_dirs(tmp_path: str) -> dict[str, str]:
    """Create temporary test directories.

    This fixture creates temporary directories for raw, parsed, and deadletter responses
    that can be used across multiple test modules.

    Args:
        tmp_path: Pytest fixture providing a temporary directory

    Returns:
        Dictionary containing paths to raw, parsed, and deadletter response directories
    """
    raw_dir = os.path.join(tmp_path, TEST_RAW_RESPONSES_DIR)
    parsed_dir = os.path.join(tmp_path, TEST_PARSED_RESPONSES_DIR)
    deadletter_dir = os.path.join(tmp_path, TEST_DEADLETTER_RESPONSES_DIR)
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(parsed_dir, exist_ok=True)
    os.makedirs(deadletter_dir, exist_ok=True)
    return {"raw": raw_dir, "parsed": parsed_dir, "deadletter": deadletter_dir}


@pytest.fixture
def test_config(test_dirs: dict[str, str]) -> StockDataConfig:
    """Create test configuration.

    Args:
        test_dirs: Dictionary containing test directory paths

    Returns:
        StockDataConfig: Test configuration instance
    """
    return create_stock_data_config(
        raw_responses_dir=test_dirs["raw"],
        parsed_responses_dir=test_dirs["parsed"],
        deadletter_responses_dir=test_dirs["deadletter"],
    )


@pytest.fixture
def test_data_files(test_dirs: dict[str, str]) -> dict[str, str]:
    """Set up test data files in temporary directories.

    This fixture copies test data files from the fixtures directory to the
    temporary test directories, ensuring test isolation.

    Args:
        test_dirs: Dictionary containing test directory paths

    Returns:
        Dictionary containing paths to test data files
    """
    # Copy test files from fixtures to temporary directories
    fixture_files = {
        DEFAULT_TEST_SYMBOL: f"{DEFAULT_TEST_SYMBOL}_{TEST_DATE.strftime('%Y-%m-%d')}.html",
    }

    test_files = {}
    for symbol, filename in fixture_files.items():
        source = os.path.join(os.path.dirname(TEST_FIXTURE_PATH), filename)
        if os.path.exists(source):
            dest = os.path.join(test_dirs["raw"], filename)
            shutil.copy2(source, dest)
            test_files[symbol] = dest

    return test_files


@pytest_asyncio.fixture
async def loader(
    async_test_db: AsyncSession,
    test_config: StockDataConfig,
    test_data_files: dict[str, str],
) -> StockDataLoader:
    """Create a stock data loader instance with test configuration.

    This fixture creates a StockDataLoader instance configured to use test directories
    instead of production ones, ensuring test isolation.

    Args:
        async_test_db: Database session for testing
        test_config: Test configuration instance
        test_data_files: Dictionary containing paths to test data files

    Returns:
        StockDataLoader: Configured loader instance for testing
    """
    # Create loader with test configuration
    loader = StockDataLoader(session=async_test_db, config=test_config)

    # Verify we're using test directories
    assert loader.config.raw_responses_dir.startswith(test_config.raw_responses_dir)
    assert loader.config.parsed_responses_dir.startswith(test_config.parsed_responses_dir)

    return loader


@pytest.fixture
def parser(test_config: StockDataConfig) -> StockDataParser:
    """Create a stock data parser instance with test configuration.

    Args:
        test_config: Test configuration instance

    Returns:
        StockDataParser: Configured parser instance for testing
    """
    return StockDataParser(config=test_config)
