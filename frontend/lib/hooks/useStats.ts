import { useQuery } from '@tanstack/react-query';
import { apiRequest, API_ENDPOINTS } from '@/lib/api';
import type { StatsData } from '@/lib/types';

/**
 * React Query Hook for fetching statistics overview
 *
 * Usage:
 * ```tsx
 * const { data: stats, isLoading, error } = useStats();
 * ```
 */
export function useStats() {
  return useQuery({
    queryKey: ['stats', 'overview'],
    queryFn: () => apiRequest<StatsData>({ url: API_ENDPOINTS.STATS.OVERVIEW }),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * React Query Hook for fetching tips by category statistics
 *
 * Usage:
 * ```tsx
 * const { data: categoryStats, isLoading, error } = useTipsByCategory();
 * ```
 */
export function useTipsByCategory() {
  return useQuery({
    queryKey: ['stats', 'tips-by-category'],
    queryFn: () => apiRequest({ url: API_ENDPOINTS.STATS.TIPS_BY_CATEGORY }),
    staleTime: 1000 * 60 * 10, // 10 minutes
  });
}

/**
 * React Query Hook for fetching tips by difficulty statistics
 *
 * Usage:
 * ```tsx
 * const { data: difficultyStats, isLoading, error } = useTipsByDifficulty();
 * ```
 */
export function useTipsByDifficulty() {
  return useQuery({
    queryKey: ['stats', 'tips-by-difficulty'],
    queryFn: () => apiRequest({ url: API_ENDPOINTS.STATS.TIPS_BY_DIFFICULTY }),
    staleTime: 1000 * 60 * 10, // 10 minutes
  });
}
