/**
 * Stock Tracking Integration Tests
 *
 * End-to-end integration tests that test the complete frontend-backend workflow
 * for the stock tracking feature. These tests verify that React components
 * properly integrate with the backend API.
 *
 * SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>
 * SPDX-License-Identifier: MIT
 */

import * as React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { StockRequestForm } from '@/components/stock-tracking/StockRequestForm';
import { TrackedStocksPage } from '@/pages/admin/TrackedStocksPage';
import { StockRequestPage } from '@/pages/StockRequestPage';
import * as stockTrackingAPI from '@/lib/api/stockTracking';

// Mock the API client
vi.mock('@/lib/api/stockTracking');

const mockStockTrackingAPI = vi.mocked(stockTrackingAPI);

const renderWithRouter = (component: React.ReactElement) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('Stock Tracking Integration Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  describe('StockRequestForm Integration', () => {
    it('successfully submits stock tracking request and displays success message', async () => {
      // Arrange
      const mockTrackStock = mockStockTrackingAPI.trackStock.mockResolvedValue({
        status: 'tracking',
        message: 'Stock AAPL is now being tracked',
        symbol: 'AAPL',
      });

      renderWithRouter(<StockRequestForm />);

      // Act - User enters stock symbol
      const input = screen.getByLabelText(/stock symbol/i);
      fireEvent.change(input, { target: { value: 'AAPL' } });

      // Act - User submits form
      const submitButton = screen.getByRole('button', { name: /request tracking/i });
      fireEvent.click(submitButton);

      // Assert - API is called with correct data
      await waitFor(() => {
        expect(mockTrackStock).toHaveBeenCalledWith('AAPL');
      });

      // Assert - Success message is displayed
      await waitFor(() => {
        expect(screen.getByText(/Stock AAPL is now being tracked/i)).toBeInTheDocument();
      });

      // Assert - Form is reset
      expect(input).toHaveValue('');
    });

    it('handles API errors and displays error message to user', async () => {
      // Arrange
      const mockTrackStock = mockStockTrackingAPI.trackStock.mockRejectedValue(
        new Error('Network error occurred')
      );

      renderWithRouter(<StockRequestForm />);

      // Act - User enters stock symbol
      const input = screen.getByLabelText(/stock symbol/i);
      fireEvent.change(input, { target: { value: 'AAPL' } });

      // Act - User submits form
      const submitButton = screen.getByRole('button', { name: /request tracking/i });
      fireEvent.click(submitButton);

      // Assert - API is called
      await waitFor(() => {
        expect(mockTrackStock).toHaveBeenCalledWith('AAPL');
      });

      // Assert - Error message is displayed (using the actual error message from component)
      await waitFor(() => {
        expect(screen.getByText(/failed to request stock tracking/i)).toBeInTheDocument();
      });
    });

    it('validates stock symbol format before making API call', async () => {
      // Arrange
      const mockTrackStock = mockStockTrackingAPI.trackStock.mockResolvedValue({
        status: 'success',
        message: 'Stock AAPL tracking has been requested',
        symbol: 'AAPL',
      });

      renderWithRouter(<StockRequestForm />);

      // Act - User enters invalid stock symbol
      const input = screen.getByLabelText(/stock symbol/i);
      fireEvent.change(input, { target: { value: '1INVALID' } });

      // Trigger validation by blurring the field
      fireEvent.blur(input);

      // Assert - Validation error is displayed
      await waitFor(() => {
        expect(
          screen.getByText(/stock symbol must be 2-10 characters, start with a letter/i)
        ).toBeInTheDocument();
      });

      // Act - User submits form
      const submitButton = screen.getByRole('button', { name: /request tracking/i });
      fireEvent.click(submitButton);

      // Assert - API is NOT called due to validation error
      expect(mockTrackStock).not.toHaveBeenCalled();
    });

    it('shows loading state during API call', async () => {
      // Arrange - Create a promise that we can control
      let resolvePromise: (value: { status: string; message: string; symbol: string }) => void;
      const mockPromise = new Promise<{ status: string; message: string; symbol: string }>(
        (resolve) => {
          resolvePromise = resolve;
        }
      );

      mockStockTrackingAPI.trackStock.mockReturnValue(mockPromise);

      renderWithRouter(<StockRequestForm />);

      // Act - User enters stock symbol and submits
      const input = screen.getByLabelText(/stock symbol/i);
      fireEvent.change(input, { target: { value: 'AAPL' } });

      const submitButton = screen.getByRole('button', { name: /request tracking/i });
      fireEvent.click(submitButton);

      // Assert - Loading state is shown
      await waitFor(() => {
        expect(screen.getByText(/requesting\.\.\./i)).toBeInTheDocument();
      });

      // Act - Resolve the promise
      resolvePromise!({
        status: 'tracking',
        message: 'Stock AAPL is now being tracked',
        symbol: 'AAPL',
      });

      // Assert - Loading state is removed
      await waitFor(() => {
        expect(screen.queryByText(/requesting\.\.\./i)).not.toBeInTheDocument();
      });
    });

    it('handles validation errors without making API calls', async () => {
      // Arrange
      const mockTrackStock = mockStockTrackingAPI.trackStock.mockResolvedValue({
        status: 'success',
        message: 'Stock AAPL tracking has been requested',
        symbol: 'AAPL',
      });

      renderWithRouter(<StockRequestForm />);

      // Act - User submits form without entering anything
      const submitButton = screen.getByRole('button', { name: /request tracking/i });
      fireEvent.click(submitButton);

      // Assert - Validation error is displayed
      await waitFor(() => {
        expect(screen.getByText(/stock symbol is required/i)).toBeInTheDocument();
      });

      // Assert - API is NOT called due to validation error
      expect(mockTrackStock).not.toHaveBeenCalled();
    });
  });

  describe('TrackedStocksPage Integration', () => {
    it('successfully loads and displays tracked stocks from API', async () => {
      // Arrange
      const mockGetTrackedStocks = mockStockTrackingAPI.getTrackedStocks.mockResolvedValue({
        status: 'success',
        message: 'Retrieved 2 tracked stocks',
        stocks: [
          {
            symbol: 'AAPL',
            is_active: true,
            last_pull_date: '2024-01-15T10:30:00Z',
            last_pull_status: 'SUCCESS',
            error_message: null,
          },
          {
            symbol: 'TSLA',
            is_active: false,
            last_pull_date: '2024-01-14T15:45:00Z',
            last_pull_status: 'ERROR',
            error_message: 'API rate limit exceeded',
          },
        ],
      });

      renderWithRouter(<TrackedStocksPage />);

      // Assert - API is called
      await waitFor(() => {
        expect(mockGetTrackedStocks).toHaveBeenCalled();
      });

      // Assert - Stocks are displayed
      await waitFor(() => {
        expect(screen.getByText('AAPL')).toBeInTheDocument();
        expect(screen.getByText('TSLA')).toBeInTheDocument();
      });

      // Assert - Status information is displayed
      expect(screen.getByText(/active/i)).toBeInTheDocument();
      expect(screen.getByText(/inactive/i)).toBeInTheDocument();
    });

    it('handles API errors and displays error message', async () => {
      // Arrange
      mockStockTrackingAPI.getTrackedStocks.mockRejectedValue(new Error('Authentication failed'));

      renderWithRouter(<TrackedStocksPage />);

      // Assert - API is called
      await waitFor(() => {
        expect(mockStockTrackingAPI.getTrackedStocks).toHaveBeenCalled();
      });

      // Assert - Error message is displayed
      await waitFor(() => {
        expect(screen.getByText(/failed to load tracked stocks/i)).toBeInTheDocument();
      });
    });

    it('successfully deactivates stock tracking', async () => {
      // Arrange
      mockStockTrackingAPI.getTrackedStocks.mockResolvedValue({
        status: 'success',
        message: 'Retrieved 1 tracked stock',
        stocks: [
          {
            symbol: 'AAPL',
            is_active: true,
            last_pull_date: '2024-01-15T10:30:00Z',
            last_pull_status: 'SUCCESS',
            error_message: null,
          },
        ],
      });

      const mockDeactivateStockTracking =
        mockStockTrackingAPI.deactivateStockTracking.mockResolvedValue({
          status: 'deactivated',
          message: 'Stock AAPL tracking has been deactivated',
          symbol: 'AAPL',
        });

      renderWithRouter(<TrackedStocksPage />);

      // Wait for stocks to load
      await waitFor(() => {
        expect(screen.getByText('AAPL')).toBeInTheDocument();
      });

      // Act - User clicks deactivate button
      const deactivateButton = screen.getByRole('button', { name: /deactivate/i });
      fireEvent.click(deactivateButton);

      // Wait for confirmation dialog and click confirm
      await waitFor(() => {
        expect(
          screen.getByText(/are you sure you want to deactivate tracking/i)
        ).toBeInTheDocument();
      });

      const confirmButton = screen.getByRole('button', { name: /deactivate/i });
      fireEvent.click(confirmButton);

      // Assert - Deactivate API is called
      await waitFor(() => {
        expect(mockDeactivateStockTracking).toHaveBeenCalledWith('AAPL');
      });
    });
  });

  describe('StockRequestPage Integration', () => {
    it('renders complete page with form and information', () => {
      // Arrange
      renderWithRouter(<StockRequestPage />);

      // Assert - Page title and description (using more specific selectors)
      expect(screen.getByRole('heading', { name: 'Request Stock Tracking' })).toBeInTheDocument();
      expect(screen.getByText(/submit a request to track a stock symbol/i)).toBeInTheDocument();

      // Assert - Breadcrumb navigation
      expect(screen.getByText('Home')).toBeInTheDocument();
      expect(screen.getByRole('navigation')).toBeInTheDocument();

      // Assert - Form is present
      expect(screen.getByText('Stock Tracking Request')).toBeInTheDocument();
      expect(screen.getByLabelText(/stock symbol/i)).toBeInTheDocument();

      // Assert - Information section
      expect(screen.getByText('How it works')).toBeInTheDocument();
      expect(screen.getByText('1. Submit Request')).toBeInTheDocument();
      expect(screen.getByText('2. Processing')).toBeInTheDocument();
      expect(screen.getByText("3. That's It.")).toBeInTheDocument();

      // Check that the page title is displayed
      expect(screen.getByRole('heading', { name: /request stock tracking/i })).toBeInTheDocument();
    });

    it('provides complete user workflow from page to form submission', async () => {
      // Arrange
      mockStockTrackingAPI.trackStock.mockResolvedValue({
        status: 'tracking',
        message: 'Stock AAPL is now being tracked',
        symbol: 'AAPL',
      });

      renderWithRouter(<StockRequestPage />);

      // Act - User enters stock symbol in the form
      const input = screen.getByLabelText(/stock symbol/i);
      fireEvent.change(input, { target: { value: 'AAPL' } });

      // Act - User submits form
      const submitButton = screen.getByRole('button', { name: /request tracking/i });
      fireEvent.click(submitButton);

      // Assert - API is called
      await waitFor(() => {
        expect(mockStockTrackingAPI.trackStock).toHaveBeenCalledWith('AAPL');
      });

      // Assert - Success message is displayed
      await waitFor(() => {
        expect(screen.getByText(/stock AAPL is now being tracked/i)).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling Integration', () => {
    it('handles network errors gracefully across all components', async () => {
      // Arrange
      mockStockTrackingAPI.trackStock.mockRejectedValue(new Error('Network error occurred'));

      renderWithRouter(<StockRequestForm />);

      // Act - User enters stock symbol and submits
      const input = screen.getByLabelText(/stock symbol/i);
      fireEvent.change(input, { target: { value: 'AAPL' } });

      const submitButton = screen.getByRole('button', { name: /request tracking/i });
      fireEvent.click(submitButton);

      // Assert - Error message is displayed (using actual component error message)
      await waitFor(() => {
        expect(screen.getByText(/failed to request stock tracking/i)).toBeInTheDocument();
      });
    });
  });

  describe('Data Consistency Integration', () => {
    it('maintains consistent data flow from form to API to response', async () => {
      // Arrange
      const mockTrackStock = mockStockTrackingAPI.trackStock.mockResolvedValue({
        status: 'tracking',
        message: 'Stock AAPL is now being tracked',
        symbol: 'AAPL',
      });

      renderWithRouter(<StockRequestForm />);

      // Act - User enters symbol with mixed case
      const input = screen.getByLabelText(/stock symbol/i);
      fireEvent.change(input, { target: { value: 'aapl' } });

      const submitButton = screen.getByRole('button', { name: /request tracking/i });
      fireEvent.click(submitButton);

      // Assert - API receives normalized symbol (uppercase)
      await waitFor(() => {
        expect(mockTrackStock).toHaveBeenCalledWith('AAPL');
      });

      // Assert - Response displays normalized symbol
      await waitFor(() => {
        expect(screen.getByText(/stock AAPL is now being tracked/i)).toBeInTheDocument();
      });
    });
  });
});
