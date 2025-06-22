/**
 * Admin Route Protection Component
 *
 * Extends ProtectedRoute to provide admin-specific route protection.
 * Ensures users have both authentication and admin privileges.
 *
 * SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>
 * SPDX-License-Identifier: MIT
 */

import * as React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { ProtectedRoute } from './ProtectedRoute';

interface AdminRouteProps {
  children: React.ReactNode;
}

export function AdminRoute({ children }: AdminRouteProps) {
  const location = useLocation();

  // First check if user is authenticated
  const token = localStorage.getItem('token');

  if (!token) {
    // Redirect to login page but save the attempted url
    return <Navigate to="/auth/login" state={{ from: location }} replace />;
  }

  // Then check for admin privileges
  const isAdmin = localStorage.getItem('adminToken') || localStorage.getItem('isAdmin') === 'true';

  if (!isAdmin) {
    // Redirect to dashboard or show access denied
    return <Navigate to="/dashboard" state={{ from: location }} replace />;
  }

  return <ProtectedRoute>{children}</ProtectedRoute>;
}
