"""Tests for stock data background tasks.

This module contains tests for the background tasks in the stock data module,
including task execution, error handling, and periodic operations.

Following the testing style guide patterns:
- Proper test naming: test_<method>_<scenario>_<expected_result>
- Arrange-Act-Assert pattern
- Async testing with @pytest.mark.asyncio
- Test class organization
- Comprehensive error handling tests

### Legal
SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cream_api.stock_data.models import TrackedStock
from cream_api.stock_data.tasks import (
    process_raw_files_task,
    retrieve_historical_data_task,
    update_all_tracked_stocks,
)
from cream_api.tests.stock_data.test_constants import DEFAULT_TEST_SYMBOL


class TestRetrieveHistoricalDataTask:
    """Test cases for retrieve_historical_data_task function."""

    @pytest.mark.asyncio
    async def test_retrieve_historical_data_task_success(self) -> None:
        """Test successful historical data retrieval."""
        with patch("cream_api.stock_data.tasks.StockDataRetriever") as mock_retriever_class:
            mock_retriever = AsyncMock()
            mock_retriever_class.return_value = mock_retriever
            mock_retriever.get_historical_data = AsyncMock()

            await retrieve_historical_data_task(DEFAULT_TEST_SYMBOL)

            mock_retriever.get_historical_data.assert_called_once_with(symbol=DEFAULT_TEST_SYMBOL, end_date=None)

    @pytest.mark.asyncio
    async def test_retrieve_historical_data_task_with_end_date(self) -> None:
        """Test historical data retrieval with specific end date."""
        with patch("cream_api.stock_data.tasks.StockDataRetriever") as mock_retriever_class:
            mock_retriever = AsyncMock()
            mock_retriever_class.return_value = mock_retriever
            mock_retriever.get_historical_data = AsyncMock()

            end_date = "2024-01-15"
            await retrieve_historical_data_task(DEFAULT_TEST_SYMBOL, end_date)

            mock_retriever.get_historical_data.assert_called_once_with(symbol=DEFAULT_TEST_SYMBOL, end_date=end_date)

    @pytest.mark.asyncio
    async def test_retrieve_historical_data_task_handles_errors(self) -> None:
        """Test that retrieve_historical_data_task propagates errors."""
        with patch("cream_api.stock_data.tasks.StockDataRetriever") as mock_retriever_class:
            mock_retriever = AsyncMock()
            mock_retriever_class.return_value = mock_retriever
            mock_retriever.get_historical_data = AsyncMock(side_effect=Exception("API Error"))

            # Should raise the exception since the function doesn't handle errors
            with pytest.raises(Exception, match="API Error"):
                await retrieve_historical_data_task(DEFAULT_TEST_SYMBOL)


class TestProcessRawFilesTask:
    """Test cases for process_raw_files_task function."""

    @pytest.mark.asyncio
    async def test_process_raw_files_task_success(self) -> None:
        """Test successful raw files processing."""
        with (
            patch("cream_api.stock_data.tasks.AsyncSessionLocal") as mock_session_local,
            patch("cream_api.stock_data.tasks.StockDataLoader") as mock_loader_class,
            patch("cream_api.stock_data.tasks.FileProcessor") as mock_processor_class,
            patch("cream_api.stock_data.tasks.config") as mock_config,
        ):
            # Mock session
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session

            # Mock loader
            mock_loader = AsyncMock()
            mock_loader_class.return_value = mock_loader

            # Mock processor
            mock_processor = AsyncMock()
            mock_processor_class.return_value = mock_processor

            # Mock config
            mock_config.raw_responses_dir = "/tmp/test_raw"

            # Mock directory exists
            with patch("os.path.exists", return_value=True):
                await process_raw_files_task()

            mock_processor.process_raw_files.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_raw_files_task_directory_not_exists(self) -> None:
        """Test raw files processing when directory doesn't exist."""
        with patch("cream_api.stock_data.tasks.config") as mock_config:
            mock_config.raw_responses_dir = "/tmp/nonexistent"

            with patch("os.path.exists", return_value=False):
                # Should not raise exception and should return early
                await process_raw_files_task()

    @pytest.mark.asyncio
    async def test_process_raw_files_task_handles_database_errors(self) -> None:
        """Test that process_raw_files_task handles database errors."""
        with (
            patch("cream_api.stock_data.tasks.AsyncSessionLocal") as mock_session_local,
            patch("cream_api.stock_data.tasks.config") as mock_config,
        ):
            mock_config.raw_responses_dir = "/tmp/test_raw"

            # Mock session that raises database error
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session

            with (
                patch("os.path.exists", return_value=True),
                patch("cream_api.stock_data.tasks.StockDataLoader") as mock_loader_class,
            ):
                AsyncMock()
                mock_loader_class.side_effect = Exception("Database error")

                with pytest.raises(Exception, match="Database error"):
                    await process_raw_files_task()


class TestUpdateAllTrackedStocks:
    """Test cases for update_all_tracked_stocks function."""

    @pytest.mark.asyncio
    async def test_update_all_tracked_stocks_success(self, async_test_db: AsyncSession) -> None:
        """Test successful update of all tracked stocks."""
        # Create test tracked stock
        tracked_stock = TrackedStock(symbol=DEFAULT_TEST_SYMBOL, is_active=True, last_pull_status="pending")
        async_test_db.add(tracked_stock)
        await async_test_db.commit()

        with patch("cream_api.stock_data.tasks.retrieve_historical_data_task") as mock_retrieve:
            mock_retrieve.return_value = None

            await update_all_tracked_stocks(async_test_db)

            # Verify the stock was updated
            stmt = select(TrackedStock).where(TrackedStock.symbol == DEFAULT_TEST_SYMBOL)
            result = await async_test_db.execute(stmt)
            updated_stock = result.scalar_one()

            assert updated_stock.last_pull_status == "success"
            assert updated_stock.error_message is None

    @pytest.mark.asyncio
    async def test_update_all_tracked_stocks_handles_retrieval_errors(self, async_test_db: AsyncSession) -> None:
        """Test that update_all_tracked_stocks handles retrieval errors."""
        # Create test tracked stock
        tracked_stock = TrackedStock(symbol=DEFAULT_TEST_SYMBOL, is_active=True, last_pull_status="pending")
        async_test_db.add(tracked_stock)
        await async_test_db.commit()

        with patch("cream_api.stock_data.tasks.retrieve_historical_data_task") as mock_retrieve:
            mock_retrieve.side_effect = Exception("API Error")

            await update_all_tracked_stocks(async_test_db)

            # Verify the stock was updated with error status
            stmt = select(TrackedStock).where(TrackedStock.symbol == DEFAULT_TEST_SYMBOL)
            result = await async_test_db.execute(stmt)
            updated_stock = result.scalar_one()

            assert updated_stock.last_pull_status == "failure"
            assert updated_stock.error_message is not None and "API Error" in updated_stock.error_message

    @pytest.mark.asyncio
    async def test_update_all_tracked_stocks_no_active_stocks(self, async_test_db: AsyncSession) -> None:
        """Test update_all_tracked_stocks when no active stocks exist."""
        with patch("cream_api.stock_data.tasks.retrieve_historical_data_task") as mock_retrieve:
            await update_all_tracked_stocks(async_test_db)

            # Should not call retrieve function
            mock_retrieve.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_all_tracked_stocks_handles_database_errors(self, async_test_db: AsyncSession) -> None:
        """Test that update_all_tracked_stocks handles retrieval errors gracefully."""
        # Create test tracked stock first so we have something to process
        tracked_stock = TrackedStock(symbol=DEFAULT_TEST_SYMBOL, is_active=True, last_pull_status="pending")
        async_test_db.add(tracked_stock)
        await async_test_db.commit()

        with patch("cream_api.stock_data.tasks.retrieve_historical_data_task") as mock_retrieve:
            mock_retrieve.side_effect = Exception("Database error")

            # Should handle the error gracefully, not raise it
            await update_all_tracked_stocks(async_test_db)

            # Verify the stock was updated with error status
            stmt = select(TrackedStock).where(TrackedStock.symbol == DEFAULT_TEST_SYMBOL)
            result = await async_test_db.execute(stmt)
            updated_stock = result.scalar_one()

            assert updated_stock.last_pull_status == "failure"
            assert updated_stock.error_message is not None and "Database error" in updated_stock.error_message


class TestTaskIntegration:
    """Integration tests for task interactions."""

    @pytest.mark.asyncio
    async def test_task_error_message_cleaning(self, async_test_db: AsyncSession) -> None:
        """Test that error messages are properly cleaned in tasks."""
        # Create test tracked stock
        tracked_stock = TrackedStock(symbol=DEFAULT_TEST_SYMBOL, is_active=True, last_pull_status="pending")
        async_test_db.add(tracked_stock)
        await async_test_db.commit()

        with patch("cream_api.stock_data.tasks.retrieve_historical_data_task") as mock_retrieve:
            # Mock error with parameters dump
            error_msg = "Database error [parameters: {'param': 'value', 'large_dump': '...'}]"
            mock_retrieve.side_effect = Exception(error_msg)

            await update_all_tracked_stocks(async_test_db)

            # Verify the stock was updated with cleaned error message
            stmt = select(TrackedStock).where(TrackedStock.symbol == DEFAULT_TEST_SYMBOL)
            result = await async_test_db.execute(stmt)
            updated_stock = result.scalar_one()

            assert updated_stock.last_pull_status == "failure"
            assert updated_stock.error_message is not None and "[parameters:" not in updated_stock.error_message
            assert updated_stock.error_message is not None and "Database error" in updated_stock.error_message
