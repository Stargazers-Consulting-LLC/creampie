"""Tests for stock data schemas.

This module contains comprehensive tests for the Pydantic schemas used in
stock tracking functionality, including validation, serialization, and
integration tests.

References:
    - [Pytest Documentation](https://docs.pytest.org/)
    - [Pydantic Testing](https://docs.pydantic.dev/usage/testing/)
    - [Python Type Hints](https://docs.python.org/3/library/typing.html)

### Legal
SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from cream_api.stock_data.schemas import (
    PullStatus,
    StockRequestCreate,
    StockRequestResponse,
    StockTrackingUpdate,
    TrackedStockListResponse,
)

# Test constants
EXPECTED_STOCK_COUNT = 2
DEFAULT_PAGE_SIZE = 10


class TestStockRequestCreate:
    """Test cases for StockRequestCreate schema."""

    def test_valid_symbol_uppercase_letters(self) -> None:
        """Test that valid uppercase letter symbols are accepted."""
        data = {"symbol": "AAPL"}
        request = StockRequestCreate(**data)
        assert request.symbol == "AAPL"

    def test_valid_symbol_with_digits(self) -> None:
        """Test that valid symbols with digits are accepted."""
        data = {"symbol": "GOOGL"}
        request = StockRequestCreate(**data)
        assert request.symbol == "GOOGL"

    def test_symbol_converted_to_uppercase(self) -> None:
        """Test that lowercase symbols are converted to uppercase."""
        data = {"symbol": "aapl"}
        request = StockRequestCreate(**data)
        assert request.symbol == "AAPL"

    def test_lowercase_symbols_are_valid(self) -> None:
        """Test that lowercase symbols are converted to uppercase and accepted."""
        data = {"symbol": "aa"}
        request = StockRequestCreate(**data)
        assert request.symbol == "AA"

    def test_symbol_whitespace_rejected(self) -> None:
        """Test that symbols with whitespace are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            StockRequestCreate(symbol="  AAPL  ")

        error = exc_info.value
        assert len(error.errors()) == 1
        assert error.errors()[0]["type"] == "value_error"
        assert "whitespace" in str(error.errors()[0]["msg"])

    def test_symbol_mixed_case_converted(self) -> None:
        """Test that mixed case symbols are converted to uppercase."""
        data = {"symbol": "AaPl"}
        request = StockRequestCreate(**data)
        assert request.symbol == "AAPL"

    def test_symbol_with_digits_valid(self) -> None:
        """Test that symbols with digits are valid."""
        data = {"symbol": "BRK1"}
        request = StockRequestCreate(**data)
        assert request.symbol == "BRK1"

    def test_symbol_max_length_valid(self) -> None:
        """Test that symbols at maximum length are valid."""
        data = {"symbol": "ABCDEFGHIJ"}
        request = StockRequestCreate(**data)
        assert request.symbol == "ABCDEFGHIJ"

    def test_symbol_min_length_valid(self) -> None:
        """Test that two character symbols are valid."""
        data = {"symbol": "AA"}
        request = StockRequestCreate(**data)
        assert request.symbol == "AA"

    @pytest.mark.parametrize(
        "invalid_symbol",
        [
            "123",  # Starts with digit
            "AAPL!",  # Contains special character
            "AAPL-",  # Contains hyphen
            "AAPL_",  # Contains underscore
            "1AAPL",  # Starts with digit
            "AAPL1!",  # Contains special character
        ],
    )
    def test_invalid_symbols_rejected(self, invalid_symbol: str) -> None:
        """Test that invalid symbols are rejected with appropriate errors."""
        with pytest.raises(ValidationError) as exc_info:
            StockRequestCreate(symbol=invalid_symbol)

        error = exc_info.value
        assert len(error.errors()) == 1
        # Handle different error types for Pydantic v2
        error_type = error.errors()[0]["type"]
        assert error_type in ["value_error", "string_too_short", "string_too_long"]

    @pytest.mark.parametrize(
        "invalid_symbol",
        [
            "",  # Empty string
            "ABCDEFGHIJK",  # Too long (11 characters)
        ],
    )
    def test_invalid_symbols_rejected_field_validation(self, invalid_symbol: str) -> None:
        """Test that invalid symbols are rejected by Field validation."""
        with pytest.raises(ValidationError) as exc_info:
            StockRequestCreate(symbol=invalid_symbol)

        error = exc_info.value
        assert len(error.errors()) == 1
        error_type = error.errors()[0]["type"]
        assert error_type in ["string_too_short", "string_too_long"]

    @pytest.mark.parametrize(
        "invalid_symbol",
        [
            "AAPL ",  # Contains space
            "AAPL\n",  # Contains newline
            "AAPL\t",  # Contains tab
        ],
    )
    def test_invalid_symbols_rejected_custom_validation(self, invalid_symbol: str) -> None:
        """Test that invalid symbols are rejected by custom validation."""
        with pytest.raises(ValidationError) as exc_info:
            StockRequestCreate(symbol=invalid_symbol)

        error = exc_info.value
        assert len(error.errors()) == 1
        assert error.errors()[0]["type"] == "value_error"

    def test_symbol_starting_with_digit_rejected(self) -> None:
        """Test that symbols starting with digits are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            StockRequestCreate(symbol="1AAPL")

        error = exc_info.value
        assert len(error.errors()) == 1
        assert "must start with a letter" in str(error.errors()[0]["msg"])

    def test_symbol_with_special_characters_rejected(self) -> None:
        """Test that symbols with special characters are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            StockRequestCreate(symbol="AAPL!")

        error = exc_info.value
        assert len(error.errors()) == 1
        assert "uppercase letters (A-Z) and digits (0-9)" in str(error.errors()[0]["msg"])


class TestStockRequestResponse:
    """Test cases for StockRequestResponse schema."""

    def test_valid_response_creation(self) -> None:
        """Test creating a valid response with all required fields."""
        response = StockRequestResponse(
            id="123e4567-e89b-12d3-a456-426614174000",
            symbol="AAPL",
            is_active=True,
            last_pull_date=None,
            last_pull_status=PullStatus.SUCCESS,
            error_message=None,
            created_at=datetime.now(),
        )
        assert response.id == "123e4567-e89b-12d3-a456-426614174000"
        assert response.symbol == "AAPL"
        assert response.is_active is True
        assert response.last_pull_status == PullStatus.SUCCESS

    def test_response_with_optional_fields(self) -> None:
        """Test creating a response with optional fields."""
        now = datetime.now()
        response = StockRequestResponse(
            id="123e4567-e89b-12d3-a456-426614174000",
            symbol="AAPL",
            is_active=True,
            last_pull_date=now,
            last_pull_status=PullStatus.SUCCESS,
            error_message="Some error occurred",
            created_at=now,
        )
        assert response.last_pull_date is not None
        assert response.error_message == "Some error occurred"

    def test_response_without_optional_fields(self) -> None:
        """Test creating a response without optional fields."""
        response = StockRequestResponse(
            id="123e4567-e89b-12d3-a456-426614174000",
            symbol="AAPL",
            is_active=False,
            last_pull_date=None,
            last_pull_status=PullStatus.PENDING,
            error_message=None,
            created_at=datetime.now(),
        )
        assert response.last_pull_date is None
        assert response.error_message is None

    def test_response_from_orm_model(self) -> None:
        """Test creating response from ORM model attributes."""

        # Simulate ORM model with attributes
        class MockTrackedStock:
            def __init__(self) -> None:
                self.id = "123e4567-e89b-12d3-a456-426614174000"
                self.symbol = "AAPL"
                self.is_active = True
                self.last_pull_date = datetime.now()
                self.last_pull_status = PullStatus.SUCCESS
                self.error_message = None
                self.created_at = datetime.now()

        mock_model = MockTrackedStock()
        response = StockRequestResponse.model_validate(mock_model)
        assert response.id == mock_model.id
        assert response.symbol == mock_model.symbol

    def test_disabled_status_works_correctly(self) -> None:
        """Test that DISABLED status works correctly in responses."""
        response = StockRequestResponse(
            id="123e4567-e89b-12d3-a456-426614174000",
            symbol="AAPL",
            is_active=False,
            last_pull_date=None,
            last_pull_status=PullStatus.DISABLED,
            error_message=None,
            created_at=datetime.now(),
        )
        assert response.last_pull_status == PullStatus.DISABLED
        assert response.is_active is False


class TestTrackedStockListResponse:
    """Test cases for TrackedStockListResponse schema."""

    def test_valid_list_response_creation(self) -> None:
        """Test creating a valid list response."""
        stock_responses = [
            StockRequestResponse(
                id="123e4567-e89b-12d3-a456-426614174000",
                symbol="AAPL",
                is_active=True,
                last_pull_date=None,
                last_pull_status=PullStatus.SUCCESS,
                error_message=None,
                created_at=datetime.now(),
            ),
            StockRequestResponse(
                id="123e4567-e89b-12d3-a456-426614174001",
                symbol="TSLA",
                is_active=True,
                last_pull_date=None,
                last_pull_status=PullStatus.SUCCESS,
                error_message=None,
                created_at=datetime.now(),
            ),
        ]

        response = TrackedStockListResponse(
            stocks=stock_responses,
            total_count=EXPECTED_STOCK_COUNT,
            page=1,
            page_size=DEFAULT_PAGE_SIZE,
            total_pages=1,
        )
        assert len(response.stocks) == EXPECTED_STOCK_COUNT
        assert response.total_count == EXPECTED_STOCK_COUNT
        assert response.page == 1
        assert response.page_size == DEFAULT_PAGE_SIZE
        assert response.total_pages == 1

    def test_empty_list_response(self) -> None:
        """Test creating a list response with no stocks."""
        response = TrackedStockListResponse(
            stocks=[],
            total_count=0,
            page=1,
            page_size=DEFAULT_PAGE_SIZE,
            total_pages=0,
        )
        assert len(response.stocks) == 0
        assert response.total_count == 0
        assert response.total_pages == 0


class TestStockTrackingUpdate:
    """Test cases for StockTrackingUpdate schema."""

    def test_valid_update_all_fields(self) -> None:
        """Test creating a valid update with all fields."""
        update = StockTrackingUpdate(
            is_active=False,
            last_pull_status=PullStatus.FAILED,
            error_message="API rate limit exceeded",
        )
        assert update.is_active is False
        assert update.last_pull_status == PullStatus.FAILED
        assert update.error_message == "API rate limit exceeded"

    def test_valid_update_without_error_message(self) -> None:
        """Test creating a valid update without error message."""
        update = StockTrackingUpdate(
            is_active=True,
            last_pull_status=PullStatus.SUCCESS,
            error_message=None,
        )
        assert update.is_active is True
        assert update.last_pull_status == PullStatus.SUCCESS
        assert update.error_message is None

    @pytest.mark.parametrize(
        "valid_status", [PullStatus.PENDING, PullStatus.SUCCESS, PullStatus.FAILED, PullStatus.DISABLED]
    )
    def test_valid_pull_status_accepted(self, valid_status: PullStatus) -> None:
        """Test that valid pull status values are accepted."""
        update = StockTrackingUpdate(
            is_active=True,
            last_pull_status=valid_status,
            error_message=None,
        )
        assert update.last_pull_status == valid_status


class TestSchemaIntegration:
    """Integration tests for schema interactions."""

    def test_create_to_response_flow(self) -> None:
        """Test the flow from create request to response."""
        # Create request
        create_request = StockRequestCreate(symbol="AAPL")

        # Simulate processing and create response
        response = StockRequestResponse(
            id="123e4567-e89b-12d3-a456-426614174000",
            symbol=create_request.symbol,
            is_active=True,
            last_pull_date=None,
            last_pull_status=PullStatus.PENDING,
            error_message=None,
            created_at=datetime.now(),
        )

        assert response.symbol == "AAPL"
        assert response.is_active is True

    def test_update_flow(self) -> None:
        """Test updating a tracked stock."""
        # Initial state
        initial_response = StockRequestResponse(
            id="123e4567-e89b-12d3-a456-426614174000",
            symbol="AAPL",
            is_active=True,
            last_pull_date=None,
            last_pull_status=PullStatus.PENDING,
            error_message=None,
            created_at=datetime.now(),
        )

        # Update request
        update = StockTrackingUpdate(
            is_active=False,
            last_pull_status=PullStatus.FAILED,
            error_message="API error",
        )

        # Simulate applying update
        updated_response = StockRequestResponse(
            id=initial_response.id,
            symbol=initial_response.symbol,
            is_active=update.is_active,
            last_pull_date=None,
            last_pull_status=update.last_pull_status,
            error_message=update.error_message,
            created_at=initial_response.created_at,
        )

        assert updated_response.is_active is False
        assert updated_response.last_pull_status == PullStatus.FAILED
        assert updated_response.error_message == "API error"
