/**
 * Stock Request Page Component
 *
 * A page that allows users to request stock tracking with a form interface.
 * Provides a clean, user-friendly interface for submitting stock tracking requests.
 *
 * SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>
 * SPDX-License-Identifier: MIT
 */

import * as React from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight } from 'lucide-react';
import { StockRequestForm } from '@/components/stock-tracking/StockRequestForm';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export function StockRequestPage() {
  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* Breadcrumb Navigation */}
      <nav className="flex items-center space-x-1 text-sm text-muted-foreground">
        <Link to="/" className="hover:text-foreground transition-colors">
          Home
        </Link>
        <ChevronRight className="h-4 w-4" />
        <span className="text-foreground">Request Stock Tracking</span>
      </nav>

      {/* Page Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Request Stock Tracking</h1>
        <p className="text-muted-foreground">
          Submit a request to track a stock symbol. We&apos;ll monitor the stock and provide you
          with updates.
        </p>
      </div>

      {/* Main Content */}
      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Stock Tracking Request</CardTitle>
            <CardDescription>
              Enter the stock symbol you&apos;d like to track. We&apos;ll start monitoring it
              immediately.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <StockRequestForm />
          </CardContent>
        </Card>

        {/* Additional Information */}
        <Card>
          <CardHeader>
            <CardTitle>How it works</CardTitle>
            <CardDescription>
              Learn about our stock tracking process and what to expect.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-3">
              <div className="space-y-2">
                <h4 className="font-semibold">1. Submit Request</h4>
                <p className="text-sm text-muted-foreground">
                  Enter a valid stock symbol and submit your tracking request.
                </p>
              </div>
              <div className="space-y-2">
                <h4 className="font-semibold">2. Processing</h4>
                <p className="text-sm text-muted-foreground">
                  We&apos;ll validate the symbol and begin monitoring the stock.
                </p>
              </div>
              <div className="space-y-2">
                <h4 className="font-semibold">3. That&apos;s It.</h4>
                <p className="text-sm text-muted-foreground">
                  Really. The only reason I don&apos;t process the entire market is because most of
                  it isn&apos;t interesting.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
