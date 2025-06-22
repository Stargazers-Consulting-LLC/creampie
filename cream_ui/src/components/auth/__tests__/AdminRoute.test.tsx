/**
 * AdminRoute Component Tests
 *
 * Tests for the AdminRoute component that protects routes requiring admin access.
 *
 * SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>
 * SPDX-License-Identifier: MIT
 */

import * as React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AdminRoute } from '../AdminRoute';

// Mock ProtectedRoute to return children directly
vi.mock('../ProtectedRoute', () => ({
  ProtectedRoute: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

const TestContent = () => <div data-testid="test-content">Admin Content</div>;

describe('AdminRoute', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
  });

  afterEach(() => {
    // Clean up localStorage after each test
    localStorage.clear();
  });

  it('renders content when user has token and adminToken', () => {
    localStorage.setItem('token', 'user-token');
    localStorage.setItem('adminToken', 'admin-token');

    render(
      <MemoryRouter>
        <AdminRoute>
          <TestContent />
        </AdminRoute>
      </MemoryRouter>
    );

    expect(screen.getByTestId('test-content')).toBeInTheDocument();
  });

  it('renders content when user has token and isAdmin=true', () => {
    localStorage.setItem('token', 'user-token');
    localStorage.setItem('isAdmin', 'true');

    render(
      <MemoryRouter>
        <AdminRoute>
          <TestContent />
        </AdminRoute>
      </MemoryRouter>
    );

    expect(screen.getByTestId('test-content')).toBeInTheDocument();
  });
});
