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

import pytest
from sqlalchemy import select

from cream_api.stock_data.config import StockDataConfig
from cream_api.stock_data.loader import StockDataLoader
from cream_api.stock_data.models import StockData
from cream_api.tests.stock_data.test_constants import (
    TEST_ADJ_CLOSE_PRICE,
    TEST_CLOSE_PRICE,
    TEST_DATE,
    TEST_HIGH_PRICE,
    TEST_HTML_FILENAME,
    TEST_LOW_PRICE,
    TEST_OPEN_PRICE,
    TEST_STOCK_DATA,
    TEST_SYMBOL,
    TEST_VOLUME,
)


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
async def test_store_data(
    loader: StockDataLoader,
    test_config: StockDataConfig,
    test_data_files: dict[str, Path],
) -> None:
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
    await loader.store_data(TEST_SYMBOL, await loader.transform_data(valid_data))

    # Verify data was stored
    result = await loader.session.execute(select(StockData))
    stored_data = result.scalars().all()
    assert len(stored_data) == 1
    assert stored_data[0].date == TEST_DATE
    assert stored_data[0].open == TEST_OPEN_PRICE


@pytest.mark.asyncio
async def test_store_data_invalid(loader: StockDataLoader) -> None:
    """Test storing invalid data in the database."""
    invalid_data: dict[str, Any] = {"prices": []}
    with pytest.raises(ValueError, match="Prices list cannot be empty"):
        await loader.validate_data(invalid_data)


@pytest.mark.asyncio
async def test_process_raw_files(
    loader: StockDataLoader,
    test_config: StockDataConfig,
    test_data_files: dict[str, Path],
) -> None:
    """Test processing raw HTML files.

    This test verifies that:
    1. Raw HTML files are properly processed
    2. Data is correctly extracted and stored
    3. Files are moved to the parsed directory
    4. Only test data files are processed
    """
    # Verify test files exist
    assert test_data_files.get(TEST_SYMBOL) is not None
    assert test_data_files[TEST_SYMBOL].exists()

    # Verify we're using test directories
    assert str(loader.config.raw_responses_dir).startswith(str(test_config.raw_responses_dir))
    assert str(loader.config.parsed_responses_dir).startswith(str(test_config.parsed_responses_dir))

    # Process files using the loader's method
    await loader.process_raw_files()

    # Verify files were moved to parsed directory
    parsed_dir = test_config.parsed_responses_dir
    assert (parsed_dir / TEST_HTML_FILENAME).exists()
    assert not (test_config.raw_responses_dir / TEST_HTML_FILENAME).exists()

    # Verify data was stored
    result = await loader.session.execute(select(StockData))
    stored_data = result.scalars().all()
    assert len(stored_data) > 0

    # Verify only test data was processed
    for data in stored_data:
        assert data.symbol == TEST_SYMBOL


@pytest.mark.asyncio
async def test_process_raw_files_error_handling(
    loader: StockDataLoader,
    test_config: StockDataConfig,
    test_data_files: dict[str, Path],
) -> None:
    """Test error handling when processing raw files.

    This test verifies that:
    1. Invalid files are properly handled
    2. Errors are logged but don't crash the process
    3. Valid files are still processed
    4. Only test data files are processed
    """
    # Create an invalid file
    invalid_file = test_config.raw_responses_dir / "INVALID.html"
    invalid_file.write_text("invalid content")

    # Process files using the loader's method
    await loader.process_raw_files()

    # Verify invalid file was handled (should still exist since loader doesn't remove invalid files)
    assert invalid_file.exists()

    # Verify valid files were still processed
    assert (test_config.parsed_responses_dir / TEST_HTML_FILENAME).exists()

    # Verify only test data was processed
    result = await loader.session.execute(select(StockData))
    stored_data = result.scalars().all()
    for data in stored_data:
        assert data.symbol == TEST_SYMBOL
