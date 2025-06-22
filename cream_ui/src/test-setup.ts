/**
 * Test setup configuration for vitest.
 *
 * Configures global test environment and mocks.
 *
 * SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>
 * SPDX-License-Identifier: MIT
 */

import { vi } from 'vitest';
import '@testing-library/jest-dom';

// Mock import.meta.env for tests
vi.mock('vite', () => ({
  importMetaEnv: {
    VITE_API_BASE_URL: 'http://localhost:8000',
  },
}));

// Mock localStorage
const mockLocalStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
});

// Mock fetch globally
global.fetch = vi.fn();

// Reset mocks before each test
beforeEach(() => {
  vi.clearAllMocks();
  mockLocalStorage.getItem.mockReturnValue('test-token');
});
