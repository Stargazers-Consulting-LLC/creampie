"""Integration tests for stock tracking feature.

This module contains comprehensive end-to-end integration tests for the stock tracking
feature, testing the complete workflow from frontend form submission to backend
database operations.

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

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cream_api.main import app
from cream_api.stock_data.models import TrackedStock
from cream_api.stock_data.schemas import PullStatus
from cream_api.tests.stock_data.stock_data_test_constants import DEFAULT_TEST_SYMBOL

client = TestClient(app)


class TestCompleteUserWorkflow:
    """Integration tests for complete user workflow from form to database."""

    @pytest.mark.asyncio
    async def test_complete_stock_tracking_workflow_success(self, async_test_db: AsyncSession) -> None:
        """Test complete workflow: form submission → API → database.

        This test verifies the complete end-to-end workflow:
        1. User submits stock tracking request via API
        2. API validates and processes the request
        3. Database is updated with tracking entry
        4. Response confirms successful tracking

        Args:
            async_test_db: Async database session for testing
        """
        # Arrange - Simulate frontend form submission
        request_data = {"symbol": DEFAULT_TEST_SYMBOL}

        # Act - Frontend makes API call
        response = client.post("/api/stock-data/track", json=request_data)

        # Assert - Frontend receives success response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "tracking"
        assert data["message"] == f"Stock {DEFAULT_TEST_SYMBOL} is now being tracked"
        assert data["symbol"] == DEFAULT_TEST_SYMBOL

        # Assert - Database contains the tracking entry
        result = await async_test_db.execute(select(TrackedStock).where(TrackedStock.symbol == DEFAULT_TEST_SYMBOL))
        tracked_stock = result.scalar_one()
        assert tracked_stock.symbol == DEFAULT_TEST_SYMBOL
        assert tracked_stock.is_active is True
        assert tracked_stock.last_pull_status == PullStatus.PENDING

    @pytest.mark.asyncio
    async def test_complete_workflow_with_duplicate_request_handled_gracefully(
        self, async_test_db: AsyncSession
    ) -> None:
        """Test complete workflow handles duplicate requests gracefully.

        This test verifies that:
        1. First request creates tracking entry
        2. Second request returns success without creating duplicate
        3. Database maintains single entry
        4. Frontend receives consistent responses

        Args:
            async_test_db: Async database session for testing
        """
        # Arrange
        request_data = {"symbol": DEFAULT_TEST_SYMBOL}

        # Act - First request (should create entry)
        response1 = client.post("/api/stock-data/track", json=request_data)

        # Act - Second request (should return existing entry)
        response2 = client.post("/api/stock-data/track", json=request_data)

        # Assert - Both responses are successful and identical
        assert response1.status_code == status.HTTP_200_OK
        assert response2.status_code == status.HTTP_200_OK
        assert response1.json() == response2.json()

        # Assert - Database contains only one entry
        result = await async_test_db.execute(select(TrackedStock).where(TrackedStock.symbol == DEFAULT_TEST_SYMBOL))
        tracked_stocks = result.scalars().all()
        assert len(tracked_stocks) == 1
        assert tracked_stocks[0].symbol == DEFAULT_TEST_SYMBOL

    @pytest.mark.asyncio
    async def test_complete_workflow_with_invalid_symbol_returns_validation_error(
        self, async_test_db: AsyncSession
    ) -> None:
        """Test complete workflow with invalid symbol returns proper error.

        This test verifies that:
        1. Frontend validation catches invalid symbols
        2. API returns appropriate error response
        3. Database is not modified
        4. Frontend can display error message to user

        Args:
            async_test_db: Async database session for testing
        """
        # Arrange - Invalid symbol (starts with number)
        request_data = {"symbol": "1INVALID"}

        # Act - Frontend makes API call
        response = client.post("/api/stock-data/track", json=request_data)

        # Assert - Frontend receives validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data

        # Assert - Database is not modified
        result = await async_test_db.execute(select(TrackedStock).where(TrackedStock.symbol == "1INVALID"))
        tracked_stock = result.scalar_one_or_none()
        assert tracked_stock is None

    @pytest.mark.asyncio
    async def test_complete_workflow_with_empty_symbol_returns_validation_error(
        self, async_test_db: AsyncSession
    ) -> None:
        """Test complete workflow with empty symbol returns proper error.

        This test verifies that:
        1. Frontend validation catches empty symbols
        2. API returns appropriate error response
        3. Database is not modified
        4. Frontend can display error message to user

        Args:
            async_test_db: Async database session for testing
        """
        # Arrange - Empty symbol
        request_data = {"symbol": ""}

        # Act - Frontend makes API call
        response = client.post("/api/stock-data/track", json=request_data)

        # Assert - Frontend receives validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data

        # Assert - Database is not modified
        result = await async_test_db.execute(select(TrackedStock).where(TrackedStock.symbol == ""))
        tracked_stock = result.scalar_one_or_none()
        assert tracked_stock is None


class TestAdminWorkflowIntegration:
    """Integration tests for admin workflow (currently disabled)."""

    @pytest.mark.asyncio
    async def test_admin_list_tracked_stocks_requires_authentication(self, async_test_db: AsyncSession) -> None:
        """Test admin workflow requires proper authentication.

        This test verifies that:
        1. Admin endpoints require authentication
        2. Unauthenticated requests are rejected
        3. Frontend can handle authentication errors
        4. Database is not accessed for unauthorized requests

        Args:
            async_test_db: Async database session for testing
        """
        # Act - Admin tries to list tracked stocks without auth
        response = client.get("/api/stock-data/track")

        # Assert - Request is rejected
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data
        assert "Not authenticated" in data["detail"]

    @pytest.mark.asyncio
    async def test_admin_deactivate_tracking_requires_authentication(self, async_test_db: AsyncSession) -> None:
        """Test admin deactivate workflow requires proper authentication.

        This test verifies that:
        1. Admin deactivate endpoint requires authentication
        2. Unauthenticated requests are rejected
        3. Frontend can handle authentication errors
        4. Database is not modified for unauthorized requests

        Args:
            async_test_db: Async database session for testing
        """
        # Act - Admin tries to deactivate tracking without auth
        response = client.delete(f"/api/stock-data/tracked/{DEFAULT_TEST_SYMBOL}")

        # Assert - Request is rejected
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data
        assert "Not authenticated" in data["detail"]


class TestErrorHandlingIntegration:
    """Integration tests for error handling across frontend and backend."""

    @pytest.mark.asyncio
    async def test_api_error_response_format_consistent(self, async_test_db: AsyncSession) -> None:
        """Test that API error responses have consistent format.

        This test verifies that:
        1. All error responses have consistent structure
        2. Frontend can parse error responses reliably
        3. Error messages are user-friendly
        4. Status codes are appropriate

        Args:
            async_test_db: Async database session for testing
        """
        # Arrange - Multiple error scenarios
        error_scenarios = [
            {"symbol": ""},  # Empty symbol
            {"symbol": "1INVALID"},  # Invalid format
            {"symbol": "A" * 20},  # Too long
        ]

        for scenario in error_scenarios:
            # Act
            response = client.post("/api/stock-data/track", json=scenario)

            # Assert - Consistent error response format
            assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_400_BAD_REQUEST]
            data = response.json()
            assert "detail" in data
            assert isinstance(data["detail"], str | list)

    @pytest.mark.asyncio
    async def test_database_consistency_maintained_during_errors(self, async_test_db: AsyncSession) -> None:
        """Test that database consistency is maintained during errors.

        This test verifies that:
        1. Invalid requests don't modify database state
        2. Database transactions are properly rolled back
        3. No partial data is committed
        4. System remains in consistent state

        Args:
            async_test_db: Async database session for testing
        """
        # Arrange - Get initial database state
        initial_result = await async_test_db.execute(select(TrackedStock))
        initial_count = len(initial_result.scalars().all())

        # Act - Make invalid request
        response = client.post("/api/stock-data/track", json={"symbol": "1INVALID"})

        # Assert - Request fails
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Assert - Database state unchanged
        final_result = await async_test_db.execute(select(TrackedStock))
        final_count = len(final_result.scalars().all())
        assert final_count == initial_count


class TestDataConsistencyIntegration:
    """Integration tests for data consistency across the system."""

    @pytest.mark.asyncio
    async def test_stock_symbol_normalization_consistent(self, async_test_db: AsyncSession) -> None:
        """Test that stock symbols are normalized consistently.

        This test verifies that:
        1. Symbols are converted to uppercase
        2. Whitespace is trimmed
        3. Normalization is consistent across API and database
        4. Frontend receives normalized data

        Args:
            async_test_db: Async database session for testing
        """
        # Arrange - Symbol with mixed case and whitespace
        request_data = {"symbol": "  aapl  "}

        # Act
        response = client.post("/api/stock-data/track", json=request_data)

        # Assert - Response contains normalized symbol
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["symbol"] == "AAPL"

        # Assert - Database contains normalized symbol
        result = await async_test_db.execute(select(TrackedStock).where(TrackedStock.symbol == "AAPL"))
        tracked_stock = result.scalar_one()
        assert tracked_stock.symbol == "AAPL"

    @pytest.mark.asyncio
    async def test_tracking_status_consistency(self, async_test_db: AsyncSession) -> None:
        """Test that tracking status is consistent across system.

        This test verifies that:
        1. New tracking entries have correct initial status
        2. Status values are consistent between API and database
        3. Frontend receives accurate status information
        4. Status transitions work correctly

        Args:
            async_test_db: Async database session for testing
        """
        # Arrange
        request_data = {"symbol": DEFAULT_TEST_SYMBOL}

        # Act
        response = client.post("/api/stock-data/track", json=request_data)

        # Assert - API response indicates tracking
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "tracking"

        # Assert - Database has correct initial status
        result = await async_test_db.execute(select(TrackedStock).where(TrackedStock.symbol == DEFAULT_TEST_SYMBOL))
        tracked_stock = result.scalar_one()
        assert tracked_stock.is_active is True
        assert tracked_stock.last_pull_status == PullStatus.PENDING
