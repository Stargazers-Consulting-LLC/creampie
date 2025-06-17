"""Tests for stock data loader.

This module contains tests for the StockDataLoader class, which is responsible for:
- Validating stock data structure
- Transforming raw data into StockData objects
- Storing data in the database
- Processing raw HTML files

The tests follow the testing best practices outlined in the Backend Style Guide, including:
- Proper test isolation with dedicated database sessions
- Comprehensive error handling tests
- Clear test organization and documentation
"""

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cream_api.settings import get_app_settings
from cream_api.stock_data.loader import StockDataLoader
from cream_api.stock_data.models import StockData
from cream_api.tests.stock_data.test_constants import (
    TEST_ADJ_CLOSE_PRICE,
    TEST_CLOSE_PRICE,
    TEST_DATE,
    TEST_HIGH_PRICE,
    TEST_HTML_CONTENT,
    TEST_HTML_FILENAME,
    TEST_LOW_PRICE,
    TEST_OPEN_PRICE,
    TEST_PARSED_RESPONSES_DIR,
    TEST_RAW_RESPONSES_DIR,
    TEST_STOCK_DATA,
    TEST_SYMBOL,
    TEST_VOLUME,
)

settings = get_app_settings()


@pytest.fixture
def test_raw_responses_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for test raw responses.

    This fixture ensures test isolation by creating a unique temporary directory
    for each test that needs to work with raw response files.

    Returns:
        Path: Path to the temporary directory for raw responses
    """
    return tmp_path / TEST_RAW_RESPONSES_DIR


@pytest.fixture
def test_parsed_responses_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for test parsed responses.

    This fixture ensures test isolation by creating a unique temporary directory
    for each test that needs to work with parsed response files.

    Returns:
        Path: Path to the temporary directory for parsed responses
    """
    return tmp_path / TEST_PARSED_RESPONSES_DIR


@pytest_asyncio.fixture
async def session(async_test_db: AsyncSession) -> AsyncSession:
    """Create a database session for testing.

    This fixture provides an isolated database session for each test,
    ensuring that database operations don't interfere with each other.

    Returns:
        AsyncSession: Isolated database session for testing
    """
    return async_test_db


@pytest_asyncio.fixture
async def loader(
    session: AsyncSession,
    test_raw_responses_dir: Path,
    test_parsed_responses_dir: Path,
) -> StockDataLoader:
    """Create a stock data loader instance with test directories.

    This fixture creates a StockDataLoader instance configured to use test directories
    instead of production ones, ensuring test isolation.

    Args:
        session: Database session for testing
        test_raw_responses_dir: Directory for test raw responses
        test_parsed_responses_dir: Directory for test parsed responses

    Returns:
        StockDataLoader: Configured loader instance for testing
    """
    with (
        patch("cream_api.settings.app_settings.HTML_RAW_RESPONSES_DIR", test_raw_responses_dir),
        patch("cream_api.settings.app_settings.HTML_PARSED_RESPONSES_DIR", test_parsed_responses_dir),
    ):
        return StockDataLoader(session)


@pytest.mark.asyncio
async def test_validate_data_valid(loader: StockDataLoader) -> None:
    """Test validation of valid stock data.

    This test verifies that:
    1. The loader accepts valid stock data structure
    2. No exceptions are raised for valid data
    3. All required fields are properly validated
    """
    await loader.validate_data(TEST_STOCK_DATA)  # Should not raise


@pytest.mark.asyncio
async def test_validate_data_invalid(loader: StockDataLoader) -> None:
    """Test validation of invalid stock data.

    This test verifies that:
    1. The loader rejects invalid stock data structure
    2. Appropriate exceptions are raised for invalid data
    3. Missing required fields are properly detected
    """
    invalid_data: dict[str, Any] = {
        "prices": [
            {
                "date": TEST_DATE.strftime("%Y-%m-%d"),
                "open": str(TEST_OPEN_PRICE),
                # Missing required fields
            }
        ]
    }
    with pytest.raises(ValueError, match="Missing required fields"):
        await loader.validate_data(invalid_data)


@pytest.mark.asyncio
async def test_validate_data_empty_prices(loader: StockDataLoader) -> None:
    """Test validation of data with empty prices list.

    This test verifies that:
    1. The loader rejects data with empty prices list
    2. Appropriate exception is raised
    """
    invalid_data: dict[str, Any] = {"prices": []}
    with pytest.raises(ValueError, match="Prices list cannot be empty"):
        await loader.validate_data(invalid_data)


@pytest.mark.asyncio
async def test_validate_data_invalid_type(loader: StockDataLoader) -> None:
    """Test validation of data with invalid type.

    This test verifies that:
    1. The loader rejects data with invalid type
    2. Appropriate exception is raised
    """
    invalid_data: str = "not a dict"
    with pytest.raises(ValueError, match="Data must be a dictionary"):
        await loader.validate_data(invalid_data)  # type: ignore


@pytest.mark.asyncio
async def test_transform_data(loader: StockDataLoader) -> None:
    """Test transformation of raw data to StockData objects.

    This test verifies that:
    1. Raw data is correctly transformed into StockData objects
    2. All fields are properly converted to their expected types
    3. The transformation maintains data integrity
    """
    result = await loader.transform_data(TEST_STOCK_DATA)
    assert len(result) == 1
    assert isinstance(result[0], StockData)
    assert result[0].date == TEST_DATE
    assert result[0].open == TEST_OPEN_PRICE
    assert result[0].high == TEST_HIGH_PRICE
    assert result[0].low == TEST_LOW_PRICE
    assert result[0].close == TEST_CLOSE_PRICE
    assert result[0].adj_close == TEST_ADJ_CLOSE_PRICE
    assert result[0].volume == TEST_VOLUME


@pytest.mark.asyncio
async def test_store_data(loader: StockDataLoader, test_dirs: dict[str, Path]) -> None:
    """Test storing data in the database."""
    # Create test data
    valid_data = {
        "prices": [
            {
                "date": TEST_DATE.strftime("%Y-%m-%d"),
                "open": str(TEST_OPEN_PRICE),
                "high": str(TEST_HIGH_PRICE),
                "low": str(TEST_LOW_PRICE),
                "close": str(TEST_CLOSE_PRICE),
                "adj_close": str(TEST_ADJ_CLOSE_PRICE),
                "volume": str(TEST_VOLUME),
            }
        ]
    }

    # Store data
    await loader.process_data(TEST_SYMBOL, valid_data)

    # Verify data was stored
    async with loader.session as session:
        result = await session.execute(select(StockData).where(StockData.symbol == TEST_SYMBOL))
        stored_data = result.scalar_one()
        assert stored_data is not None
        assert stored_data.symbol == TEST_SYMBOL
        assert stored_data.date == TEST_DATE
        assert stored_data.open == TEST_OPEN_PRICE
        assert stored_data.high == TEST_HIGH_PRICE
        assert stored_data.low == TEST_LOW_PRICE
        assert stored_data.close == TEST_CLOSE_PRICE
        assert stored_data.adj_close == TEST_ADJ_CLOSE_PRICE
        assert stored_data.volume == TEST_VOLUME


@pytest.mark.asyncio
async def test_store_data_invalid(loader: StockDataLoader) -> None:
    """Test storing invalid data."""
    invalid_data: dict[str, Any] = {"prices": []}  # Empty prices list should trigger validation error
    with pytest.raises(ValueError):
        await loader.process_data(TEST_SYMBOL, invalid_data)


@pytest.mark.asyncio
async def test_process_raw_files(loader: StockDataLoader, test_dirs: dict[str, Path]) -> None:
    """Test processing raw HTML files."""
    # Create test file in raw responses directory
    test_file = test_dirs["raw"] / TEST_HTML_FILENAME
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text(TEST_HTML_CONTENT)

    # Process files
    await loader.process_raw_files()

    # Verify file was moved
    assert not test_file.exists()
    parsed_file = test_dirs["parsed"] / TEST_HTML_FILENAME
    assert parsed_file.exists()

    # Verify data was stored
    async with loader.session as session:
        result = await session.execute(select(StockData).where(StockData.symbol == TEST_SYMBOL))
        stored_data = result.scalar_one()
        assert stored_data is not None
        assert stored_data.symbol == TEST_SYMBOL
        assert stored_data.date == TEST_DATE
        assert stored_data.open == TEST_OPEN_PRICE
        assert stored_data.high == TEST_HIGH_PRICE
        assert stored_data.low == TEST_LOW_PRICE
        assert stored_data.close == TEST_CLOSE_PRICE
        assert stored_data.adj_close == TEST_ADJ_CLOSE_PRICE
        assert stored_data.volume == TEST_VOLUME


@pytest.mark.asyncio
async def test_process_raw_files_error_handling(
    loader: StockDataLoader, test_raw_responses_dir: Path, test_parsed_responses_dir: Path
) -> None:
    """Test error handling during raw file processing.

    This test verifies that:
    1. Errors during file processing are properly caught
    2. The process continues with remaining files
    3. Failed files are not moved to the parsed directory
    """
    # Create test HTML file
    test_file = test_raw_responses_dir / TEST_HTML_FILENAME
    test_raw_responses_dir.mkdir(exist_ok=True)
    test_parsed_responses_dir.mkdir(exist_ok=True)
    test_file.write_text("invalid html")

    # Mock the parser to raise an exception
    mock_parser = MagicMock()
    mock_parser.parse_html_file.side_effect = ValueError("Invalid HTML")

    with patch("cream_api.stock_data.loader.StockDataParser", return_value=mock_parser):
        await loader.process_raw_files()

    # Verify file was not moved
    assert test_file.exists()
    assert not (test_parsed_responses_dir / TEST_HTML_FILENAME).exists()
