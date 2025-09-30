import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiRequest, API_ENDPOINTS, buildUrl } from '@/lib/api';
import type { TipData } from '@/lib/types';

/**
 * React Query Hook for fetching today's tip
 *
 * Usage:
 * ```tsx
 * const { data: tip, isLoading, error } = useTodayTip();
 * ```
 */
export function useTodayTip() {
  return useQuery({
    queryKey: ['tips', 'today'],
    queryFn: () => apiRequest<TipData>({ url: API_ENDPOINTS.TIPS.TODAY }),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * React Query Hook for fetching recent tips
 *
 * Usage:
 * ```tsx
 * const { data: tips, isLoading, error } = useRecentTips(5);
 * ```
 */
export function useRecentTips(limit: number = 10) {
  return useQuery({
    queryKey: ['tips', 'recent', limit],
    queryFn: () =>
      apiRequest<TipData[]>({
        url: buildUrl(API_ENDPOINTS.TIPS.RECENT, { limit }),
      }),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * React Query Hook for fetching a specific tip by ID
 *
 * Usage:
 * ```tsx
 * const { data: tip, isLoading, error } = useTip(tipId);
 * ```
 */
export function useTip(id: string | null) {
  return useQuery({
    queryKey: ['tips', id],
    queryFn: () => apiRequest<TipData>({ url: API_ENDPOINTS.TIPS.BY_ID(id!) }),
    enabled: !!id, // Only run query if id is provided
    staleTime: 1000 * 60 * 10, // 10 minutes
  });
}

/**
 * React Query Hook for fetching tips list with pagination
 *
 * Usage:
 * ```tsx
 * const { data, isLoading, error } = useTipsList({ page: 1, limit: 20 });
 * ```
 */
export function useTipsList(params?: { page?: number; limit?: number }) {
  return useQuery({
    queryKey: ['tips', 'list', params],
    queryFn: () =>
      apiRequest<{ tips: TipData[]; total: number }>({
        url: buildUrl(API_ENDPOINTS.TIPS.LIST, params),
      }),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * React Query Hook for searching tips
 *
 * Usage:
 * ```tsx
 * const { data, isLoading, error } = useSearchTips('grep', { difficulty: 'Beginner' });
 * ```
 */
export function useSearchTips(query: string, filters?: Record<string, any>) {
  return useQuery({
    queryKey: ['tips', 'search', query, filters],
    queryFn: () =>
      apiRequest<TipData[]>({
        url: buildUrl(API_ENDPOINTS.TIPS.SEARCH, { q: query, ...filters }),
      }),
    enabled: query.length > 0, // Only search if query is not empty
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
}

/**
 * Example mutation hook for future use
 * (Currently placeholder - will be implemented with backend)
 *
 * Usage:
 * ```tsx
 * const { mutate: likeTip, isPending } = useLikeTip();
 * likeTip(tipId, {
 *   onSuccess: () => toast.success('Tip liked!'),
 *   onError: (error) => toast.error(error.message),
 * });
 * ```
 */
export function useLikeTip() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (tipId: string) => {
      // Placeholder - implement when backend ready
      return apiRequest({ url: `/api/tips/${tipId}/like`, method: 'POST' });
    },
    onSuccess: () => {
      // Invalidate and refetch relevant queries
      queryClient.invalidateQueries({ queryKey: ['tips'] });
    },
  });
}
