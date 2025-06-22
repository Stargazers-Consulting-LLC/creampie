/**
 * Email verification page component.
 * Handles email verification flow and provides resend functionality.
 *
 * SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>
 * SPDX-License-Identifier: MIT
 */

import * as React from 'react';
import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

export function VerifyEmailPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [isResending, setIsResending] = useState(false);
  const [resendSuccess, setResendSuccess] = useState(false);
  const email = location.state?.email;

  const handleResendEmail = async () => {
    if (!email) return;

    setIsResending(true);
    try {
      const response = await fetch('/api/auth/resend-verification', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      if (!response.ok) {
        throw new Error('Failed to resend verification email');
      }

      setResendSuccess(true);
    } catch (error) {
      console.error('Error resending verification email:', error);
    } finally {
      setIsResending(false);
    }
  };

  if (!email) {
    navigate('/auth/signup');
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Verify your email
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          We&apos;ve sent a verification link to{' '}
          <span className="font-medium text-indigo-600">{email}</span>
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <div className="space-y-6">
            <div className="text-sm text-gray-500">
              <p className="mb-4">
                Please check your email and click the verification link to activate your account.
                The link will expire in 72 hours.
              </p>
              <p>
                If you don&apos;t see the email, check your spam folder or click the button below to
                resend the verification email.
              </p>
            </div>

            <div>
              <button
                onClick={handleResendEmail}
                disabled={isResending || resendSuccess}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isResending
                  ? 'Sending...'
                  : resendSuccess
                    ? 'Email sent!'
                    : 'Resend verification email'}
              </button>
            </div>

            <div className="text-center">
              <a
                href="/auth/login"
                className="text-sm font-medium text-indigo-600 hover:text-indigo-500"
              >
                Return to sign in
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
