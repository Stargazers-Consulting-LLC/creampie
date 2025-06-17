"""Shared test fixtures for stock data tests."""

from pathlib import Path
from unittest.mock import patch

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from cream_api.stock_data.loader import StockDataLoader
from cream_api.tests.stock_data.test_constants import TEST_PARSED_RESPONSES_DIR, TEST_RAW_RESPONSES_DIR


@pytest_asyncio.fixture
async def loader(
    session: AsyncSession,
    test_dirs: dict[str, Path],
) -> StockDataLoader:
    """Create a stock data loader instance with test directories.

    This fixture creates a StockDataLoader instance configured to use test directories
    instead of production ones, ensuring test isolation.

    Args:
        session: Database session for testing
        test_dirs: Dictionary containing test directory paths

    Returns:
        StockDataLoader: Configured loader instance for testing
    """
    with (
        patch("cream_api.settings.app_settings.HTML_RAW_RESPONSES_DIR", test_dirs["raw"]),
        patch("cream_api.settings.app_settings.HTML_PARSED_RESPONSES_DIR", test_dirs["parsed"]),
    ):
        return StockDataLoader(session)


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
