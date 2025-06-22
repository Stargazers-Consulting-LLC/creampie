/**
 * Stock Request Form Component
 *
 * A React component for users to request stock tracking with proper validation
 * and user feedback. Uses React Hook Form with Zod validation and shadcn/ui components.
 *
 * SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>
 * SPDX-License-Identifier: MIT
 */

import * as React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { trackStock, type ApiError } from '@/lib/api/stockTracking';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, CheckCircle, AlertCircle } from 'lucide-react';

// Form validation schema
const stockRequestSchema = z.object({
  symbol: z
    .string()
    .min(1, 'Stock symbol is required')
    .refine((value) => value.length >= 2, 'Stock symbol must be at least 2 characters')
    .refine((value) => value.length <= 10, 'Stock symbol must be 10 characters or less')
    .refine(
      (value) => /^[A-Za-z][A-Za-z0-9]*$/.test(value),
      'Stock symbol must be 2-10 characters, start with a letter'
    )
    .transform((value) => value.trim().toUpperCase()),
});

type StockRequestFormData = z.infer<typeof stockRequestSchema>;

interface StockRequestFormProps {
  onSuccess?: (symbol: string) => void;
  onError?: (error: string) => void;
  className?: string;
}

export function StockRequestForm({ onSuccess, onError, className }: StockRequestFormProps) {
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [successMessage, setSuccessMessage] = React.useState<string | null>(null);
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);

  const form = useForm<StockRequestFormData>({
    resolver: zodResolver(stockRequestSchema),
    defaultValues: {
      symbol: '',
    },
    mode: 'onBlur', // Show errors when user leaves field or submits
  });

  const onSubmit = async (data: StockRequestFormData) => {
    setIsSubmitting(true);
    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      const response = await trackStock(data.symbol);

      setSuccessMessage(`Successfully requested tracking for ${data.symbol}. ${response.message}`);
      form.reset();

      // Call success callback if provided
      if (onSuccess) {
        onSuccess(data.symbol);
      }
    } catch (error) {
      const apiError = error as ApiError;
      const errorMsg = apiError.detail || 'Failed to request stock tracking. Please try again.';

      setErrorMessage(errorMsg);

      // Call error callback if provided
      if (onError) {
        onError(errorMsg);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.toUpperCase();
    form.setValue('symbol', value);

    // Clear error message when user starts typing
    if (errorMessage) {
      setErrorMessage(null);
    }
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>Request Stock Tracking</CardTitle>
        <CardDescription>
          Enter a stock symbol to request tracking. The symbol will be automatically validated and
          processed.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="symbol"
              render={({ field }) => (
                <FormItem>
                  <FormLabel htmlFor="stock-symbol">Stock Symbol</FormLabel>
                  <FormControl>
                    <Input
                      id="stock-symbol"
                      placeholder="e.g., AAPL, TSLA, GOOGL"
                      autoComplete="off"
                      autoCapitalize="characters"
                      maxLength={10}
                      disabled={isSubmitting}
                      {...field}
                      onChange={handleInputChange}
                      value={field.value}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Success Message */}
            {successMessage && (
              <Alert className="border-green-200 bg-green-50">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <AlertDescription className="text-green-800">{successMessage}</AlertDescription>
              </Alert>
            )}

            {/* Error Message */}
            {errorMessage && (
              <Alert className="border-red-200 bg-red-50">
                <AlertCircle className="h-4 w-4 text-red-600" />
                <AlertDescription className="text-red-800">{errorMessage}</AlertDescription>
              </Alert>
            )}

            <Button type="submit" disabled={isSubmitting} className="w-full">
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Requesting...
                </>
              ) : (
                'Request Tracking'
              )}
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}
