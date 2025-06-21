# STOCK-003: Add API Endpoints for Stock Tracking

## Type
Task

## Priority
High

## Assignee
FastAPI Engineer

## Story Points
3

## Description
Add new API endpoints for requesting stock tracking and managing tracked stocks.


## Before Resuming Work:
- [x] Are there unused imports?
- [x] Are the legal notices correct?
- [x] Can we move anything into a module level constants file?
- [x] Are there constants in the tests that should be moved?

## Acceptance Criteria
- [x] Add `POST /stock-data/track` endpoint for requesting stock tracking
- [x] Add `GET /stock-data/track` endpoint for listing tracked stocks (admin)
- [x] Add `DELETE /stock-data/tracked/{symbol}` endpoint for deactivating tracking (admin)
- [x] Implement proper authentication and authorization
- [x] Add request/response validation using Pydantic schemas
- [x] Include proper error handling and status codes
- [x] Add API documentation with examples

## Technical Details
**File:** `cream_api/stock_data/api.py`

**Endpoints:**
- `POST /stock-data/track` - Request stock tracking ✅
- `GET /stock-data/track` - List all tracked stocks (admin only) ✅ (rejects all users until admin roles implemented)
- `DELETE /stock-data/tracked/{symbol}` - Deactivate tracking (admin only) ✅ (rejects all users until admin roles implemented)

**Requirements:**
- Use existing FastAPI patterns
- Implement proper authentication
- Add comprehensive error handling
- Include API documentation
- Follow existing endpoint structure

## Dependencies
- STOCK-001 (Pydantic schemas)
- STOCK-002 (Business logic)

## Definition of Done
- [x] All endpoints are implemented and working
- [x] Authentication is properly configured
- [x] Error handling is comprehensive
- [x] API documentation is complete
- [x] Integration tests are written and passing
- [x] Endpoints follow existing patterns

## Notes
Ensure proper separation of concerns between API layer and business logic layer.
