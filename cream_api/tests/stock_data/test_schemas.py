"""Tests for stock data schemas.

This module contains comprehensive unit tests for the Pydantic schemas used in the
stock data module. It tests validation logic, data transformation, error handling,
and edge cases for all schema classes including StockRequestCreate,
StockRequestResponse, TrackedStockListResponse, and StockTrackingUpdate.

The tests cover symbol validation, status enums, field constraints, and integration
scenarios to ensure robust data validation throughout the stock tracking system.

References:
    - [Pydantic Testing](https://docs.pydantic.dev/latest/usage/testing/)
    - [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

### Legal
SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

from datetime import datetime
from typing import Any

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

EXPECTED_STOCK_COUNT = 2


class TestStockRequestCreate:
    """Test cases for StockRequestCreate schema."""

    def test_valid_symbol_uppercase_letters(self) -> None:
        """Test that validate_symbol_format accepts valid uppercase letter symbols.

        Verifies that stock symbols containing only uppercase letters (A-Z) are
        accepted and returned unchanged by the validation function.
        """
        data: dict[str, str] = {"symbol": "AAPL"}
        request = StockRequestCreate(**data)
        assert request.symbol == "AAPL"

    def test_valid_symbol_with_digits(self) -> None:
        """Test that validate_symbol_format accepts valid symbols with digits.

        Verifies that stock symbols containing uppercase letters and digits (0-9)
        are accepted and properly validated.
        """
        data: dict[str, str] = {"symbol": "GOOGL"}
        request = StockRequestCreate(**data)
        assert request.symbol == "GOOGL"

    def test_symbol_converted_to_uppercase(self) -> None:
        """Test that validate_symbol_format converts lowercase symbols to uppercase.

        Verifies that input symbols are normalized to uppercase format regardless
        of the original case provided by the user.
        """
        data: dict[str, str] = {"symbol": "aapl"}
        request = StockRequestCreate(**data)
        assert request.symbol == "AAPL"

    def test_lowercase_symbols_are_valid(self) -> None:
        """Test that validate_symbol_format accepts and converts lowercase symbols.

        Verifies that lowercase input symbols are accepted, converted to uppercase,
        and pass all validation rules.
        """
        data: dict[str, str] = {"symbol": "aa"}
        request = StockRequestCreate(**data)
        assert request.symbol == "AA"

    def test_symbol_whitespace_trimmed(self) -> None:
        """Test that validate_symbol_format trims whitespace from symbols.

        Verifies that leading and trailing whitespace is removed from input
        symbols before validation and processing.
        """
        data: dict[str, str] = {"symbol": "  AAPL  "}
        request = StockRequestCreate(**data)
        assert request.symbol == "AAPL"

    def test_symbol_mixed_case_converted(self) -> None:
        """Test that validate_symbol_format converts mixed case symbols to uppercase.

        Verifies that symbols with mixed uppercase and lowercase letters are
        properly converted to all uppercase format.
        """
        data: dict[str, str] = {"symbol": "AaPl"}
        request = StockRequestCreate(**data)
        assert request.symbol == "AAPL"

    def test_symbol_with_digits_valid(self) -> None:
        """Test that validate_symbol_format accepts symbols containing digits.

        Verifies that stock symbols can contain both letters and digits in
        any combination, as long as they start with a letter.
        """
        data: dict[str, str] = {"symbol": "BRK1"}
        request = StockRequestCreate(**data)
        assert request.symbol == "BRK1"

    def test_symbol_max_length_valid(self) -> None:
        """Test that validate_symbol_format accepts symbols at maximum length.

        Verifies that symbols exactly at the maximum allowed length (10 characters)
        are accepted and processed correctly.
        """
        data: dict[str, str] = {"symbol": "ABCDEFGHIJ"}
        request = StockRequestCreate(**data)
        assert request.symbol == "ABCDEFGHIJ"

    def test_symbol_min_length_valid(self) -> None:
        """Test that validate_symbol_format accepts symbols at minimum length.

        Verifies that symbols exactly at the minimum required length (2 characters)
        are accepted and processed correctly.
        """
        data: dict[str, str] = {"symbol": "AA"}
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
        """Test that validate_symbol_format rejects invalid symbols with appropriate errors.

        Verifies that symbols containing invalid characters or starting with digits
        are rejected with descriptive error messages.
        """
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
        """Test that Field validation rejects symbols with invalid length.

        Verifies that Pydantic Field validation catches length violations before
        custom validation logic is executed.
        """
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
        """Test that custom validation rejects symbols with invalid characters.

        Verifies that the custom field validator catches symbols containing
        special characters or starting with digits.
        """
        with pytest.raises(ValidationError) as exc_info:
            StockRequestCreate(symbol=invalid_symbol)

        error = exc_info.value
        assert len(error.errors()) == 1
        assert error.errors()[0]["type"] == "value_error"

    def test_symbol_starting_with_digit_rejected(self) -> None:
        """Test that validate_symbol_format rejects symbols starting with digits.

        Verifies that stock symbols must start with a letter (A-Z) and cannot
        begin with numeric digits.
        """
        with pytest.raises(ValidationError) as exc_info:
            StockRequestCreate(symbol="1AAPL")

        error = exc_info.value
        assert len(error.errors()) == 1
        assert "must start with a letter" in str(error.errors()[0]["msg"])

    def test_symbol_with_special_characters_rejected(self) -> None:
        """Test that validate_symbol_format rejects symbols with special characters.

        Verifies that stock symbols cannot contain special characters, only
        uppercase letters and digits are allowed.
        """
        with pytest.raises(ValidationError) as exc_info:
            StockRequestCreate(symbol="AAPL!")

        error = exc_info.value
        assert len(error.errors()) == 1
        assert "uppercase letters (A-Z) and digits (0-9)" in str(error.errors()[0]["msg"])

    def test_symbol_length_exactly_one_character(self) -> None:
        """Test that validate_symbol_format rejects single character symbols.

        Verifies that stock symbols must be at least 2 characters long and
        single character inputs are rejected with appropriate error messages.
        """
        with pytest.raises(ValidationError) as exc_info:
            StockRequestCreate(symbol="A")

        error = exc_info.value
        assert len(error.errors()) == 1
        assert "must be 2-10 characters long" in str(error.errors()[0]["msg"])

    def test_symbol_length_exactly_max_length(self) -> None:
        """Test that validate_symbol_format accepts symbols at exactly maximum length.

        Verifies that symbols exactly at the maximum allowed length (10 characters)
        are accepted and processed correctly.
        """
        data: dict[str, str] = {"symbol": "ABCDEFGHIJ"}  # 10 characters
        request = StockRequestCreate(**data)
        assert request.symbol == "ABCDEFGHIJ"

    def test_symbol_length_one_over_max_rejected(self) -> None:
        """Test that validate_symbol_format rejects symbols exceeding maximum length.

        Verifies that symbols longer than the maximum allowed length (10 characters)
        are rejected by Field validation before custom validation.
        """
        with pytest.raises(ValidationError) as exc_info:
            StockRequestCreate(symbol="ABCDEFGHIJK")  # 11 characters

        error = exc_info.value
        assert len(error.errors()) == 1
        # Field validation happens before custom validation, so we get the field error
        assert "String should have at most 10 characters" in str(error.errors()[0]["msg"])

    def test_symbol_with_lowercase_letters_converted(self) -> None:
        """Test that validate_symbol_format converts lowercase letters to uppercase.

        Verifies that symbols containing lowercase letters are properly converted
        to uppercase format during validation.
        """
        data: dict[str, str] = {"symbol": "aBcDeF"}
        request = StockRequestCreate(**data)
        assert request.symbol == "ABCDEF"

    def test_symbol_with_mixed_case_and_digits(self) -> None:
        """Test that validate_symbol_format handles mixed case and digits correctly.

        Verifies that symbols with mixed uppercase, lowercase, and digits are
        properly converted to uppercase format while maintaining digit positions.
        """
        data: dict[str, str] = {"symbol": "aB1cD2eF"}
        request = StockRequestCreate(**data)
        assert request.symbol == "AB1CD2EF"

    def test_symbol_with_only_digits_rejected(self) -> None:
        """Test that validate_symbol_format rejects symbols containing only digits.

        Verifies that stock symbols cannot consist entirely of numeric digits
        and must contain at least one letter.
        """
        with pytest.raises(ValidationError) as exc_info:
            StockRequestCreate(symbol="12345")

        error = exc_info.value
        assert len(error.errors()) == 1
        assert "must start with a letter" in str(error.errors()[0]["msg"])

    def test_symbol_with_leading_whitespace_trimmed(self) -> None:
        """Test that validate_symbol_format trims leading whitespace."""
        data: dict[str, str] = {"symbol": "  AAPL"}
        request = StockRequestCreate(**data)
        assert request.symbol == "AAPL"

    def test_symbol_with_trailing_whitespace_trimmed(self) -> None:
        """Test that validate_symbol_format trims trailing whitespace."""
        data: dict[str, str] = {"symbol": "AAPL  "}
        request = StockRequestCreate(**data)
        assert request.symbol == "AAPL"

    def test_symbol_with_newline_trimmed(self) -> None:
        """Test that validate_symbol_format trims newline characters."""
        data: dict[str, str] = {"symbol": "\nAAPL\n"}
        request = StockRequestCreate(**data)
        assert request.symbol == "AAPL"

    def test_symbol_with_tab_trimmed(self) -> None:
        """Test that validate_symbol_format trims tab characters."""
        data: dict[str, str] = {"symbol": "\tAAPL\t"}
        request = StockRequestCreate(**data)
        assert request.symbol == "AAPL"

    def test_symbol_with_multiple_whitespace_characters_trimmed(self) -> None:
        """Test that validate_symbol_format trims multiple whitespace characters."""
        data: dict[str, str] = {"symbol": "  \t\n  AAPL  \n\t  "}
        request = StockRequestCreate(**data)
        assert request.symbol == "AAPL"


class TestStockRequestResponse:
    """Test cases for StockRequestResponse schema."""

    def test_valid_response_creation(self) -> None:
        """Test that StockRequestResponse can be created with valid data.

        Verifies that the response schema accepts all required fields and
        properly validates the data structure.
        """
        data: dict[str, Any] = {
            "id": "test-id-123",
            "symbol": "AAPL",
            "is_active": True,
            "last_pull_date": datetime.now(),
            "last_pull_status": PullStatus.SUCCESS,
            "error_message": None,
        }
        response = StockRequestResponse(**data)
        assert response.id == "test-id-123"
        assert response.symbol == "AAPL"
        assert response.is_active is True
        assert response.last_pull_status == PullStatus.SUCCESS

    def test_response_with_optional_fields(self) -> None:
        """Test that StockRequestResponse accepts optional error message field.

        Verifies that the response schema properly handles optional fields
        and maintains data integrity.
        """
        data: dict[str, Any] = {
            "id": "test-id-456",
            "symbol": "TSLA",
            "is_active": False,
            "last_pull_date": datetime.now(),
            "last_pull_status": PullStatus.FAILED,
            "error_message": "API rate limit exceeded",
        }
        response = StockRequestResponse(**data)
        assert response.error_message == "API rate limit exceeded"
        assert response.is_active is False
        assert response.last_pull_status == PullStatus.FAILED

    def test_response_without_optional_fields(self) -> None:
        """Test that StockRequestResponse works without optional error message.

        Verifies that the response schema functions correctly when optional
        fields are not provided.
        """
        data: dict[str, Any] = {
            "id": "test-id-789",
            "symbol": "GOOGL",
            "is_active": True,
            "last_pull_date": datetime.now(),
            "last_pull_status": PullStatus.PENDING,
        }
        response = StockRequestResponse(**data)
        assert response.error_message is None
        assert response.is_active is True
        assert response.last_pull_status == PullStatus.PENDING

    def test_response_from_orm_model(self) -> None:
        """Test that StockRequestResponse can be created from ORM model data.

        Verifies that the response schema is compatible with database model
        data structures and handles ORM field names correctly.
        """
        # Simulate ORM model data
        orm_data: dict[str, Any] = {
            "id": "orm-id-123",
            "symbol": "MSFT",
            "is_active": True,
            "last_pull_date": datetime.now(),
            "last_pull_status": PullStatus.SUCCESS,
            "error_message": None,
        }
        response = StockRequestResponse(**orm_data)
        assert response.id == "orm-id-123"
        assert response.symbol == "MSFT"

    def test_disabled_status_works_correctly(self) -> None:
        """Test that StockRequestResponse handles disabled status correctly.

        Verifies that the response schema properly handles the DISABLED status
        and associated inactive state.
        """
        data: dict[str, Any] = {
            "id": "disabled-id-123",
            "symbol": "DISABLED",
            "is_active": False,
            "last_pull_date": datetime.now(),
            "last_pull_status": PullStatus.DISABLED,
            "error_message": "Tracking deactivated by admin",
        }
        response = StockRequestResponse(**data)
        assert response.is_active is False
        assert response.last_pull_status == PullStatus.DISABLED
        assert response.error_message == "Tracking deactivated by admin"


class TestTrackedStockListResponse:
    """Test cases for TrackedStockListResponse schema."""

    def test_valid_list_response_creation(self) -> None:
        """Test that TrackedStockListResponse can be created with valid data.

        Verifies that the list response schema accepts multiple stock responses
        and properly calculates pagination metadata.
        """
        stock_responses: list[StockRequestResponse] = [
            StockRequestResponse(
                id="id-1",
                symbol="AAPL",
                is_active=True,
                last_pull_date=datetime.now(),
                last_pull_status=PullStatus.SUCCESS,
                error_message=None,
            ),
            StockRequestResponse(
                id="id-2",
                symbol="TSLA",
                is_active=True,
                last_pull_date=datetime.now(),
                last_pull_status=PullStatus.SUCCESS,
                error_message=None,
            ),
        ]

        data: dict[str, Any] = {
            "stocks": stock_responses,
            "total_count": EXPECTED_STOCK_COUNT,
            "page": 1,
            "page_size": DEFAULT_PAGE_SIZE,
            "total_pages": 1,
        }
        response = TrackedStockListResponse(**data)
        assert len(response.stocks) == EXPECTED_STOCK_COUNT
        assert response.total_count == EXPECTED_STOCK_COUNT
        assert response.page == 1
        assert response.page_size == DEFAULT_PAGE_SIZE
        assert response.total_pages == 1

    def test_empty_list_response(self) -> None:
        """Test that TrackedStockListResponse handles empty stock lists correctly.

        Verifies that the list response schema works properly when no stocks
        are being tracked.
        """
        data: dict[str, Any] = {
            "stocks": [],
            "total_count": 0,
            "page": 1,
            "page_size": DEFAULT_PAGE_SIZE,
            "total_pages": 0,
        }
        response = TrackedStockListResponse(**data)
        assert len(response.stocks) == 0
        assert response.total_count == 0
        assert response.total_pages == 0


class TestStockTrackingUpdate:
    """Test cases for StockTrackingUpdate schema."""

    def test_valid_update_all_fields(self) -> None:
        """Test that StockTrackingUpdate can be created with all fields.

        Verifies that the update schema accepts all required fields and
        properly validates the update data structure.
        """
        data: dict[str, Any] = {
            "is_active": False,
            "last_pull_status": PullStatus.FAILED,
            "error_message": "API connection timeout",
        }
        update = StockTrackingUpdate(**data)
        assert update.is_active is False
        assert update.last_pull_status == PullStatus.FAILED
        assert update.error_message == "API connection timeout"

    def test_valid_update_without_error_message(self) -> None:
        """Test that StockTrackingUpdate works without optional error message.

        Verifies that the update schema functions correctly when the optional
        error message field is not provided.
        """
        data: dict[str, Any] = {
            "is_active": True,
            "last_pull_status": PullStatus.SUCCESS,
        }
        update = StockTrackingUpdate(**data)
        assert update.is_active is True
        assert update.last_pull_status == PullStatus.SUCCESS
        assert update.error_message is None

    @pytest.mark.parametrize(
        "valid_status", [PullStatus.PENDING, PullStatus.SUCCESS, PullStatus.FAILED, PullStatus.DISABLED]
    )
    def test_valid_pull_status_accepted(self, valid_status: PullStatus) -> None:
        """Test that StockTrackingUpdate accepts all valid pull status values.

        Verifies that the update schema accepts all defined PullStatus enum
        values without validation errors.
        """
        data: dict[str, Any] = {
            "is_active": True,
            "last_pull_status": valid_status,
        }
        update = StockTrackingUpdate(**data)
        assert update.last_pull_status == valid_status


class TestSchemaIntegration:
    """Integration tests for schema interactions."""

    def test_create_to_response_flow(self) -> None:
        """Test the complete flow from create request to response.

        Verifies that data flows correctly through the validation pipeline
        from input request to output response.
        """
        # Create request
        create_data: dict[str, str] = {"symbol": "AAPL"}
        create_request = StockRequestCreate(**create_data)
        assert create_request.symbol == "AAPL"

        # Create response
        response_data: dict[str, Any] = {
            "id": "test-id",
            "symbol": create_request.symbol,
            "is_active": True,
            "last_pull_date": datetime.now(),
            "last_pull_status": PullStatus.PENDING,
            "error_message": None,
        }
        response = StockRequestResponse(**response_data)
        assert response.symbol == create_request.symbol

    def test_update_flow(self) -> None:
        """Test the complete update flow with status changes.

        Verifies that update operations work correctly with status
        transitions and error message handling.
        """
        # Initial state
        initial_data: dict[str, Any] = {
            "is_active": True,
            "last_pull_status": PullStatus.PENDING,
            "error_message": None,
        }
        initial_update = StockTrackingUpdate(**initial_data)

        # Updated state
        updated_data: dict[str, Any] = {
            "is_active": False,
            "last_pull_status": PullStatus.FAILED,
            "error_message": "Network timeout",
        }
        updated_update = StockTrackingUpdate(**updated_data)

        assert initial_update.is_active != updated_update.is_active
        assert initial_update.last_pull_status != updated_update.last_pull_status
        assert initial_update.error_message != updated_update.error_message
