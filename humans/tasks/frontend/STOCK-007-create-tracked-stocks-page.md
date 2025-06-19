# STOCK-007: Create Tracked Stocks Management Page

## Type
Task

## Priority
Medium

## Assignee
React Engineer

## Story Points
4

## Description
Create a React page for admin users to view and manage all tracked stocks.

## Acceptance Criteria
- [ ] Create `TrackedStocksPage` component
- [ ] Display list of all tracked stocks
- [ ] Show stock status and last update information
- [ ] Add ability to deactivate stock tracking
- [ ] Implement proper loading states
- [ ] Add error handling for failed operations
- [ ] Include admin-only access control

## Technical Details
**File:** `cream_ui/src/pages/admin/TrackedStocksPage.tsx`

**Page Features:**
- Table/list view of tracked stocks
- Stock symbol, status, and last update info
- Deactivate button for each stock
- Loading and error states
- Admin access control

**Requirements:**
- Use shadcn/ui table components
- Implement proper data fetching
- Add confirmation dialogs for actions
- Include proper error handling
- Add responsive design

## Dependencies
- STOCK-005 (API client functions)
- STOCK-006 (Stock request form)

## Definition of Done
- [ ] Page displays tracked stocks correctly
- [ ] Admin actions are working properly
- [ ] Loading and error states are handled
- [ ] Access control is implemented
- [ ] Unit tests are written and passing
- [ ] Page follows existing patterns

## Notes
Ensure proper admin access control and confirmation for destructive actions.
