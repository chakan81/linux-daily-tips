'use client';

import { Loader2 } from 'lucide-react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  text?: string;
}

const sizeClasses = {
  sm: 'w-4 h-4',
  md: 'w-8 h-8',
  lg: 'w-12 h-12',
  xl: 'w-16 h-16',
};

/**
 * Loading Spinner Component
 *
 * A reusable loading indicator with customizable size and optional text.
 *
 * Usage:
 * ```tsx
 * <LoadingSpinner size="md" text="Loading..." />
 * ```
 */
export function LoadingSpinner({ size = 'md', className = '', text }: LoadingSpinnerProps) {
  return (
    <div className={`flex flex-col items-center justify-center ${className}`} role="status">
      <Loader2
        className={`${sizeClasses[size]} animate-spin text-blue-600 dark:text-blue-400`}
        aria-hidden="true"
      />
      {text && (
        <p className="mt-2 text-sm text-gray-600 dark:text-gray-400" aria-live="polite">
          {text}
        </p>
      )}
      <span className="sr-only">Loading...</span>
    </div>
  );
}

/**
 * Full Page Loading Spinner
 *
 * A loading spinner that covers the entire viewport.
 * Useful for page-level loading states.
 *
 * Usage:
 * ```tsx
 * <FullPageLoader text="Loading content..." />
 * ```
 */
export function FullPageLoader({ text = 'Loading...' }: { text?: string }) {
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm z-50">
      <LoadingSpinner size="xl" text={text} />
    </div>
  );
}

/**
 * Inline Loading Spinner
 *
 * A small inline spinner for button loading states.
 *
 * Usage:
 * ```tsx
 * <button disabled>
 *   <InlineLoader /> Loading...
 * </button>
 * ```
 */
export function InlineLoader({ className = '' }: { className?: string }) {
  return (
    <Loader2
      className={`inline-block w-4 h-4 animate-spin ${className}`}
      aria-hidden="true"
    />
  );
}
