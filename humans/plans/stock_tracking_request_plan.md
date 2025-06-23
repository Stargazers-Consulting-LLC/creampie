# Stock Tracking Request Plan

> This document outlines the plan for implementing stock tracking request functionality. Use this for understanding the planned implementation and requirements.

## Table of Contents
1. [Overview](#overview)
2. [Description](#description)
3. [Business Value](#business-value)
4. [User Stories](#user-stories)
5. [Architecture Analysis](#architecture-analysis)
6. [Technical Requirements](#technical-requirements)
7. [Implementation Plan](#implementation-plan)
8. [Testing Strategy](#testing-strategy)
9. [Documentation Updates](#documentation-updates)
10. [Success Criteria](#success-criteria)
11. [Risks and Mitigation](#risks-and-mitigation)

---

## Overview

**Feature Name:** Stock Tracking Request UI
**Status:** In Progress
**Priority:** Medium

This feature will allow authenticated users to request that the system track specific stocks on their behalf. All backend logic will be contained within the `cream_api/stock_data` module, following the established project patterns.

## Description

This feature will allow authenticated users to request that the system track specific stocks on their behalf. All backend logic will be contained within the `cream_api/stock_data` module, following the established project patterns.

The feature provides users with control over which stocks are monitored, increasing engagement and expanding data coverage based on user demand.

## Business Value

- **User Engagement**: Increases user interaction with the platform by allowing them to request stock tracking
- **Data Coverage**: Expands the range of stocks being tracked based on user demand
- **User Satisfaction**: Provides users with control over which stocks are monitored
- **Platform Growth**: Encourages users to return to check on their requested stocks

Each benefit should be measurable or observable.

## User Stories

- As a **registered user**, I want to **request that a specific stock be tracked** so that **I can monitor stocks I'm interested in**
- As a **registered user**, I want to **see confirmation when my request is processed** so that **I know the system is working on my request**
- As an **admin user**, I want to **view all tracked stocks and their status** so that **I can manage the tracking system**
- As an **admin user**, I want to **deactivate tracking for specific stocks** so that **I can control system resources**

Each story should be testable and have clear acceptance criteria.

## Architecture Analysis

Based on the current project structure:

- **Backend**: All stock-related logic in `cream_api/stock_data/` module
- **Models**: Stock models in `cream_api/stock_data/models.py` (TrackedStock model)
- **API**: Endpoints defined in `cream_api/stock_data/api.py`, router in `cream_api/main.py`
- **Frontend**: React/TypeScript with shadcn/ui components in `cream_ui/src/`

All listed files and modules must exist in the codebase.

## Technical Requirements

### Functional Requirements

- **Stock Request Creation**: Users can submit stock symbol requests with validation
- **Duplicate Prevention**: System prevents tracking the same stock multiple times
- **Request Confirmation**: Users receive immediate feedback on request status
- **Admin Management**: Admins can view and manage all tracked stocks
- **Integration with Existing Pipeline**: New requests integrate with existing stock data processing

Each requirement must have clear acceptance criteria.

### Non-Functional Requirements

- **Performance**: API response time < 200ms for stock request submission
- **Security**: Rate limiting of 10 requests/minute per user, input sanitization for stock symbols
- **Scalability**: Support 100 concurrent stock request submissions
- **Compatibility**: Works with existing authentication system and protected routes

All requirements must be measurable or verifiable.

## Implementation Plan

### 1. Database Schema Changes

#### Update `cream_api/stock_data/models.py`

No new models needed - use existing `TrackedStock` model:

- **TrackedStock Model**: Already exists and tracks stocks globally
  - Fields: `id: int, symbol: str, last_pull_date: datetime, last_pull_status: str, error_message: str, is_active: bool`
  - Unique constraint on symbol (prevents duplicate tracking)
  - **Purpose**: Track which stocks are being monitored by the system
  - **Relationships**: No new relationships needed

The existing `TrackedStock` model is sufficient for our use case. When a user requests a stock:
1. If the stock is already being tracked (exists in TrackedStock), the request is approved immediately
2. If the stock is not being tracked, create a new TrackedStock entry and approve the request
3. All users benefit from stocks being tracked, regardless of who requested them

### 2. Backend Implementation

#### A. Models
- No changes needed to existing `TrackedStock` model
- Use existing model with fields: `id`, `symbol`, `last_pull_date`, `last_pull_status`, `error_message`, `is_active`

#### B. Schemas
- **StockRequestCreate**: `symbol: str = Field(..., min_length=1, max_length=10, regex=r'^[A-Z]+$')`
- **StockRequestResponse**: Based on TrackedStock model with fields: `id`, `symbol`, `is_active`, `last_pull_date`
- Include validation for symbol format (uppercase letters only) and length (1-10 characters)

#### C. Business Logic
- `def process_stock_request(symbol: str, user_id: int) -> TrackedStock:` - Process user stock request
- `def get_tracked_stocks() -> List[TrackedStock]:` - Get all tracked stocks (admin only)
- `def deactivate_stock_tracking(symbol: str) -> TrackedStock:` - Deactivate tracking (admin only)

#### D. Error Handling
- `StockAlreadyTrackedError` - When stock is already being tracked
- `InvalidStockSymbolError` - When symbol format is invalid
- `StockNotFoundError` - When stock doesn't exist in external API

#### E. Background Tasks
- No additional tasks needed - use existing `update_all_tracked_stocks()` from `cream_api/stock_data/tasks.py`
- Existing `run_periodic_updates()` automatically picks up new TrackedStock entries

### 3. API Integration

#### A. Router Integration
- No changes needed to `cream_api/main.py` - stock data router already imported
- Add new endpoints to existing `cream_api/stock_data/api.py`
- Reference existing endpoint patterns like `/stock-data/track`

#### B. Endpoint Implementation
- `POST /stock-data/request` - Submit stock tracking request (requires auth)
- `GET /stock-data/tracked` - List all tracked stocks (admin only)
- `PATCH /stock-data/tracked/{symbol}/deactivate` - Deactivate tracking (admin only)
- Include specific request/response formats with field names
- List specific auth requirements: `@requires_auth` for user endpoints, `@requires_admin` for admin endpoints

### 4. Frontend Implementation

#### A. API Client Functions
- `trackStock(symbol: string): Promise<TrackedStock>` - Request to track new stock
- `getTrackedStocks(): Promise<TrackedStock[]>` - Get all tracked stocks (admin only)
- `deactivateTracking(symbol: string): Promise<TrackedStock>` - Deactivate tracking (admin only)
- Include specific TypeScript interfaces with field names

#### B. Pages
- **StockRequestPage**: `cream_ui/src/pages/stock-requests/StockRequestPage.tsx`
- Describe specific form fields: stock symbol input with validation, submit button, loading state, success/error messages

#### C. Components
- **StockRequestForm**: `cream_ui/src/components/stock-requests/StockRequestForm.tsx` with props: `onSubmit: (symbol: string) => void`
- **StockSymbolInput**: `cream_ui/src/components/stock-requests/StockSymbolInput.tsx` with validation
- **MessageDisplay**: `cream_ui/src/components/stock-requests/MessageDisplay.tsx` for success/error messages

### 5. User Experience Flow

#### A. Primary User Flow
1. User navigates to `/stock-requests` page
2. User sees form with stock symbol input field
3. User enters stock symbol (validation: 1-10 uppercase letters)
4. User clicks "Track Stock" button
5. Form shows loading state during submission
6. If successful, shows confirmation message with stock symbol
7. If stock already tracked, shows "already being tracked" message
8. If error, shows error message with details

#### B. Alternative Flows (if applicable)
1. Invalid symbol shows error message with validation rules
2. Admin sees additional management options in admin dashboard
3. Network error shows retry option with fallback message

### 6. Integration Points

#### A. Existing Systems
- Integrates with `cream_api/stock_data/` module using existing `TrackedStock` model
- References existing functions: `update_all_tracked_stocks()` for background processing
- Uses existing authentication system from `cream_api/users/`

#### B. External Dependencies
- No new external dependencies required
- Uses existing stock data retrieval system
- Leverages existing authentication and authorization

#### C. Background Processing
- Uses existing `run_periodic_updates()` task from `cream_api/stock_data/tasks.py`
- No additional task scheduling needed
- References existing task patterns

## Technical Considerations

### A. Security
- Input sanitization for stock symbols (uppercase letters only)
- Rate limiting: 10 requests/minute per user
- Admin-only access for management endpoints
- Reference existing security patterns from `cream_api/common/`

### B. Performance
- Simple form submission with minimal data processing
- Database indexing on symbol field for fast lookups
- Optimistic updates for better UX
- Reference existing performance patterns

### C. Error Handling
- Graceful handling of invalid stock symbols with clear error messages
- Network timeout retry logic for API calls
- Fallback states for network issues
- Reference existing error handling patterns

## Implementation Phases

### Phase 1: Backend Schemas
1. Create `cream_api/stock_data/schemas.py` with StockRequestCreate and StockRequestResponse models
2. Add validation for stock symbol format (uppercase letters, 1-10 characters)
3. Write unit tests for new schemas in `tests/stock_data/test_schemas.py`

### Phase 2: Frontend Implementation
1. Create `cream_ui/src/lib/api/stockRequests.ts` with API client functions
2. Build StockRequestForm component with validation in `cream_ui/src/components/stock-requests/`
3. Add error handling and loading states to all components
4. Implement responsive design with shadcn/ui components

### Phase 3: Integration & Testing
1. End-to-end testing of complete user flow with realistic scenarios
2. Performance testing with 100 concurrent requests
3. Update API documentation with new endpoints in OpenAPI/Swagger

## Testing Strategy

### A. Backend Tests
- Unit tests in `tests/stock_data/test_schemas.py` for validation logic
- Integration tests in `tests/stock_data/test_api.py` for endpoint functionality
- Test existing `/stock-data/track` endpoint integration
- Reference existing test patterns from `tests/stock_data/`

### B. Frontend Tests
- Component tests in `cream_ui/src/components/__tests__/StockRequestForm.test.tsx`
- Test scenarios: "validates symbol format", "handles API errors", "shows loading states"
- API integration tests for all client functions
- End-to-end tests for complete user flow

### C. Performance Tests
- API response time testing under load (100 concurrent requests)
- Database query performance testing for symbol lookups
- Frontend component rendering performance tests

## Documentation Updates

### A. API Documentation
- Add `/stock-data/request` endpoint to OpenAPI/Swagger documentation
- Add `/stock-data/tracked` endpoint for admin access
- Include request/response examples for each endpoint
- Document error codes and messages for all scenarios

### B. User Documentation
- Update user guide with stock tracking feature instructions
- Add troubleshooting guide for common errors (invalid symbols, network issues)
- Create admin documentation for stock management features

## Success Criteria

1. Users can successfully request stock tracking with 95% success rate
2. Form provides feedback within 2 seconds for all interactions
3. API endpoints respond within 200ms for stock request submissions
4. 90% test coverage for all new code components
5. All new endpoints documented in OpenAPI with examples
6. Error handling covers 100% of failure scenarios
7. Admin interface provides full stock management capabilities
8. Integration with existing stock data pipeline works seamlessly

All criteria must be measurable and testable.

## Risks and Mitigation

| Risk | Impact | Probability | Mitigation Strategy |
|------|--------|-------------|-------------------|
| Invalid stock symbols cause API errors | API returns 500 errors | Medium | Add comprehensive input validation and error handling |
| Duplicate requests overwhelm system | Performance degradation | Low | Implement rate limiting and duplicate prevention |
| Admin interface security issues | Unauthorized access | Medium | Implement proper admin authentication and authorization |
| Integration with existing pipeline fails | Stock data not updated | Low | Thorough testing of integration points and fallback mechanisms |

## Review Checklist

- [x] Business requirements reviewed and approved
- [x] Technical design reviewed against existing patterns
- [x] Security review completed with specific measures identified
- [x] Performance requirements validated with specific metrics
- [x] UI/UX design approved with specific user flows
- [ ] Documentation completed for all new components
- [ ] Test cases reviewed with specific coverage requirements
- [ ] Deployment plan approved with specific steps
- [x] Integration points validated against existing systems
- [x] User experience flows tested with specific scenarios

## Notes

This feature leverages the existing stock data infrastructure, requiring minimal new code while providing significant user value. The implementation focuses on reusing existing patterns and components to ensure consistency and maintainability.

## References

- Existing `TrackedStock` model in `cream_api/stock_data/models.py`
- Existing stock data API patterns in `cream_api/stock_data/api.py`
- Project architecture and component relationships
- Project-specific patterns and conventions
- Detailed stock data module analysis
- Decision-making frameworks

---

**Last Updated:** 2025-06-18
**Version:** 2.1
**Status:** In Progress
