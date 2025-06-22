"""Tests for stock data schemas.

This module contains tests for the Pydantic schemas used in the stock data module.
It follows the testing best practices outlined in the Backend Style Guide.

References:
    - [Pydantic Testing](https://docs.pydantic.dev/latest/usage/testing/)
    - [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

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
from cream_api.tests.stock_data.stock_data_test_constants import DEFAULT_PAGE_SIZE

# Test constants
EXPECTED_STOCK_COUNT = 2


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

    def test_symbol_whitespace_trimmed(self) -> None:
        """Test that symbols with whitespace are trimmed."""
        data = {"symbol": "  AAPL  "}
        request = StockRequestCreate(**data)
        assert request.symbol == "AAPL"

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
            "AAPL!",  # Contains special character
            "AAPL-",  # Contains hyphen
            "AAPL_",  # Contains underscore
            "1AAPL",  # Starts with digit
            "AAPL1!",  # Contains special character
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

    def test_symbol_length_exactly_one_character(self) -> None:
        """Test that single character symbols are rejected (minimum is 2)."""
        with pytest.raises(ValidationError) as exc_info:
            StockRequestCreate(symbol="A")

        error = exc_info.value
        assert len(error.errors()) == 1
        assert "must be 2-10 characters long" in str(error.errors()[0]["msg"])

    def test_symbol_length_exactly_max_length(self) -> None:
        """Test that symbols at exactly maximum length are accepted."""
        data = {"symbol": "ABCDEFGHIJ"}  # 10 characters
        request = StockRequestCreate(**data)
        assert request.symbol == "ABCDEFGHIJ"

    def test_symbol_length_one_over_max_rejected(self) -> None:
        """Test that symbols one character over maximum length are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            StockRequestCreate(symbol="ABCDEFGHIJK")  # 11 characters

        error = exc_info.value
        assert len(error.errors()) == 1
        # Field validation happens before custom validation, so we get the field error
        assert "String should have at most 10 characters" in str(error.errors()[0]["msg"])

    def test_symbol_with_lowercase_letters_converted(self) -> None:
        """Test that symbols with lowercase letters are converted to uppercase."""
        data = {"symbol": "aBcDeF"}
        request = StockRequestCreate(**data)
        assert request.symbol == "ABCDEF"

    def test_symbol_with_mixed_case_and_digits(self) -> None:
        """Test that symbols with mixed case and digits are properly converted."""
        data = {"symbol": "aB1cD2eF"}
        request = StockRequestCreate(**data)
        assert request.symbol == "AB1CD2EF"

    def test_symbol_with_only_digits_rejected(self) -> None:
        """Test that symbols with only digits are rejected (must start with letter)."""
        with pytest.raises(ValidationError) as exc_info:
            StockRequestCreate(symbol="12345")

        error = exc_info.value
        assert len(error.errors()) == 1
        assert "must start with a letter" in str(error.errors()[0]["msg"])

    def test_symbol_with_leading_whitespace_trimmed(self) -> None:
        """Test that symbols with leading whitespace are trimmed."""
        data = {"symbol": " AAPL"}
        request = StockRequestCreate(**data)
        assert request.symbol == "AAPL"

    def test_symbol_with_trailing_whitespace_trimmed(self) -> None:
        """Test that symbols with trailing whitespace are trimmed."""
        data = {"symbol": "AAPL "}
        request = StockRequestCreate(**data)
        assert request.symbol == "AAPL"

    def test_symbol_with_newline_trimmed(self) -> None:
        """Test that symbols with newline characters are trimmed."""
        data = {"symbol": "AAPL\n"}
        request = StockRequestCreate(**data)
        assert request.symbol == "AAPL"

    def test_symbol_with_tab_trimmed(self) -> None:
        """Test that symbols with tab characters are trimmed."""
        data = {"symbol": "AAPL\t"}
        request = StockRequestCreate(**data)
        assert request.symbol == "AAPL"

    def test_symbol_with_multiple_whitespace_characters_trimmed(self) -> None:
        """Test that symbols with multiple whitespace characters are trimmed."""
        data = {"symbol": "AAPL \n\t"}
        request = StockRequestCreate(**data)
        assert request.symbol == "AAPL"


class TestStockRequestResponse:
    """Test cases for StockRequestResponse schema."""

    def test_valid_response_creation(self) -> None:
        """Test creating a valid response with all required fields."""
        now = datetime.now()
        response = StockRequestResponse(
            id="123e4567-e89b-12d3-a456-426614174000",
            symbol="AAPL",
            is_active=True,
            last_pull_date=now,
            last_pull_status=PullStatus.SUCCESS,
            error_message=None,
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
        )
        assert response.last_pull_date == now
        assert response.error_message == "Some error occurred"

    def test_response_without_optional_fields(self) -> None:
        """Test creating a response without optional fields."""
        now = datetime.now()
        response = StockRequestResponse(
            id="123e4567-e89b-12d3-a456-426614174000",
            symbol="AAPL",
            is_active=True,
            last_pull_date=now,
            last_pull_status=PullStatus.PENDING,
            error_message=None,
        )
        assert response.last_pull_date == now
        assert response.error_message is None

    def test_response_from_orm_model(self) -> None:
        """Test creating response from ORM model."""
        now = datetime.now()
        mock_data = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "symbol": "AAPL",
            "is_active": True,
            "last_pull_date": now,
            "last_pull_status": "success",
            "error_message": None,
        }

        response = StockRequestResponse.model_validate(mock_data)
        assert response.symbol == "AAPL"
        assert response.last_pull_status == PullStatus.SUCCESS

    def test_disabled_status_works_correctly(self) -> None:
        """Test that disabled status is handled correctly."""
        now = datetime.now()
        response = StockRequestResponse(
            id="123e4567-e89b-12d3-a456-426614174000",
            symbol="AAPL",
            is_active=False,
            last_pull_date=now,
            last_pull_status=PullStatus.DISABLED,
            error_message=None,
        )
        assert response.is_active is False
        assert response.last_pull_status == PullStatus.DISABLED


class TestTrackedStockListResponse:
    """Test cases for TrackedStockListResponse schema."""

    def test_valid_list_response_creation(self) -> None:
        """Test creating a valid list response."""
        now = datetime.now()
        stocks = [
            StockRequestResponse(
                id="1",
                symbol="AAPL",
                is_active=True,
                last_pull_date=now,
                last_pull_status=PullStatus.SUCCESS,
                error_message=None,
            ),
            StockRequestResponse(
                id="2",
                symbol="TSLA",
                is_active=True,
                last_pull_date=now,
                last_pull_status=PullStatus.SUCCESS,
                error_message=None,
            ),
        ]

        response = TrackedStockListResponse(
            stocks=stocks,
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
        """Test creating an empty list response."""
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
        """Test that all valid pull statuses are accepted."""
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
        create_request = StockRequestCreate(symbol="AAPL")
        assert create_request.symbol == "AAPL"

        now = datetime.now()
        response = StockRequestResponse(
            id="123e4567-e89b-12d3-a456-426614174000",
            symbol=create_request.symbol,
            is_active=True,
            last_pull_date=now,
            last_pull_status=PullStatus.PENDING,
            error_message=None,
        )
        assert response.symbol == create_request.symbol
        assert response.last_pull_status == PullStatus.PENDING

    def test_update_flow(self) -> None:
        """Test the update flow."""
        now = datetime.now()
        original_response = StockRequestResponse(
            id="123e4567-e89b-12d3-a456-426614174000",
            symbol="AAPL",
            is_active=True,
            last_pull_date=now,
            last_pull_status=PullStatus.PENDING,
            error_message=None,
        )

        update = StockTrackingUpdate(
            is_active=False,
            last_pull_status=PullStatus.SUCCESS,
            error_message=None,
        )

        # Simulate updating the response
        updated_response = StockRequestResponse(
            id=original_response.id,
            symbol=original_response.symbol,
            is_active=update.is_active,
            last_pull_date=original_response.last_pull_date,
            last_pull_status=update.last_pull_status,
            error_message=update.error_message,
        )

        assert updated_response.is_active is False
        assert updated_response.last_pull_status == PullStatus.SUCCESS
        assert updated_response.error_message is None
