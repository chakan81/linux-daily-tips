'use client';

import { FileQuestion, WifiOff, RefreshCw } from 'lucide-react';
import Link from 'next/link';

/**
 * TipErrorState Props
 */
interface TipErrorStateProps {
  error: Error;
  onRetry?: () => void;
}

/**
 * TipErrorState Component
 * Displays error state with appropriate icon and action
 */
export function TipErrorState({ error, onRetry }: TipErrorStateProps) {
  // Determine error type
  const is404 = error.message.includes('404') || error.message.includes('not found');
  const isNetworkError = error.message.includes('network') || error.message.includes('fetch');

  if (is404) {
    return (
      <div
        className="flex flex-col items-center justify-center min-h-[50vh] px-4 text-center"
        role="status"
        aria-live="polite"
      >
        <FileQuestion
          className="w-20 h-20 text-gray-500 mb-6"
          aria-hidden="true"
        />
        <h2 className="text-3xl font-bold text-foreground mb-4">
          Tip Not Found
        </h2>
        <p className="text-lg text-muted-foreground mb-8 max-w-md">
          The tip you&apos;re looking for doesn&apos;t exist or has been removed.
        </p>
        <Link
          href="/tips"
          className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-500 to-purple-500 text-white px-6 py-3 rounded-xl font-semibold hover:shadow-lg hover:shadow-blue-500/50 transition-all duration-200"
          aria-label="Browse all tips"
        >
          Browse All Tips
        </Link>
      </div>
    );
  }

  if (isNetworkError) {
    return (
      <div
        className="flex flex-col items-center justify-center min-h-[50vh] px-4 text-center"
        role="status"
        aria-live="polite"
      >
        <WifiOff
          className="w-20 h-20 text-gray-500 mb-6"
          aria-hidden="true"
        />
        <h2 className="text-3xl font-bold text-foreground mb-4">
          Connection Error
        </h2>
        <p className="text-lg text-muted-foreground mb-8 max-w-md">
          Unable to connect to the server. Please check your internet connection and try again.
        </p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-500 to-purple-500 text-white px-6 py-3 rounded-xl font-semibold hover:shadow-lg hover:shadow-blue-500/50 transition-all duration-200"
            aria-label="Try again"
            type="button"
          >
            <RefreshCw className="w-5 h-5" aria-hidden="true" />
            Try Again
          </button>
        )}
      </div>
    );
  }

  // Generic error
  return (
    <div
      className="flex flex-col items-center justify-center min-h-[50vh] px-4 text-center"
      role="status"
      aria-live="polite"
    >
      <div
        className="w-20 h-20 rounded-full bg-red-900/20 flex items-center justify-center mb-6"
        aria-hidden="true"
      >
        <span className="text-4xl">⚠️</span>
      </div>
      <h2 className="text-3xl font-bold text-foreground mb-4">
        Something Went Wrong
      </h2>
      <p className="text-lg text-muted-foreground mb-2 max-w-md">
        An unexpected error occurred while loading this tip.
      </p>
      <p className="text-sm text-gray-500 mb-8 font-mono">
        {error.message}
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-500 to-purple-500 text-white px-6 py-3 rounded-xl font-semibold hover:shadow-lg hover:shadow-blue-500/50 transition-all duration-200"
          aria-label="Try again"
          type="button"
        >
          <RefreshCw className="w-5 h-5" aria-hidden="true" />
          Try Again
        </button>
      )}
    </div>
  );
}
