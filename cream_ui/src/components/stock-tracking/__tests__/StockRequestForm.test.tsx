/**
 * Stock Request Form Component Tests
 *
 * Comprehensive test suite for the StockRequestForm component, covering
 * form validation, submission, error handling, and user interactions.
 *
 * SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>
 * SPDX-License-Identifier: MIT
 */

import * as React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { StockRequestForm } from '../StockRequestForm';
import * as stockTrackingApi from '@/lib/api/stockTracking';

// Mock the API module
vi.mock('@/lib/api/stockTracking', () => ({
  trackStock: vi.fn(),
  isValidStockSymbol: vi.fn(),
}));

describe('StockRequestForm', () => {
  const mockTrackStock = vi.mocked(stockTrackingApi.trackStock);

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the form with correct elements', () => {
    render(<StockRequestForm />);

    expect(screen.getByText('Request Stock Tracking')).toBeInTheDocument();
    expect(
      screen.getByText(
        'Enter a stock symbol to request tracking. The symbol will be automatically validated and processed.'
      )
    ).toBeInTheDocument();
    expect(screen.getByLabelText('Stock Symbol')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('e.g., AAPL, TSLA, GOOGL')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Request Tracking' })).toBeInTheDocument();
  });

  it('validates required field', async () => {
    const user = userEvent.setup();
    render(<StockRequestForm />);

    const submitButton = screen.getByRole('button', { name: 'Request Tracking' });

    // Try to submit without entering a value
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Stock symbol is required')).toBeInTheDocument();
    });
  });

  it('validates stock symbol format', async () => {
    const user = userEvent.setup();
    render(<StockRequestForm />);

    const input = screen.getByLabelText('Stock Symbol');
    const submitButton = screen.getByRole('button', { name: 'Request Tracking' });

    // Enter invalid symbol
    await user.type(input, '123');
    await user.click(submitButton);

    await waitFor(() => {
      expect(
        screen.getByText(/Stock symbol must be 2-10 characters, start with a letter/)
      ).toBeInTheDocument();
    });
  });

  it('validates symbol length', async () => {
    const user = userEvent.setup();
    render(<StockRequestForm />);

    const input = screen.getByLabelText('Stock Symbol');
    const submitButton = screen.getByRole('button', { name: 'Request Tracking' });

    // Enter single character
    await user.type(input, 'A');
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Stock symbol must be at least 2 characters')).toBeInTheDocument();
    });
  });

  it('auto-uppercases input', async () => {
    const user = userEvent.setup();
    render(<StockRequestForm />);

    const input = screen.getByLabelText('Stock Symbol');

    await user.type(input, 'aapl');

    expect(input).toHaveValue('AAPL');
  });

  it('submits form with valid data', async () => {
    const user = userEvent.setup();
    const onSuccess = vi.fn();
    mockTrackStock.mockResolvedValue({
      status: 'tracking',
      message: 'Stock tracking requested successfully',
      symbol: 'AAPL',
    });

    render(<StockRequestForm onSuccess={onSuccess} />);

    const input = screen.getByLabelText('Stock Symbol');
    const submitButton = screen.getByRole('button', { name: 'Request Tracking' });

    await user.type(input, 'AAPL');
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockTrackStock).toHaveBeenCalledWith('AAPL');
    });

    await waitFor(() => {
      expect(onSuccess).toHaveBeenCalledWith('AAPL');
    });
  });

  it('shows loading state during submission', async () => {
    const user = userEvent.setup();
    mockTrackStock.mockImplementation(() => new Promise((resolve) => setTimeout(resolve, 100)));

    render(<StockRequestForm />);

    const input = screen.getByLabelText('Stock Symbol');
    const submitButton = screen.getByRole('button', { name: 'Request Tracking' });

    await user.type(input, 'AAPL');
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Requesting...')).toBeInTheDocument();
    });
  });

  it('handles API errors', async () => {
    const user = userEvent.setup();
    const onError = vi.fn();
    mockTrackStock.mockRejectedValue({ detail: 'Stock symbol not found' });

    render(<StockRequestForm onError={onError} />);

    const input = screen.getByLabelText('Stock Symbol');
    const submitButton = screen.getByRole('button', { name: 'Request Tracking' });

    await user.type(input, 'INVALID');
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Stock symbol not found')).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(onError).toHaveBeenCalledWith('Stock symbol not found');
    });
  });

  it('handles network errors', async () => {
    const user = userEvent.setup();
    mockTrackStock.mockRejectedValue({ detail: 'Failed to request stock tracking' });

    render(<StockRequestForm />);

    const input = screen.getByLabelText('Stock Symbol');
    const submitButton = screen.getByRole('button', { name: 'Request Tracking' });

    await user.type(input, 'AAPL');
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Failed to request stock tracking/)).toBeInTheDocument();
    });
  });

  it('calls onSuccess callback when successful', async () => {
    const user = userEvent.setup();
    const onSuccess = vi.fn();
    mockTrackStock.mockResolvedValue({
      status: 'tracking',
      message: 'Success',
      symbol: 'AAPL',
    });

    render(<StockRequestForm onSuccess={onSuccess} />);

    const input = screen.getByLabelText('Stock Symbol');
    const submitButton = screen.getByRole('button', { name: 'Request Tracking' });

    await user.type(input, 'AAPL');
    await user.click(submitButton);

    await waitFor(() => {
      expect(onSuccess).toHaveBeenCalledWith('AAPL');
    });
  });

  it('calls onError callback when error occurs', async () => {
    const user = userEvent.setup();
    const onError = vi.fn();
    mockTrackStock.mockRejectedValue({ detail: 'API Error' });

    render(<StockRequestForm onError={onError} />);

    const input = screen.getByLabelText('Stock Symbol');
    const submitButton = screen.getByRole('button', { name: 'Request Tracking' });

    await user.type(input, 'AAPL');
    await user.click(submitButton);

    await waitFor(() => {
      expect(onError).toHaveBeenCalledWith('API Error');
    });
  });

  it('clears form after successful submission', async () => {
    const user = userEvent.setup();
    mockTrackStock.mockResolvedValue({
      status: 'tracking',
      message: 'Success',
      symbol: 'AAPL',
    });

    render(<StockRequestForm />);

    const input = screen.getByLabelText('Stock Symbol');
    const submitButton = screen.getByRole('button', { name: 'Request Tracking' });

    await user.type(input, 'AAPL');
    await user.click(submitButton);

    await waitFor(() => {
      expect(input).toHaveValue('');
    });
  });

  it('clears error message when user starts typing', async () => {
    const user = userEvent.setup();
    mockTrackStock.mockRejectedValue({ detail: 'API Error' });

    render(<StockRequestForm />);

    const input = screen.getByLabelText('Stock Symbol');
    const submitButton = screen.getByRole('button', { name: 'Request Tracking' });

    // First, trigger an error
    await user.type(input, 'AAPL');
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('API Error')).toBeInTheDocument();
    });

    // Then start typing to clear the error
    await user.clear(input);
    await user.type(input, 'T');

    await waitFor(() => {
      expect(screen.queryByText('API Error')).not.toBeInTheDocument();
    });
  });

  it('submit button is enabled when form is not submitting', async () => {
    render(<StockRequestForm />);

    const submitButton = screen.getByRole('button', { name: 'Request Tracking' });
    expect(submitButton).not.toBeDisabled();
  });

  it('submit button is disabled when form is submitting', async () => {
    const user = userEvent.setup();
    mockTrackStock.mockImplementation(() => new Promise((resolve) => setTimeout(resolve, 100)));

    render(<StockRequestForm />);

    const input = screen.getByLabelText('Stock Symbol');
    const submitButton = screen.getByRole('button', { name: 'Request Tracking' });

    await user.type(input, 'AAPL');
    await user.click(submitButton);

    await waitFor(() => {
      expect(submitButton).toBeDisabled();
    });
  });

  it('applies custom className', () => {
    render(<StockRequestForm className="custom-class" />);

    const card = screen.getByText('Request Stock Tracking').closest('[data-slot="card"]');
    expect(card).toHaveClass('custom-class');
  });
});
