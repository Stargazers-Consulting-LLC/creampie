# STOCK-005: Create Frontend API Client for Stock Tracking

## Type
Task

## Priority
High

## Assignee
React Engineer

## Story Points
3

## Description
Create TypeScript API client functions for interacting with the stock tracking backend endpoints.

## Acceptance Criteria
- [ ] Create `trackStock()` function for requesting stock tracking
- [ ] Create `getTrackedStocks()` function for fetching tracked stocks
- [ ] Create `deactivateStockTracking()` function for admin operations
- [ ] Implement proper TypeScript interfaces
- [ ] Add error handling and type safety
- [ ] Follow existing API client patterns
- [ ] Include proper request/response typing

## Technical Details
**File:** `cream_ui/src/lib/api/stockTracking.ts`

**Functions:**
- `trackStock(symbol: string): Promise<TrackedStock>`
- `getTrackedStocks(): Promise<TrackedStock[]>`
- `deactivateStockTracking(symbol: string): Promise<void>`

**Requirements:**
- Use existing axios patterns
- Implement proper error handling
- Add TypeScript interfaces
- Follow existing API client structure
- Include proper request headers

## Dependencies
- STOCK-003 (Backend API endpoints)

## Definition of Done
- [ ] All API client functions are implemented
- [ ] TypeScript interfaces are defined
- [ ] Error handling is comprehensive
- [ ] Code follows existing patterns
- [ ] Unit tests are written and passing

## Notes
Ensure proper error handling and user feedback for API failures.
