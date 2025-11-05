'use client';

import { AlertCircle, AlertTriangle, Info, XCircle } from 'lucide-react';

export type ErrorType = 'error' | 'warning' | 'info' | 'critical';

interface ErrorMessageProps {
  type?: ErrorType;
  title?: string;
  message: string;
  onRetry?: () => void;
  onDismiss?: () => void;
  className?: string;
}

const typeConfig = {
  error: {
    icon: AlertCircle,
    bgColor: 'bg-red-50 dark:bg-red-900/20',
    borderColor: 'border-red-200 dark:border-red-800',
    iconColor: 'text-red-600 dark:text-red-400',
    titleColor: 'text-red-900 dark:text-red-200',
    messageColor: 'text-red-700 dark:text-red-300',
  },
  warning: {
    icon: AlertTriangle,
    bgColor: 'bg-yellow-50 dark:bg-yellow-900/20',
    borderColor: 'border-yellow-200 dark:border-yellow-800',
    iconColor: 'text-yellow-600 dark:text-yellow-400',
    titleColor: 'text-yellow-900 dark:text-yellow-200',
    messageColor: 'text-yellow-700 dark:text-yellow-300',
  },
  info: {
    icon: Info,
    bgColor: 'bg-blue-50 dark:bg-blue-900/20',
    borderColor: 'border-blue-200 dark:border-blue-800',
    iconColor: 'text-blue-600 dark:text-blue-400',
    titleColor: 'text-blue-900 dark:text-blue-200',
    messageColor: 'text-blue-700 dark:text-blue-300',
  },
  critical: {
    icon: XCircle,
    bgColor: 'bg-red-100 dark:bg-red-900/30',
    borderColor: 'border-red-300 dark:border-red-700',
    iconColor: 'text-red-700 dark:text-red-300',
    titleColor: 'text-red-900 dark:text-red-100',
    messageColor: 'text-red-800 dark:text-red-200',
  },
};

/**
 * Error Message Component
 *
 * A versatile error display component with different severity levels.
 *
 * Features:
 * - Multiple error types (error, warning, info, critical)
 * - Optional retry and dismiss actions
 * - Accessible with proper ARIA attributes
 * - Dark mode support
 *
 * Usage:
 * ```tsx
 * <ErrorMessage
 *   type="error"
 *   title="Failed to load data"
 *   message="Could not fetch the requested data. Please try again."
 *   onRetry={() => refetch()}
 * />
 * ```
 */
export function ErrorMessage({
  type = 'error',
  title,
  message,
  onRetry,
  onDismiss,
  className = '',
}: ErrorMessageProps) {
  const config = typeConfig[type];
  const Icon = config.icon;

  return (
    <div
      className={`rounded-lg border p-4 ${config.bgColor} ${config.borderColor} ${className}`}
      role="alert"
      aria-live="assertive"
    >
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0">
          <Icon className={`w-5 h-5 ${config.iconColor}`} aria-hidden="true" />
        </div>

        <div className="flex-1">
          {title && (
            <h3 className={`text-sm font-semibold mb-1 ${config.titleColor}`}>
              {title}
            </h3>
          )}
          <p className={`text-sm ${config.messageColor}`}>
            {message}
          </p>

          {(onRetry || onDismiss) && (
            <div className="mt-3 flex gap-2">
              {onRetry && (
                <button
                  onClick={onRetry}
                  className={`text-sm font-medium ${config.iconColor} hover:underline focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-current rounded px-2 py-1`}
                >
                  Try Again
                </button>
              )}
              {onDismiss && (
                <button
                  onClick={onDismiss}
                  className={`text-sm font-medium ${config.messageColor} hover:underline focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-current rounded px-2 py-1`}
                >
                  Dismiss
                </button>
              )}
            </div>
          )}
        </div>

        {onDismiss && (
          <button
            onClick={onDismiss}
            className={`flex-shrink-0 ${config.iconColor} hover:opacity-70 transition-opacity focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-current rounded`}
            aria-label="Dismiss"
          >
            <XCircle className="w-5 h-5" />
          </button>
        )}
      </div>
    </div>
  );
}

/**
 * Inline Error Message
 *
 * A compact error message for forms and inline validation.
 *
 * Usage:
 * ```tsx
 * <InlineError message="This field is required" />
 * ```
 */
export function InlineError({ message, className = '' }: { message: string; className?: string }) {
  return (
    <p className={`text-sm text-red-600 dark:text-red-400 flex items-center gap-1 ${className}`} role="alert">
      <AlertCircle className="w-4 h-4" aria-hidden="true" />
      {message}
    </p>
  );
}
