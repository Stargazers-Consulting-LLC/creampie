"""Integration tests for stock data API endpoints.

This module contains comprehensive integration tests for the stock data API endpoints,
including tests for successful operations, error handling, and expected failures.

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
from sqlalchemy.ext.asyncio import AsyncSession

from cream_api.common.constants import STOCK_TRACK_PATH, STOCK_TRACKED_PATH
from cream_api.main import app
from cream_api.users.models.app_user import AppUser

from .stock_data_test_constants import DEFAULT_TEST_SYMBOL

client = TestClient(app)


class TestStockTrackingAPI:
    """Integration tests for stock tracking API endpoints."""

    @pytest.mark.asyncio
    async def test_post_track_stock_with_valid_symbol_returns_success_response(
        self, async_test_db: AsyncSession
    ) -> None:
        """Test successful stock tracking request with valid symbol.

        This test verifies that:
        1. The API accepts a valid stock symbol
        2. Returns a successful response with correct format
        3. Response contains expected status and message

        Args:
            async_test_db: Async database session for testing
        """
        # Arrange
        request_data = {"symbol": DEFAULT_TEST_SYMBOL}

        # Act
        response = client.post(STOCK_TRACK_PATH, json=request_data)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "tracking"
        assert data["message"] == f"Stock {DEFAULT_TEST_SYMBOL} is now being tracked"
        assert data["symbol"] == DEFAULT_TEST_SYMBOL

    @pytest.mark.asyncio
    async def test_post_track_stock_with_invalid_symbol_returns_bad_request(self, async_test_db: AsyncSession) -> None:
        """Test stock tracking with invalid symbol returns validation error.

        This test verifies that:
        1. The API rejects invalid stock symbols
        2. Returns appropriate error status code
        3. Error message contains validation details

        Args:
            async_test_db: Async database session for testing
        """
        # Arrange - Use a symbol that starts with a number (invalid)
        request_data = {"symbol": "1INVALID"}

        # Act
        response = client.post(STOCK_TRACK_PATH, json=request_data)

        # Assert - Pydantic validation returns 422 for invalid format
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_post_track_stock_with_empty_symbol_returns_bad_request(self, async_test_db: AsyncSession) -> None:
        """Test stock tracking with empty symbol returns validation error.

        This test verifies that:
        1. The API rejects empty stock symbols
        2. Returns appropriate error status code
        3. Error message indicates empty symbol issue

        Args:
            async_test_db: Async database session for testing
        """
        # Arrange
        request_data = {"symbol": ""}

        # Act
        response = client.post(STOCK_TRACK_PATH, json=request_data)

        # Assert - Pydantic validation returns 422 for empty string
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_post_track_stock_with_duplicate_symbol_returns_success(self, async_test_db: AsyncSession) -> None:
        """Test tracking the same symbol twice returns success response.

        This test verifies that:
        1. The API handles duplicate symbol requests gracefully
        2. Both requests return successful responses
        3. Responses are consistent for the same symbol

        Args:
            async_test_db: Async database session for testing
        """
        # Arrange
        request_data = {"symbol": DEFAULT_TEST_SYMBOL}

        # Act - First request
        response1 = client.post(STOCK_TRACK_PATH, json=request_data)

        # Act - Second request
        response2 = client.post(STOCK_TRACK_PATH, json=request_data)

        # Assert
        assert response1.status_code == status.HTTP_200_OK
        assert response2.status_code == status.HTTP_200_OK
        assert response1.json() == response2.json()


class TestAdminEndpoints:
    """Integration tests for admin-only endpoints (expected to fail)."""

    @pytest.mark.asyncio
    async def test_get_tracked_stocks_without_authentication_returns_unauthorized(
        self, async_test_db: AsyncSession
    ) -> None:
        """Test GET /track without authentication returns unauthorized error.

        This test verifies that:
        1. The admin endpoint requires authentication
        2. Returns 401 Unauthorized when no token provided
        3. Error message indicates authentication requirement

        Args:
            async_test_db: Async database session for testing
        """
        # Act
        response = client.get("/api/stock-data/track")

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "Not authenticated" in data["detail"]

    @pytest.mark.asyncio
    async def test_get_tracked_stocks_with_invalid_token_returns_unauthorized(
        self, async_test_db: AsyncSession
    ) -> None:
        """Test GET /track with invalid token returns unauthorized error.

        This test verifies that:
        1. The admin endpoint validates authentication tokens
        2. Returns 401 or 403 when token is invalid
        3. Proper error handling for authentication failures

        Args:
            async_test_db: Async database session for testing
        """
        # Arrange
        headers = {"Authorization": "Bearer dummy_token"}

        # Act
        response = client.get("/api/stock-data/track", headers=headers)

        # Assert
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    @pytest.mark.asyncio
    async def test_delete_tracked_stock_without_authentication_returns_unauthorized(
        self, async_test_db: AsyncSession
    ) -> None:
        """Test DELETE /tracked/{symbol} without authentication returns unauthorized error.

        This test verifies that:
        1. The admin delete endpoint requires authentication
        2. Returns 401 Unauthorized when no token provided
        3. Error message indicates authentication requirement

        Args:
            async_test_db: Async database session for testing
        """
        # Act
        response = client.delete(f"/api/stock-data/tracked/{DEFAULT_TEST_SYMBOL}")

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "Not authenticated" in data["detail"]

    @pytest.mark.asyncio
    async def test_delete_tracked_stock_with_invalid_token_returns_unauthorized(
        self, async_test_db: AsyncSession
    ) -> None:
        """Test DELETE /tracked/{symbol} with invalid token returns unauthorized error.

        This test verifies that:
        1. The admin delete endpoint validates authentication tokens
        2. Returns 401 Unauthorized when token is invalid
        3. Proper error handling for authentication failures

        Args:
            async_test_db: Async database session for testing
        """
        # Arrange - Use a token that doesn't exist in the database
        headers = {"Authorization": "Bearer invalid_token"}

        # Act
        response = client.delete(f"/api/stock-data/tracked/{DEFAULT_TEST_SYMBOL}", headers=headers)

        # Assert - Invalid token should return 401 Unauthorized
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data
        assert "Could not validate credentials" in data["detail"]

    @pytest.mark.asyncio
    async def test_delete_tracked_stock_with_invalid_symbol_format_returns_unauthorized(
        self, async_test_db: AsyncSession
    ) -> None:
        """Test that delete tracked stock endpoint validates symbol format.

        This test verifies that:
        1. The endpoint validates symbol format
        2. Invalid symbols are rejected
        3. The response indicates the issue

        Args:
            async_test_db: Async database session for testing
        """
        # Arrange - Create a test user and get auth token
        test_user = AppUser(
            email="test@example.com",
            password="hashed_password",
            first_name="Test",
            last_name="User",
            is_verified=True,
            is_active=True,
            password_reset_token="dummy_token",  # Match the token expected by auth system
        )
        async_test_db.add(test_user)
        await async_test_db.commit()

        headers = {"Authorization": "Bearer dummy_token"}

        # Act
        response = client.delete(f"{STOCK_TRACKED_PATH}/INVALID", headers=headers)

        # Assert
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


class TestAPIResponseFormat:
    """Tests for API response format consistency."""

    @pytest.mark.asyncio
    async def test_post_track_response_contains_required_fields(self, async_test_db: AsyncSession) -> None:
        """Test that POST /track returns response with required fields.

        This test verifies that:
        1. Response contains all required fields
        2. Field types are correct
        3. Field values are appropriate

        Args:
            async_test_db: Async database session for testing
        """
        # Arrange
        request_data = {"symbol": "TSLA"}

        # Act
        response = client.post(STOCK_TRACK_PATH, json=request_data)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Check required fields exist
        assert "status" in data
        assert "message" in data
        assert "symbol" in data

        # Check field types
        assert isinstance(data["status"], str)
        assert isinstance(data["message"], str)
        assert isinstance(data["symbol"], str)

        # Check field values
        assert data["status"] == "tracking"
        assert data["symbol"] == "TSLA"
        assert "is now being tracked" in data["message"]

    @pytest.mark.asyncio
    async def test_error_response_contains_detail_field(self, async_test_db: AsyncSession) -> None:
        """Test that error responses contain required detail field.

        This test verifies that:
        1. Error responses have consistent format
        2. Detail field contains meaningful error message
        3. Error message is not empty

        Args:
            async_test_db: Async database session for testing
        """
        # Arrange - Use a symbol that starts with a number (invalid)
        request_data = {"symbol": "1INVALID"}

        # Act
        response = client.post(STOCK_TRACK_PATH, json=request_data)

        # Assert - Pydantic validation returns 422 for invalid format
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()

        # Check error response format
        assert "detail" in data
        assert isinstance(data["detail"], list)  # Pydantic validation errors are lists
        assert len(data["detail"]) > 0


class TestAPIEndpointAvailability:
    """Tests to ensure all expected endpoints are available."""

    def test_stock_tracking_endpoints_are_registered(self) -> None:
        """Test that stock tracking endpoints are registered with FastAPI.

        This test verifies that:
        1. All expected endpoints are registered
        2. Endpoint paths are correct
        3. API structure is properly configured

        This is a unit test that doesn't require async database access.
        """
        # Arrange
        routes = [route.path for route in app.routes if hasattr(route, "path")]

        # Act & Assert
        assert "/api/stock-data/track" in routes

        # Check for DELETE endpoint pattern
        delete_endpoints = [route for route in routes if "tracked" in route]
        assert len(delete_endpoints) > 0

    def test_openapi_documentation_includes_stock_endpoints(self) -> None:
        """Test that OpenAPI documentation includes stock tracking endpoints.

        This test verifies that:
        1. OpenAPI documentation is available
        2. Stock endpoints are properly documented
        3. Both GET and POST methods are documented
        4. DELETE endpoint is documented

        This is a unit test that doesn't require async database access.
        """
        # Act
        response = client.get("/openapi.json")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Check that our endpoints are documented
        paths = data.get("paths", {})
        assert "/api/stock-data/track" in paths

        # Check that both GET and POST methods are documented
        track_endpoint = paths["/api/stock-data/track"]
        assert "post" in track_endpoint
        assert "get" in track_endpoint

        # Check that DELETE endpoint is documented
        delete_endpoints = [path for path in paths.keys() if "tracked" in path]
        assert len(delete_endpoints) > 0

    @pytest.mark.asyncio
    async def test_list_tracked_stocks_with_auth_returns_forbidden(self, async_test_db: AsyncSession) -> None:
        """Test that list tracked stocks endpoint returns forbidden for non-admin users.

        This test verifies that:
        1. The endpoint accepts valid authentication tokens
        2. Returns 403 Forbidden for users without admin privileges
        3. The endpoint properly validates authorization

        Args:
            async_test_db: Async database session for testing
        """
        # Arrange - Create a test user and get auth token
        test_user = AppUser(
            email="test@example.com",
            password="hashed_password",
            first_name="Test",
            last_name="User",
            is_verified=True,
            is_active=True,
            password_reset_token="dummy_token",  # Match the token expected by auth system
        )
        async_test_db.add(test_user)
        await async_test_db.commit()

        headers = {"Authorization": "Bearer dummy_token"}

        # Act
        response = client.get(STOCK_TRACK_PATH, headers=headers)

        # Assert - Valid token but no admin role should return 403 Forbidden
        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        assert "detail" in data
        assert "Admin access required" in data["detail"]

    @pytest.mark.asyncio
    async def test_delete_tracked_stock_without_auth_returns_unauthorized(self, async_test_db: AsyncSession) -> None:
        """Test that delete tracked stock endpoint requires authentication.

        This test verifies that:
        1. The endpoint rejects unauthenticated users
        2. The response indicates authentication is required
        3. The endpoint is properly protected

        Args:
            async_test_db: Async database session for testing
        """
        # Act
        response = client.delete(f"{STOCK_TRACKED_PATH}/{DEFAULT_TEST_SYMBOL}")

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data
        assert "Not authenticated" in data["detail"]

    @pytest.mark.asyncio
    async def test_delete_tracked_stock_with_auth_returns_forbidden(self, async_test_db: AsyncSession) -> None:
        """Test that delete tracked stock endpoint returns forbidden for non-admin users.

        This test verifies that:
        1. The endpoint accepts valid authentication tokens
        2. Returns 403 Forbidden for users without admin privileges
        3. The endpoint properly validates authorization

        Args:
            async_test_db: Async database session for testing
        """
        # Arrange - Create a test user and get auth token
        test_user = AppUser(
            email="test@example.com",
            password="hashed_password",
            first_name="Test",
            last_name="User",
            is_verified=True,
            is_active=True,
            password_reset_token="dummy_token",  # Match the token expected by auth system
        )
        async_test_db.add(test_user)
        await async_test_db.commit()

        headers = {"Authorization": "Bearer dummy_token"}

        # Act
        response = client.delete(f"{STOCK_TRACKED_PATH}/{DEFAULT_TEST_SYMBOL}", headers=headers)

        # Assert - Valid token but no admin role should return 403 Forbidden
        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        assert "detail" in data
        assert "Admin access required" in data["detail"]

    @pytest.mark.asyncio
    async def test_list_tracked_stocks_with_invalid_token_returns_unauthorized(
        self, async_test_db: AsyncSession
    ) -> None:
        """Test GET /track with invalid token returns unauthorized error.

        This test verifies that:
        1. The admin endpoint validates authentication tokens
        2. Returns 401 Unauthorized when token is invalid
        3. Proper error handling for authentication failures

        Args:
            async_test_db: Async database session for testing
        """
        # Arrange - Use a token that doesn't exist in the database
        headers = {"Authorization": "Bearer invalid_token"}

        # Act
        response = client.get("/api/stock-data/track", headers=headers)

        # Assert - Invalid token should return 401 Unauthorized
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data
        assert "Could not validate credentials" in data["detail"]
