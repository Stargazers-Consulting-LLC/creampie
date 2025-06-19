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
- [ ] Create `StockRequestResponse` schema for API responses
- [ ] Create `TrackedStockListResponse` schema for admin listing
- [ ] Implement proper validation rules for stock symbols
- [ ] Add comprehensive field validation and error messages
- [ ] Follow existing Pydantic patterns in the codebase

## Technical Details
**File:** `cream_api/stock_data/schemas.py`

**Requirements:**
- Symbol validation: uppercase letters and digits 0-9 only, 1-9 characters
- Proper field types and constraints
- Config for ORM mode compatibility
- Clear error messages for validation failures

## Dependencies
- None

## Definition of Done
- [ ] Schemas are created and tested
- [ ] Validation rules are working correctly
- [ ] Error messages are user-friendly
- [ ] Code follows existing patterns
- [ ] Unit tests are written and passing

## Notes
Reference existing schema patterns in the codebase for consistency.
