# Stock Tracking Request UI Feature Plan

## Overview
This feature will allow authenticated users to request that the system track specific stocks on their behalf. All backend logic will be contained within the `cream_api/stock_data` module, following the established project patterns.

## Architecture Analysis

Based on the current project structure:
- **Backend**: All stock-related logic in `cream_api/stock_data/`
- **Models**: Stock models in `cream_api/stock_data/models.py`
- **API**: Endpoints defined in main router, business logic in `cream_api/stock_data/`
- **Frontend**: React/TypeScript with shadcn/ui components

## Feature Plan

### 1. Database Schema Changes

#### Update `cream_api/stock_data/models.py`
No new models needed - use existing `TrackedStock` model:

- **TrackedStock Model**: Already exists and tracks stocks globally
  - Fields: id, symbol, last_pull_date, last_pull_status, error_message, is_active
  - Unique constraint on symbol (prevents duplicate tracking)
  - **Purpose**: Track which stocks are being monitored by the system

**Note**: The existing `TrackedStock` model is sufficient for our use case. When a user requests a stock:
1. If the stock is already being tracked (exists in TrackedStock), the request is approved immediately
2. If the stock is not being tracked, create a new TrackedStock entry and approve the request
3. All users benefit from stocks being tracked, regardless of who requested them

### 2. Backend Implementation

#### A. No changes needed to `cream_api/stock_data/models.py`
- Use existing `TrackedStock` model
- No new models required

#### B. Create `cream_api/stock_data/schemas.py`
- **StockRequestCreate**: Pydantic model for creating requests
- **StockRequestResponse**: Pydantic model for API responses (based on TrackedStock)
- Include validation for symbol format and length

#### C. No additional manager needed
- Use existing `cream_api/stock_data/` module components
- API endpoints can directly interact with `TrackedStock` model
- Existing background tasks handle data fetching and processing
- Leverage existing retriever, parser, processor, and loader logic

#### D. No additional exceptions needed
- Use existing pattern of standard HTTPException
- Pydantic validation handles input validation
- Database constraints handle duplicate prevention
- Follow existing error handling in `cream_api/stock_data/api.py`

#### E. No additional tasks needed
- Existing `tasks.py` already has all necessary functionality
- `retrieve_historical_data_task()` handles individual stock data retrieval
- `update_all_tracked_stocks()` processes all tracked stocks
- `run_periodic_updates()` automatically picks up new TrackedStock entries
- Background processing is already handled by existing task system

### 3. API Integration

#### 3A. No changes needed to `cream_api/main.py`
- Stock data router is already imported and included
- Existing `/stock-data/track` endpoint handles stock tracking requests
- Additional endpoints can be added to existing `cream_api/stock_data/api.py`

#### 3B. Update `cream_api/stock_data/api.py` (if needed)
- Existing `/track` endpoint already handles stock tracking
- **User endpoints needed**: List all tracked stocks available to the service
- **Admin-only endpoints**: Get detailed tracking status and deactivate tracking (for admin users only)

### 4. Frontend Implementation

#### A. Create `cream_ui/src/lib/api/stockRequests.ts`
- **API client functions for stock tracking operations**:
  - `trackStock(symbol: string)` - Request to track a new stock (POST to `/stock-data/track`)
  - `getTrackedStocks()` - List all tracked stocks available (GET from new endpoint)
  - `getStockStatus(symbol: string)` - Get detailed status (admin-only, GET from new endpoint)
  - `deactivateTracking(symbol: string)` - Disable tracking by setting `is_active=false` (admin-only, PATCH to new endpoint)
- **TypeScript interfaces** for request/response types (based on TrackedStock model)
- **Error handling** and type safety

#### B. Create `cream_ui/src/pages/stock-requests/StockRequestPage.tsx`
- Simple form page for requesting to track new stocks
- Single form with stock symbol input and submit button
- Success/error message display
- Loading state during submission

#### C. Create `cream_ui/src/components/stock-requests/`
- **StockRequestForm.tsx**: Simple form for requesting to track new stocks
- **StockSymbolInput.tsx**: Validated stock symbol input component
- **MessageDisplay.tsx**: Component for showing success/error messages

### 5. User Experience Flow

#### A. Stock Tracking Request Flow
1. User navigates to "Track Stocks" section
2. User sees a simple form with stock symbol input
3. User enters stock symbol (with validation)
4. User clicks "Track Stock" button
5. Form shows loading state during submission
6. If successful, shows confirmation message
7. If stock already tracked, shows "already being tracked" message
8. If error, shows error message with details

#### B. Admin Management Flow (Separate Interface)
1. Admin accesses admin dashboard
2. Admin sees list of all tracked stocks with status
3. Admin can view detailed tracking information (last pull, errors, etc.)
4. Admin can deactivate tracking for specific stocks
5. Admin can re-enable previously deactivated stocks

### 6. Integration Points

#### A. Existing Stock Data Pipeline
- Existing `/stock-data/track` endpoint already handles TrackedStock creation
- Existing background tasks automatically process new TrackedStock entries
- No additional integration needed - system is already complete

#### B. User Authentication
- Leverage existing auth system and protected routes
- Use current session management

#### C. Background Tasks
- Existing background task system already handles all processing
- No additional tasks needed - `run_periodic_updates()` picks up new stocks automatically

### 7. Implementation Phases

#### Phase 1: Backend Schemas (Week 1)
1. Add schemas to `cream_api/stock_data/schemas.py`
2. Add listing endpoints to `cream_api/stock_data/api.py` (if needed)
3. Write unit tests for new functionality

#### Phase 2: Frontend Implementation (Week 2)
1. Create API client functions
2. Build simple form components
3. Add form validation and error handling
4. Implement responsive design

#### Phase 3: Integration & Testing (Week 3)
1. End-to-end testing
2. Performance optimization
3. Documentation updates

### 8. Technical Considerations

#### A. Security
- Sanitize stock symbol input
- Rate limiting for request creation
- Admin-only access for management endpoints

#### B. Performance
- Simple form submission - no complex data loading
- Optimistic updates for better UX
- Background processing already handled by existing tasks

#### C. Error Handling
- Graceful handling of invalid stock symbols
- Clear error messages for users
- Retry logic for failed operations
- Fallback states for network issues

### 9. Testing Strategy

#### A. Backend Tests
- Unit tests for new schemas
- Integration tests for new API endpoints (if any)
- Test existing `/track` endpoint integration

#### B. Frontend Tests
- Component unit tests for form components
- Form validation tests
- API integration tests
- End-to-end form submission flow tests

### 10. Documentation Updates

#### A. API Documentation
- Update OpenAPI/Swagger docs
- Add request/response examples
- Document error codes and messages

#### B. User Documentation
- Update user guides
- Add feature documentation
- Create troubleshooting guide

## Success Criteria

1. Users can successfully request stock tracking via simple form
2. Form provides clear feedback (success/error/loading states)
3. Requests integrate with existing stock data pipeline
4. UI is responsive and user-friendly
5. All error cases are handled gracefully
6. Performance meets acceptable standards
7. Code follows established project patterns
8. Comprehensive test coverage
9. Documentation is complete and accurate

This plan follows the established project patterns by keeping all stock-related backend logic within the `cream_api/stock_data` module, while maintaining clean separation of concerns and following the existing code organization.
