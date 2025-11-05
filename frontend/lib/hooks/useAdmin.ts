import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiRequest, API_ENDPOINTS } from '@/lib/api';
import type { TipData, DraftWeek, DifficultyLevel, TipCategory } from '@/lib/types';
import type { Activity } from '@/lib/types/common';

/**
 * Admin Statistics Interface
 */
export interface AdminStats {
  totalTips: number;
  pendingApproval: number;
  activeUsers: number;
  completionRate: number;
}

/**
 * Pending Tip Interface (for admin dashboard)
 */
export interface PendingTip {
  id: number;
  title: string;
  category: TipCategory;
  difficulty: DifficultyLevel;
  createdAt: string;
  author: string;
}

/**
 * React Query Hook for fetching admin dashboard statistics
 *
 * Usage:
 * ```tsx
 * const { data: stats, isLoading, error } = useAdminStats();
 * ```
 */
export function useAdminStats() {
  return useQuery({
    queryKey: ['admin', 'stats'],
    queryFn: () => apiRequest<AdminStats>({ url: API_ENDPOINTS.ADMIN.STATS }),
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
}

/**
 * React Query Hook for fetching pending tips (drafts awaiting approval)
 *
 * Usage:
 * ```tsx
 * const { data: pendingTips, isLoading, error } = usePendingTips();
 * ```
 */
export function usePendingTips() {
  return useQuery({
    queryKey: ['admin', 'pending-tips'],
    queryFn: () => apiRequest<PendingTip[]>({ url: API_ENDPOINTS.ADMIN.PENDING_TIPS }),
    staleTime: 1000 * 60, // 1 minute
  });
}

/**
 * React Query Hook for fetching recent activity in admin dashboard
 *
 * Usage:
 * ```tsx
 * const { data: activities, isLoading, error } = useRecentActivity();
 * ```
 */
export function useRecentActivity() {
  return useQuery({
    queryKey: ['admin', 'activity'],
    queryFn: () => apiRequest<Activity[]>({ url: API_ENDPOINTS.ADMIN.RECENT_ACTIVITY }),
    staleTime: 1000 * 30, // 30 seconds
  });
}

/**
 * React Query Mutation Hook for approving a tip
 *
 * Usage:
 * ```tsx
 * const { mutate: approveTip, isPending } = useApproveTip();
 * approveTip(tipId, {
 *   onSuccess: () => toast.success('Tip approved!'),
 *   onError: (error) => toast.error(error.message),
 * });
 * ```
 */
export function useApproveTip() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (tipId: string) => {
      return apiRequest({
        url: API_ENDPOINTS.ADMIN.APPROVE_TIP(tipId),
        method: 'POST',
      });
    },
    onSuccess: () => {
      // Invalidate and refetch relevant queries
      queryClient.invalidateQueries({ queryKey: ['admin', 'pending-tips'] });
      queryClient.invalidateQueries({ queryKey: ['admin', 'stats'] });
      queryClient.invalidateQueries({ queryKey: ['admin', 'activity'] });
      queryClient.invalidateQueries({ queryKey: ['tips'] });
    },
  });
}

/**
 * React Query Mutation Hook for rejecting a tip
 *
 * Usage:
 * ```tsx
 * const { mutate: rejectTip, isPending } = useRejectTip();
 * rejectTip({ tipId, reason }, {
 *   onSuccess: () => toast.success('Tip rejected'),
 *   onError: (error) => toast.error(error.message),
 * });
 * ```
 */
export function useRejectTip() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ tipId, reason }: { tipId: string; reason?: string }) => {
      return apiRequest({
        url: API_ENDPOINTS.ADMIN.REJECT_TIP(tipId),
        method: 'POST',
        data: { reason },
      });
    },
    onSuccess: () => {
      // Invalidate and refetch relevant queries
      queryClient.invalidateQueries({ queryKey: ['admin', 'pending-tips'] });
      queryClient.invalidateQueries({ queryKey: ['admin', 'stats'] });
      queryClient.invalidateQueries({ queryKey: ['admin', 'activity'] });
    },
  });
}
