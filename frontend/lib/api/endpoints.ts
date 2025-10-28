/**
 * API Endpoints
 *
 * Centralized API endpoint definitions for type safety and maintainability.
 */

import { QueryParams } from '@/lib/types/common'

export const API_ENDPOINTS = {
  // Tips endpoints
  TIPS: {
    LIST: '/api/tips',
    TODAY: '/api/tips/today',
    BY_ID: (id: string) => `/api/tips/${id}`,
    RECENT: '/api/tips/recent',
    BY_CATEGORY: (category: string) => `/api/tips/category/${category}`,
    BY_DIFFICULTY: (difficulty: string) => `/api/tips/difficulty/${difficulty}`,
    SEARCH: '/api/tips/search',
  },

  // Draft endpoints
  DRAFTS: {
    LIST: '/api/drafts',
    BY_ID: (id: string) => `/api/drafts/${id}`,
    APPROVE: (id: string) => `/api/drafts/${id}/approve`,
    REJECT: (id: string) => `/api/drafts/${id}/reject`,
    GENERATE: '/api/drafts/generate',
  },

  // Stats endpoints
  STATS: {
    OVERVIEW: '/api/stats/overview',
    TIPS_BY_CATEGORY: '/api/stats/tips-by-category',
    TIPS_BY_DIFFICULTY: '/api/stats/tips-by-difficulty',
  },

  // Auth endpoints
  AUTH: {
    LOGIN: '/api/auth/login',
    LOGOUT: '/api/auth/logout',
    REFRESH: '/api/auth/refresh',
    ME: '/api/auth/me',
  },

  // Admin endpoints
  ADMIN: {
    STATS: '/api/admin/stats',
    PENDING_TIPS: '/api/admin/tips/pending',
    RECENT_ACTIVITY: '/api/admin/activity/recent',
    APPROVE_TIP: (id: string) => `/api/admin/tips/${id}/approve`,
    REJECT_TIP: (id: string) => `/api/admin/tips/${id}/reject`,
  },

  // Terminal endpoints
  TERMINAL: {
    CREATE_SESSION: '/api/v1/terminal/session',
    DESTROY: (sessionId: string) => `/api/v1/terminal/session/${sessionId}`,
    WS: (sessionId: string) => `/api/v1/terminal/ws/${sessionId}`,
  },
} as const;

/**
 * Helper function to build URLs with query parameters
 */
export function buildUrl(endpoint: string, params?: QueryParams): string {
  if (!params) return endpoint;

  const queryString = Object.entries(params)
    .filter(([_, value]) => value !== undefined && value !== null)
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`)
    .join('&');

  return queryString ? `${endpoint}?${queryString}` : endpoint;
}
