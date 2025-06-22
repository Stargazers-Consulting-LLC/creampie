/**
 * Protected Route Component
 *
 * Route protection component that ensures users are authenticated before
 * accessing protected routes. Redirects to login if not authenticated.
 *
 * SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>
 * SPDX-License-Identifier: MIT
 */

import * as React from 'react';
import { Navigate, useLocation } from 'react-router-dom';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const location = useLocation();
  const token = localStorage.getItem('token');

  if (!token) {
    // Redirect to login page but save the attempted url
    return <Navigate to="/auth/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
}
