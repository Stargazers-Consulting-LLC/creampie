/**
 * Main application component that handles routing and layout.
 * Provides the base structure for the application including navigation and route protection.
 *
 * SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>
 * SPDX-License-Identifier: MIT
 */
// @ts-expect-error - React is needed for JSX
import * as React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

// Page imports
import { LandingPage } from './pages/LandingPage';
import { SignUpPage } from './pages/auth/SignUpPage';
import { LoginPage } from './pages/auth/LoginPage';
import { StockRequestPage } from './pages/StockRequestPage';
import { TrackedStocksPage } from './pages/admin/TrackedStocksPage';

// Component imports
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { AdminRoute } from './components/auth/AdminRoute';
import { Navigation } from './components/Navigation';

// Styles
import './App.css';

export function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/auth/signup" element={<SignUpPage />} />
          <Route path="/auth/login" element={<LoginPage />} />

          {/* Protected routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <div>Dashboard (Coming Soon)</div>
              </ProtectedRoute>
            }
          />

          {/* Stock Tracking Routes */}
          <Route
            path="/stock-request"
            element={
              <ProtectedRoute>
                <StockRequestPage />
              </ProtectedRoute>
            }
          />

          {/* Admin Routes */}
          <Route
            path="/admin/tracked-stocks"
            element={
              <AdminRoute>
                <TrackedStocksPage />
              </AdminRoute>
            }
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
