"""Shared test fixtures for stock data tests."""

import shutil
from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from cream_api.stock_data.config import StockDataConfig, create_stock_data_config
from cream_api.stock_data.loader import StockDataLoader
from cream_api.stock_data.parser import StockDataParser
from cream_api.tests.stock_data.test_constants import (
    TEST_DATE,
    TEST_FIXTURES_DIR,
    TEST_PARSED_RESPONSES_DIR,
    TEST_RAW_RESPONSES_DIR,
    TEST_SYMBOL,
)


@pytest.fixture
def test_dirs(tmp_path: Path) -> dict[str, Path]:
    """Create temporary test directories.

    This fixture creates temporary directories for raw and parsed responses
    that can be used across multiple test modules.

    Args:
        tmp_path: Pytest fixture providing a temporary directory

    Returns:
        Dictionary containing paths to raw and parsed response directories
    """
    raw_dir = tmp_path / TEST_RAW_RESPONSES_DIR
    parsed_dir = tmp_path / TEST_PARSED_RESPONSES_DIR
    raw_dir.mkdir()
    parsed_dir.mkdir()
    return {"raw": raw_dir, "parsed": parsed_dir}


@pytest.fixture
def test_config(test_dirs: dict[str, Path]) -> StockDataConfig:
    """Create test configuration.

    Args:
        test_dirs: Dictionary containing test directory paths

    Returns:
        StockDataConfig: Test configuration instance
    """
    return create_stock_data_config(
        raw_responses_dir=test_dirs["raw"],
        parsed_responses_dir=test_dirs["parsed"],
    )


@pytest.fixture
def test_data_files(test_dirs: dict[str, Path]) -> dict[str, Path]:
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
        TEST_SYMBOL: f"{TEST_SYMBOL}_{TEST_DATE.strftime('%Y-%m-%d')}.html",
    }

    test_files = {}
    for symbol, filename in fixture_files.items():
        source = Path(TEST_FIXTURES_DIR) / filename
        if source.exists():
            dest = test_dirs["raw"] / filename
            shutil.copy2(source, dest)
            test_files[symbol] = dest

    return test_files


@pytest_asyncio.fixture
async def loader(
    async_test_db: AsyncSession,
    test_config: StockDataConfig,
    test_data_files: dict[str, Path],
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
    assert str(loader.config.raw_responses_dir).startswith(str(test_config.raw_responses_dir))
    assert str(loader.config.parsed_responses_dir).startswith(str(test_config.parsed_responses_dir))

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
