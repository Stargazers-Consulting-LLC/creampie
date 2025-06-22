/**
 * Tracked Stocks Management Page
 *
 * Admin page for viewing and managing all tracked stocks. Provides a table view
 * of stocks with their status, last update information, and ability to deactivate tracking.
 *
 * SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>
 * SPDX-License-Identifier: MIT
 */

import * as React from 'react';
import { format } from 'date-fns';
import {
  getTrackedStocks,
  deactivateStockTracking,
  type StockInfo,
  type ApiError,
} from '@/lib/api/stockTracking';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Loader2, AlertTriangle, CheckCircle, XCircle, RefreshCw } from 'lucide-react';

interface TrackedStocksPageProps {
  className?: string;
}

export function TrackedStocksPage({ className }: TrackedStocksPageProps) {
  const [stocks, setStocks] = React.useState<StockInfo[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);
  const [isRefreshing, setIsRefreshing] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [deactivatingSymbol, setDeactivatingSymbol] = React.useState<string | null>(null);

  // Load tracked stocks on component mount
  React.useEffect(() => {
    loadTrackedStocks();
  }, []);

  const loadTrackedStocks = async () => {
    try {
      setError(null);
      const response = await getTrackedStocks();
      setStocks(response.stocks);
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.detail || 'Failed to load tracked stocks');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await loadTrackedStocks();
    setIsRefreshing(false);
  };

  const handleDeactivateStock = async (symbol: string) => {
    setDeactivatingSymbol(symbol);
    try {
      await deactivateStockTracking(symbol);
      // Remove the stock from the list
      setStocks((prevStocks) => prevStocks.filter((stock) => stock.symbol !== symbol));
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.detail || `Failed to deactivate tracking for ${symbol}`);
    } finally {
      setDeactivatingSymbol(null);
    }
  };

  const getStatusBadge = (stock: StockInfo) => {
    if (!stock.is_active) {
      return <Badge variant="secondary">Inactive</Badge>;
    }

    if (stock.last_pull_status === 'success') {
      return (
        <Badge variant="default" className="bg-green-100 text-green-800">
          Active
        </Badge>
      );
    } else if (stock.last_pull_status === 'error') {
      return <Badge variant="destructive">Error</Badge>;
    } else {
      return <Badge variant="outline">Pending</Badge>;
    }
  };

  const getStatusIcon = (stock: StockInfo) => {
    if (!stock.is_active) {
      return <XCircle className="h-4 w-4 text-gray-400" />;
    }

    if (stock.last_pull_status === 'success') {
      return <CheckCircle className="h-4 w-4 text-green-600" />;
    } else if (stock.last_pull_status === 'error') {
      return <AlertTriangle className="h-4 w-4 text-red-600" />;
    } else {
      return <Loader2 className="h-4 w-4 text-yellow-600 animate-spin" />;
    }
  };

  const formatDate = (dateString: string) => {
    try {
      return format(new Date(dateString), 'MMM dd, yyyy HH:mm');
    } catch {
      return 'Invalid date';
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto py-6 space-y-6">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="flex items-center space-x-2" role="status" aria-live="polite">
            <Loader2 className="h-6 w-6 animate-spin" />
            <span>Loading tracked stocks...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`container mx-auto py-6 space-y-6 ${className}`}>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Tracked Stocks</h1>
          <p className="text-muted-foreground">Manage and monitor all tracked stock symbols</p>
        </div>
        <Button onClick={handleRefresh} disabled={isRefreshing} variant="outline" size="sm">
          {isRefreshing ? (
            <Loader2 className="h-4 w-4 animate-spin mr-2" />
          ) : (
            <RefreshCw className="h-4 w-4 mr-2" />
          )}
          Refresh
        </Button>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Stock Tracking Status</CardTitle>
          <CardDescription>
            {stocks.length} stock{stocks.length !== 1 ? 's' : ''} being tracked
          </CardDescription>
        </CardHeader>
        <CardContent>
          {stocks.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <AlertTriangle className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <p>No stocks are currently being tracked.</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Symbol</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Last Update</TableHead>
                  <TableHead>Last Pull Status</TableHead>
                  <TableHead>Error Message</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {stocks.map((stock) => (
                  <TableRow key={stock.symbol}>
                    <TableCell className="font-medium">{stock.symbol}</TableCell>
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(stock)}
                        {getStatusBadge(stock)}
                      </div>
                    </TableCell>
                    <TableCell>
                      {stock.last_pull_date ? formatDate(stock.last_pull_date) : 'Never'}
                    </TableCell>
                    <TableCell>
                      <span className="capitalize">{stock.last_pull_status || 'Unknown'}</span>
                    </TableCell>
                    <TableCell>
                      {stock.error_message ? (
                        <span
                          className="text-sm text-red-600 max-w-xs truncate block"
                          title={stock.error_message}
                        >
                          {stock.error_message}
                        </span>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      <AlertDialog>
                        <AlertDialogTrigger asChild>
                          <Button
                            variant="destructive"
                            size="sm"
                            disabled={deactivatingSymbol === stock.symbol}
                          >
                            {deactivatingSymbol === stock.symbol ? (
                              <Loader2 className="h-4 w-4 animate-spin mr-2" />
                            ) : null}
                            Deactivate
                          </Button>
                        </AlertDialogTrigger>
                        <AlertDialogContent>
                          <AlertDialogHeader>
                            <AlertDialogTitle>Deactivate Stock Tracking</AlertDialogTitle>
                            <AlertDialogDescription>
                              Are you sure you want to deactivate tracking for {stock.symbol}? This
                              action cannot be undone and will stop all data collection for this
                              stock.
                            </AlertDialogDescription>
                          </AlertDialogHeader>
                          <AlertDialogFooter>
                            <AlertDialogCancel>Cancel</AlertDialogCancel>
                            <AlertDialogAction
                              onClick={() => handleDeactivateStock(stock.symbol)}
                              className="bg-red-600 hover:bg-red-700"
                            >
                              Deactivate
                            </AlertDialogAction>
                          </AlertDialogFooter>
                        </AlertDialogContent>
                      </AlertDialog>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
