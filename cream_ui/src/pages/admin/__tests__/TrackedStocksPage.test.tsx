/**
 * TrackedStocksPage Component Tests
 *
 * Comprehensive unit tests for the TrackedStocksPage component covering
 * data loading, display, error handling, and admin actions.
 *
 * SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>
 * SPDX-License-Identifier: MIT
 */

import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TrackedStocksPage } from '../TrackedStocksPage';
import * as stockTrackingApi from '@/lib/api/stockTracking';

// Mock the API module
vi.mock('@/lib/api/stockTracking', () => ({
  getTrackedStocks: vi.fn(),
  deactivateStockTracking: vi.fn(),
}));

// Mock date-fns
vi.mock('date-fns', () => ({
  format: vi.fn((date: Date) => {
    if (date instanceof Date && !isNaN(date.getTime())) {
      return 'Jan 01, 2024 12:00';
    }
    return 'Invalid date';
  }),
}));

describe('TrackedStocksPage', () => {
  const mockGetTrackedStocks = vi.mocked(stockTrackingApi.getTrackedStocks);
  const mockDeactivateStockTracking = vi.mocked(stockTrackingApi.deactivateStockTracking);

  const mockStocks = [
    {
      symbol: 'AAPL',
      is_active: true,
      last_pull_date: '2024-01-01T12:00:00Z',
      last_pull_status: 'success',
      error_message: null,
    },
    {
      symbol: 'TSLA',
      is_active: true,
      last_pull_date: '2024-01-01T11:00:00Z',
      last_pull_status: 'error',
      error_message: 'API rate limit exceeded',
    },
    {
      symbol: 'GOOGL',
      is_active: false,
      last_pull_date: '2024-01-01T10:00:00Z',
      last_pull_status: 'success',
      error_message: null,
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders loading state initially', () => {
    render(<TrackedStocksPage />);

    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(screen.getByText('Loading tracked stocks...')).toBeInTheDocument();
  });

  it('displays tracked stocks in table format', async () => {
    mockGetTrackedStocks.mockResolvedValue({
      status: 'success',
      message: 'Stocks retrieved successfully',
      stocks: mockStocks,
    });

    render(<TrackedStocksPage />);

    await waitFor(() => {
      expect(screen.getByText('Tracked Stocks')).toBeInTheDocument();
    });

    // Check table headers
    expect(screen.getByText('Symbol')).toBeInTheDocument();
    expect(screen.getByText('Status')).toBeInTheDocument();
    expect(screen.getByText('Last Update')).toBeInTheDocument();
    expect(screen.getByText('Last Pull Status')).toBeInTheDocument();
    expect(screen.getByText('Error Message')).toBeInTheDocument();
    expect(screen.getByText('Actions')).toBeInTheDocument();

    // Check stock data
    expect(screen.getByText('AAPL')).toBeInTheDocument();
    expect(screen.getByText('TSLA')).toBeInTheDocument();
    expect(screen.getByText('GOOGL')).toBeInTheDocument();

    // Check status badges
    expect(screen.getByText('Active')).toBeInTheDocument();
    expect(screen.getByText('Error')).toBeInTheDocument();
    expect(screen.getByText('Inactive')).toBeInTheDocument();
  });

  it('displays empty state when no stocks are tracked', async () => {
    mockGetTrackedStocks.mockResolvedValue({
      status: 'success',
      message: 'No stocks found',
      stocks: [],
    });

    render(<TrackedStocksPage />);

    await waitFor(() => {
      expect(screen.getByText('No stocks are currently being tracked.')).toBeInTheDocument();
    });

    expect(screen.getByText('0 stocks being tracked')).toBeInTheDocument();
  });

  it('handles API errors gracefully', async () => {
    mockGetTrackedStocks.mockRejectedValue({
      detail: 'Authentication required. Please log in.',
      status: 401,
    });

    render(<TrackedStocksPage />);

    await waitFor(() => {
      expect(screen.getByText('Authentication required. Please log in.')).toBeInTheDocument();
    });
  });

  it('allows refreshing the stock list', async () => {
    const user = userEvent.setup();
    mockGetTrackedStocks.mockResolvedValue({
      status: 'success',
      message: 'Stocks retrieved successfully',
      stocks: mockStocks,
    });

    render(<TrackedStocksPage />);

    await waitFor(() => {
      expect(screen.getByText('AAPL')).toBeInTheDocument();
    });

    // Click refresh button
    const refreshButton = screen.getByRole('button', { name: 'Refresh' });
    await user.click(refreshButton);

    // Should call API again
    expect(mockGetTrackedStocks).toHaveBeenCalledTimes(2);
  });

  it('shows loading state during refresh', async () => {
    const user = userEvent.setup();
    render(<TrackedStocksPage />);

    // Wait for initial load to complete
    await waitFor(() => {
      expect(screen.getByText('AAPL')).toBeInTheDocument();
    });

    // Mock the API to return a promise that doesn't resolve immediately
    const mockGetTrackedStocks = stockTrackingApi.getTrackedStocks as jest.MockedFunction<
      typeof stockTrackingApi.getTrackedStocks
    >;
    mockGetTrackedStocks.mockImplementationOnce(() => new Promise(() => {}));

    // Click refresh button
    const refreshButton = screen.getByRole('button', { name: /refresh/i });
    await user.click(refreshButton);

    // Should show loading state in the refresh button (spinner)
    expect(screen.getByRole('button', { name: /refresh/i })).toBeDisabled();
  });

  it('displays confirmation dialog for deactivation', async () => {
    const user = userEvent.setup();
    mockGetTrackedStocks.mockResolvedValue({
      status: 'success',
      message: 'Stocks retrieved successfully',
      stocks: mockStocks,
    });

    render(<TrackedStocksPage />);

    await waitFor(() => {
      expect(screen.getByText('AAPL')).toBeInTheDocument();
    });

    // Click deactivate button
    const deactivateButtons = screen.getAllByRole('button', { name: 'Deactivate' });
    await user.click(deactivateButtons[0]);

    // Should show confirmation dialog
    expect(screen.getByText('Deactivate Stock Tracking')).toBeInTheDocument();
    expect(
      screen.getByText(/Are you sure you want to deactivate tracking for AAPL/)
    ).toBeInTheDocument();
  });

  it('handles stock deactivation successfully', async () => {
    const user = userEvent.setup();
    mockGetTrackedStocks.mockResolvedValue({
      status: 'success',
      message: 'Stocks retrieved successfully',
      stocks: mockStocks,
    });
    mockDeactivateStockTracking.mockResolvedValue({
      status: 'success',
      message: 'Stock tracking deactivated successfully',
      symbol: 'AAPL',
    });

    render(<TrackedStocksPage />);

    await waitFor(() => {
      expect(screen.getByText('AAPL')).toBeInTheDocument();
    });

    // Click deactivate button
    const deactivateButtons = screen.getAllByRole('button', { name: 'Deactivate' });
    await user.click(deactivateButtons[0]);

    // Confirm deactivation
    const confirmButton = screen.getByRole('button', { name: 'Deactivate' });
    await user.click(confirmButton);

    await waitFor(() => {
      expect(mockDeactivateStockTracking).toHaveBeenCalledWith('AAPL');
    });

    // AAPL should be removed from the list
    await waitFor(() => {
      expect(screen.queryByText('AAPL')).not.toBeInTheDocument();
    });
  });

  it('handles deactivation errors', async () => {
    const user = userEvent.setup();
    mockGetTrackedStocks.mockResolvedValue({
      status: 'success',
      message: 'Stocks retrieved successfully',
      stocks: mockStocks,
    });
    mockDeactivateStockTracking.mockRejectedValue({
      detail: 'Failed to deactivate tracking',
      status: 500,
    });

    render(<TrackedStocksPage />);

    await waitFor(() => {
      expect(screen.getByText('AAPL')).toBeInTheDocument();
    });

    // Click deactivate button
    const deactivateButtons = screen.getAllByRole('button', { name: 'Deactivate' });
    await user.click(deactivateButtons[0]);

    // Confirm deactivation
    const confirmButton = screen.getByRole('button', { name: 'Deactivate' });
    await user.click(confirmButton);

    await waitFor(() => {
      expect(screen.getByText('Failed to deactivate tracking')).toBeInTheDocument();
    });
  });

  it('displays correct status icons and badges', async () => {
    render(<TrackedStocksPage />);

    await waitFor(() => {
      expect(screen.getByText('AAPL')).toBeInTheDocument();
    });

    // Check for status badges - use getAllByText since there are multiple success statuses
    const successStatuses = screen.getAllByText('success');
    expect(successStatuses).toHaveLength(2); // AAPL and GOOGL have success status

    expect(screen.getByText('error')).toBeInTheDocument(); // TSLA has error status
    expect(screen.getByText('Active')).toBeInTheDocument();
    expect(screen.getByText('Inactive')).toBeInTheDocument();
  });

  it('displays error messages in table', async () => {
    mockGetTrackedStocks.mockResolvedValue({
      status: 'success',
      message: 'Stocks retrieved successfully',
      stocks: mockStocks,
    });

    render(<TrackedStocksPage />);

    await waitFor(() => {
      expect(screen.getByText('API rate limit exceeded')).toBeInTheDocument();
    });
  });

  it('formats dates correctly', async () => {
    render(<TrackedStocksPage />);

    await waitFor(() => {
      expect(screen.getByText('AAPL')).toBeInTheDocument();
    });

    // Check for formatted dates - use getAllByText since there are multiple dates
    const formattedDates = screen.getAllByText('Jan 01, 2024 12:00');
    expect(formattedDates).toHaveLength(3); // All three stocks have the same date
  });

  it('shows "Never" for stocks without last pull date', async () => {
    const stocksWithoutDate = [
      {
        symbol: 'TEST',
        is_active: true,
        last_pull_date: '',
        last_pull_status: 'pending',
        error_message: null,
      },
    ];

    mockGetTrackedStocks.mockResolvedValue({
      status: 'success',
      message: 'Stocks retrieved successfully',
      stocks: stocksWithoutDate,
    });

    render(<TrackedStocksPage />);

    await waitFor(() => {
      expect(screen.getByText('Never')).toBeInTheDocument();
    });
  });

  it('disables deactivate button during deactivation', async () => {
    const user = userEvent.setup();

    // Use the standard mock data that includes AAPL
    mockGetTrackedStocks.mockResolvedValue({
      status: 'success',
      message: 'Stocks retrieved successfully',
      stocks: mockStocks,
    });

    render(<TrackedStocksPage />);

    await waitFor(() => {
      expect(screen.getByText('AAPL')).toBeInTheDocument();
    });

    // Mock the API to return a promise that doesn't resolve immediately
    const mockDeactivateStockTracking =
      stockTrackingApi.deactivateStockTracking as jest.MockedFunction<
        typeof stockTrackingApi.deactivateStockTracking
      >;
    mockDeactivateStockTracking.mockImplementationOnce(() => new Promise(() => {}));

    // Click the first deactivate button (AAPL)
    const deactivateButtons = screen.getAllByRole('button', { name: /deactivate/i });
    await user.click(deactivateButtons[0]);

    // Confirm deactivation
    const confirmButton = screen.getByRole('button', { name: /deactivate/i });
    await user.click(confirmButton);

    // The specific button should be disabled during deactivation
    await waitFor(() => {
      expect(deactivateButtons[0]).toBeDisabled();
    });
  });

  it('updates stock count in description', async () => {
    mockGetTrackedStocks.mockResolvedValue({
      status: 'success',
      message: 'Stocks retrieved successfully',
      stocks: mockStocks,
    });

    render(<TrackedStocksPage />);

    await waitFor(() => {
      expect(screen.getByText('3 stocks being tracked')).toBeInTheDocument();
    });
  });

  it('shows singular form for one stock', async () => {
    mockGetTrackedStocks.mockResolvedValue({
      status: 'success',
      message: 'Stocks retrieved successfully',
      stocks: [mockStocks[0]], // Only one stock
    });

    render(<TrackedStocksPage />);

    await waitFor(() => {
      expect(screen.getByText('1 stock being tracked')).toBeInTheDocument();
    });
  });
});
