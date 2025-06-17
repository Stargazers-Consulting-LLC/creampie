/**
 * Main application component that handles routing and layout.
 * Provides the base structure for the application including navigation and route protection.
 */
// @ts-expect-error - React is needed for JSX
import * as React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

// Page imports
import { LandingPage } from './pages/LandingPage';
import { SignUpPage } from './pages/auth/SignUpPage';
import { LoginPage } from './pages/auth/LoginPage';
import { VerifyEmailPage } from './pages/auth/VerifyEmailPage';

// Component imports
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { Navigation } from './components/Navigation';

// Styles
import './App.css';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/auth/signup" element={<SignUpPage />} />
          <Route path="/auth/login" element={<LoginPage />} />
          <Route path="/auth/verify-email" element={<VerifyEmailPage />} />

          {/* Protected routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <div>Dashboard (Coming Soon)</div>
              </ProtectedRoute>
            }
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
