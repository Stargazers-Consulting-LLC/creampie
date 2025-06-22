/**
 * StockRequestPage Component Tests
 *
 * Comprehensive unit tests for the StockRequestPage component covering
 * navigation, layout, breadcrumbs, and integration with StockRequestForm.
 *
 * SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>
 * SPDX-License-Identifier: MIT
 */

import * as React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { StockRequestPage } from '../StockRequestPage';

// Mock the StockRequestForm component
vi.mock('@/components/stock-tracking/StockRequestForm', () => ({
  StockRequestForm: () => <div data-testid="stock-request-form">Stock Request Form</div>,
}));

// Mock the Card components
vi.mock('@/components/ui/card', () => ({
  Card: ({ children, ...props }: React.ComponentProps<'div'>) => (
    <div data-testid="card" {...props}>
      {children}
    </div>
  ),
  CardContent: ({ children, ...props }: React.ComponentProps<'div'>) => (
    <div data-testid="card-content" {...props}>
      {children}
    </div>
  ),
  CardDescription: ({ children, ...props }: React.ComponentProps<'div'>) => (
    <div data-testid="card-description" {...props}>
      {children}
    </div>
  ),
  CardHeader: ({ children, ...props }: React.ComponentProps<'div'>) => (
    <div data-testid="card-header" {...props}>
      {children}
    </div>
  ),
  CardTitle: ({ children, ...props }: React.ComponentProps<'div'>) => (
    <div data-testid="card-title" {...props}>
      {children}
    </div>
  ),
}));

const renderWithRouter = (component: React.ReactElement) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('StockRequestPage', () => {
  it('renders the page with correct title and description', () => {
    renderWithRouter(<StockRequestPage />);

    // Use getAllByText to handle multiple elements with same text
    const titleElements = screen.getAllByText('Request Stock Tracking');
    expect(titleElements).toHaveLength(2); // One in breadcrumb, one in page title

    expect(screen.getByText(/Submit a request to track a stock symbol/)).toBeInTheDocument();
  });

  it('renders breadcrumb navigation', () => {
    renderWithRouter(<StockRequestPage />);

    expect(screen.getByText('Home')).toBeInTheDocument();
    // Check for breadcrumb specifically by looking for the span element within nav
    const navElement = screen.getByRole('navigation');
    const breadcrumbElement = within(navElement).getByText('Request Stock Tracking');
    expect(breadcrumbElement).toHaveClass('text-foreground');
  });

  it('renders the StockRequestForm component', () => {
    renderWithRouter(<StockRequestPage />);

    expect(screen.getByTestId('stock-request-form')).toBeInTheDocument();
  });

  it('renders the main content cards', () => {
    renderWithRouter(<StockRequestPage />);

    const cards = screen.getAllByTestId('card');
    expect(cards).toHaveLength(2); // Main form card and info card
  });

  it('renders the stock tracking request card with correct content', () => {
    renderWithRouter(<StockRequestPage />);

    expect(screen.getByText('Stock Tracking Request')).toBeInTheDocument();
    expect(screen.getByText(/Enter the stock symbol you'd like to track/)).toBeInTheDocument();
  });

  it('renders the how it works section', () => {
    renderWithRouter(<StockRequestPage />);

    expect(screen.getByText('How it works')).toBeInTheDocument();
    expect(
      screen.getByText('Learn about our stock tracking process and what to expect.')
    ).toBeInTheDocument();
  });

  it('renders the three-step process', () => {
    renderWithRouter(<StockRequestPage />);

    expect(screen.getByText('1. Submit Request')).toBeInTheDocument();
    expect(screen.getByText('2. Processing')).toBeInTheDocument();
    expect(screen.getByText("3. That's It.")).toBeInTheDocument(); // Updated text
  });

  it('renders step descriptions', () => {
    renderWithRouter(<StockRequestPage />);

    expect(
      screen.getByText(/Enter a valid stock symbol and submit your tracking request/)
    ).toBeInTheDocument();
    expect(
      screen.getByText(/We'll validate the symbol and begin monitoring the stock/)
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        /Really. The only reason I don't process the entire market is because most of it isn't interesting/
      )
    ).toBeInTheDocument(); // Updated text
  });

  it('has proper page structure with container and spacing', () => {
    renderWithRouter(<StockRequestPage />);

    // Use getAllByText to handle multiple elements with same text
    const titleElements = screen.getAllByText('Request Stock Tracking');
    expect(titleElements).toHaveLength(2);

    const container = titleElements[1].closest('.container'); // Use the page title element
    expect(container).toBeInTheDocument();
  });

  it('renders breadcrumb with proper navigation link', () => {
    renderWithRouter(<StockRequestPage />);

    const homeLink = screen.getByText('Home').closest('a');
    expect(homeLink).toHaveAttribute('href', '/');
  });
});
