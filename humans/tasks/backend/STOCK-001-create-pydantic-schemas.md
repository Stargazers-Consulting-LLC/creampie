# STOCK-001: Create Pydantic Schemas for Stock Tracking Requests

## Type
Task

## Priority
High

## Assignee
FastAPI Engineer

## Story Points
2

## Description
Create Pydantic schemas for handling stock tracking request validation and responses.

## Acceptance Criteria
- [x] Create `StockRequestCreate` schema with symbol validation
- [x] Create `StockRequestResponse` schema for API responses
- [x] Create `TrackedStockListResponse` schema for admin listing
- [x] Implement proper validation rules for stock symbols
- [x] Add comprehensive field validation and error messages
- [x] Follow existing Pydantic patterns in the codebase

## Technical Details
**File:** `cream_api/stock_data/schemas.py`

**Requirements:**
- Symbol validation: uppercase letters and digits 0-9 only, 1-10 characters
- Proper field types and constraints
- Config for ORM mode compatibility
- Clear error messages for validation failures

## Dependencies
- None

## Definition of Done
- [x] Schemas are created and tested
- [x] Validation rules are working correctly
- [x] Error messages are user-friendly
- [x] Code follows existing patterns
- [x] Unit tests are written and passing

## Notes
Reference existing schema patterns in the codebase for consistency.

## Implementation Notes
- **Completed:** All schemas created with modern Pydantic v2 patterns
- **Validation:** Comprehensive symbol validation with whitespace rejection
- **Testing:** 100 tests passing with full coverage
- **Modern Patterns:** Used ConfigDict and @model_serializer instead of deprecated patterns
- **Enum:** Added PullStatus enum for type-safe status values (PENDING, SUCCESS, FAILED, DISABLED)
- **Warnings:** Eliminated all 80 deprecation warnings by updating to Pydantic v2 best practices

## Files Created/Modified
- `cream_api/stock_data/schemas.py` - Main schema definitions
- `cream_api/tests/stock_data/test_schemas.py` - Comprehensive test suite
- `pytest.ini` - Updated to treat warnings as errors
