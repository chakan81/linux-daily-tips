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
 * const { data, isLoading, error } = useRecentTips(5);
 * const tips = data?.items || [];
 * ```
 */
export function useRecentTips(limit: number = 10) {
  return useQuery({
    queryKey: ['tips', 'recent', limit],
    queryFn: () =>
      apiRequest<{ items: TipData[]; total: number; page: number; page_size: number }>({
        url: buildUrl(API_ENDPOINTS.TIPS.RECENT, { page: 1, page_size: limit }),
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
 * React Query Hook for fetching tips list with pagination and filters
 *
 * Usage:
 * ```tsx
 * const { data, isLoading, error } = useTipsList({
 *   page: 1,
 *   page_size: 12,
 *   difficulty: 'beginner',
 *   category: 'file-system',
 *   sort_by: 'publish_date',
 *   order: 'desc',
 * });
 * const tips = data?.items || [];
 * const total = data?.total || 0;
 * ```
 */
export function useTipsList(params?: {
  page?: number;
  page_size?: number;
  difficulty?: string;
  category?: string;
  sort_by?: string;
  order?: 'asc' | 'desc';
}) {
  // Convert page to skip for backend API (page 1 = skip 0)
  const skip = params?.page ? (params.page - 1) * (params.page_size || 10) : 0;
  const limit = params?.page_size || 10;

  const apiParams = {
    skip,
    limit,
    difficulty: params?.difficulty,
    category: params?.category,
    sort_by: params?.sort_by,
    order: params?.order,
  };

  return useQuery({
    queryKey: ['tips', 'list', params],
    queryFn: () =>
      apiRequest<{ items: TipData[]; total: number; page: number; page_size: number }>({
        url: buildUrl(API_ENDPOINTS.TIPS.LIST, apiParams),
      }),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * React Query Hook for searching tips with filters
 *
 * Uses the search endpoint with pagination and filter support
 *
 * Usage:
 * ```tsx
 * const { data, isLoading, error } = useSearchTips({
 *   q: 'grep',
 *   page: 1,
 *   page_size: 12,
 *   difficulty: 'beginner',
 * });
 * const tips = data?.items || [];
 * ```
 */
export function useSearchTips(params: {
  q: string;
  page?: number;
  page_size?: number;
  difficulty?: string;
  category?: string;
}) {
  // Convert page to skip for backend API
  const skip = params?.page ? (params.page - 1) * (params.page_size || 10) : 0;
  const limit = params.page_size || 10;

  const apiParams = {
    q: params.q,
    skip,
    limit,
    difficulty: params.difficulty,
    category: params.category,
  };

  return useQuery({
    queryKey: ['tips', 'search', params],
    queryFn: () =>
      apiRequest<{ items: TipData[]; total: number; page: number; page_size: number }>({
        url: buildUrl(API_ENDPOINTS.TIPS.SEARCH, apiParams),
      }),
    enabled: params.q.length > 0, // Only search if query is not empty
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

/**
 * React Query Hook for fetching available categories
 *
 * Fetches dynamic list of categories from the database.
 *
 * Usage:
 * ```tsx
 * const { data: categories, isLoading } = useCategories();
 * const categoryList = categories || [];
 * ```
 */
export function useCategories() {
  return useQuery({
    queryKey: ['tips', 'categories'],
    queryFn: () => apiRequest<{ categories: string[] }>({ url: API_ENDPOINTS.TIPS.CATEGORIES }),
    staleTime: 1000 * 60 * 30, // 30 minutes (카테고리는 자주 변경되지 않음)
  });
}
