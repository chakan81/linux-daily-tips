'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useState, useEffect } from 'react';

/**
 * Query Client Configuration
 *
 * Global configuration for React Query behavior.
 */
const queryClientConfig = {
  defaultOptions: {
    queries: {
      // Time before cached data is considered stale
      staleTime: 1000 * 60 * 5, // 5 minutes

      // Time before inactive queries are removed from cache
      gcTime: 1000 * 60 * 10, // 10 minutes (formerly cacheTime)

      // Retry failed queries
      retry: 1,

      // Retry delay
      retryDelay: (attemptIndex: number) => Math.min(1000 * 2 ** attemptIndex, 30000),

      // Refetch on window focus (useful for keeping data fresh)
      refetchOnWindowFocus: process.env.NODE_ENV === 'production',

      // Refetch on reconnect
      refetchOnReconnect: true,

      // Refetch on mount
      refetchOnMount: true,
    },
    mutations: {
      // Retry failed mutations
      retry: 1,

      // Retry delay
      retryDelay: (attemptIndex: number) => Math.min(1000 * 2 ** attemptIndex, 30000),
    },
  },
};

/**
 * Query Provider Component
 *
 * Provides React Query context to the application.
 * Must wrap all components that use React Query hooks.
 *
 * Features:
 * - Centralized query client configuration
 * - DevTools in development environment
 * - Per-request query client to prevent sharing between users
 *
 * Usage:
 * ```tsx
 * <QueryProvider>
 *   <App />
 * </QueryProvider>
 * ```
 */
export function QueryProvider({ children }: { children: React.ReactNode }) {
  // Create a new query client for each request to prevent sharing between users
  const [queryClient] = useState(() => new QueryClient(queryClientConfig));

  // Initialize MSW in development environment
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      import('@/lib/mocks/browser').then(({ worker }) => {
        worker.start({
          onUnhandledRequest: 'bypass', // 처리되지 않은 요청은 실제 서버로 전달
        }).then(() => {
          console.log('🔶 MSW: Mock API enabled for development');
        }).catch((error) => {
          console.error('❌ MSW: Failed to start service worker', error);
        });
      }).catch((error) => {
        console.error('❌ MSW: Failed to import browser module', error);
      });
    }
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {/* DevTools only in development */}
      {process.env.NODE_ENV === 'development' && (
        <ReactQueryDevtools
          initialIsOpen={false}
          buttonPosition="bottom-right"
          position="bottom"
        />
      )}
    </QueryClientProvider>
  );
}
