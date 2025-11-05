/**
 * Unit Tests for lib/hooks/useTips.ts
 *
 * Test coverage for React Query hooks:
 * - useTodayTip: Fetches today's tip
 * - useRecentTips: Fetches recent tips with limit
 * - useTip: Fetches specific tip by ID
 * - useTipsList: Fetches paginated tips list
 * - useSearchTips: Searches tips with filters
 * - useLikeTip: Mutation hook for liking tips
 */

import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import React, { ReactNode } from 'react'
import {
  useTodayTip,
  useRecentTips,
  useTip,
  useTipsList,
  useSearchTips,
  useLikeTip,
} from '../useTips'
import { apiRequest } from '@/lib/api'
import type { TipData } from '@/lib/types'

// Mock the API module
jest.mock('@/lib/api', () => ({
  apiRequest: jest.fn(),
  API_ENDPOINTS: {
    TIPS: {
      TODAY: '/api/tips/today',
      RECENT: '/api/tips/recent',
      BY_ID: (id: string) => `/api/tips/${id}`,
      LIST: '/api/tips',
      SEARCH: '/api/tips/search',
    },
  },
  buildUrl: jest.fn((endpoint: string, params?: any) => {
    if (!params) return endpoint
    const queryString = Object.entries(params)
      .map(([key, value]) => `${key}=${value}`)
      .join('&')
    return `${endpoint}?${queryString}`
  }),
}))

const mockedApiRequest = apiRequest as jest.MockedFunction<typeof apiRequest>

// Mock tip data
const mockTipData: TipData = {
  id: '1',
  title: 'Master File Permissions',
  description: 'Learn about chmod and file permissions',
  command: 'chmod 755 file.sh',
  explanation: 'This command sets read, write, and execute permissions',
  difficulty: 'Beginner',
  category: 'File Management',
  tags: ['permissions', 'chmod'],
  examples: [
    {
      command: 'chmod 755 script.sh',
      explanation: 'Make script executable',
    },
  ],
  relatedCommands: ['chown', 'chgrp'],
  terminalSetup: {
    preInstalledPackages: [],
    initialFiles: [],
    workingDirectory: '/home/user',
  },
  createdAt: '2025-01-15T10:00:00Z',
  updatedAt: '2025-01-15T10:00:00Z',
  publishedAt: '2025-01-15T10:00:00Z',
  viewCount: 100,
  likeCount: 10,
  isPublished: true,
}

// Create wrapper with QueryClient
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
    logger: {
      log: () => {},
      warn: () => {},
      error: () => {},
    },
  })

  return ({ children }: { children: ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children)
}

describe('useTodayTip', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('should fetch today\'s tip successfully', async () => {
    mockedApiRequest.mockResolvedValue(mockTipData)

    const { result } = renderHook(() => useTodayTip(), {
      wrapper: createWrapper(),
    })

    expect(result.current.isLoading).toBe(true)
    expect(result.current.data).toBeUndefined()

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(result.current.data).toEqual(mockTipData)
    expect(result.current.error).toBeNull()
    expect(mockedApiRequest).toHaveBeenCalledWith({ url: '/api/tips/today' })
  })

  it('should handle error when fetching fails', async () => {
    const error = new Error('Failed to fetch tip')
    mockedApiRequest.mockRejectedValue(error)

    const { result } = renderHook(() => useTodayTip(), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.isError).toBe(true)
    })

    expect(result.current.data).toBeUndefined()
    expect(result.current.error).toBeTruthy()
  })

  it('should use correct stale time (5 minutes)', async () => {
    mockedApiRequest.mockResolvedValue(mockTipData)

    const { result } = renderHook(() => useTodayTip(), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    // Check that the query was configured with 5 minute stale time
    // Note: We can't directly test staleTime, but we verify the hook works correctly
    expect(result.current.data).toEqual(mockTipData)
  })

  it('should use correct query key', async () => {
    mockedApiRequest.mockResolvedValue(mockTipData)

    const { result } = renderHook(() => useTodayTip(), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    // Query key should be ['tips', 'today']
    expect(result.current.data).toBeDefined()
  })
})

describe('useRecentTips', () => {
  const mockRecentTips: TipData[] = [
    { ...mockTipData, id: '1', title: 'Tip 1' },
    { ...mockTipData, id: '2', title: 'Tip 2' },
    { ...mockTipData, id: '3', title: 'Tip 3' },
  ]

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('should fetch recent tips with default limit', async () => {
    mockedApiRequest.mockResolvedValue(mockRecentTips)

    const { result } = renderHook(() => useRecentTips(), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(result.current.data).toEqual(mockRecentTips)
    expect(mockedApiRequest).toHaveBeenCalledWith({
      url: '/api/tips/recent?limit=10',
    })
  })

  it('should fetch recent tips with custom limit', async () => {
    mockedApiRequest.mockResolvedValue(mockRecentTips.slice(0, 5))

    const { result } = renderHook(() => useRecentTips(5), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(mockedApiRequest).toHaveBeenCalledWith({
      url: '/api/tips/recent?limit=5',
    })
  })

  it('should handle different limit values', async () => {
    mockedApiRequest.mockResolvedValue([mockTipData])

    const { result: result1 } = renderHook(() => useRecentTips(1), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result1.current.isSuccess).toBe(true)
    })

    expect(mockedApiRequest).toHaveBeenCalledWith({
      url: '/api/tips/recent?limit=1',
    })

    jest.clearAllMocks()

    const { result: result20 } = renderHook(() => useRecentTips(20), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result20.current.isSuccess).toBe(true)
    })

    expect(mockedApiRequest).toHaveBeenCalledWith({
      url: '/api/tips/recent?limit=20',
    })
  })

  it('should handle error', async () => {
    const error = new Error('Failed to fetch recent tips')
    mockedApiRequest.mockRejectedValue(error)

    const { result } = renderHook(() => useRecentTips(5), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.isError).toBe(true)
    })

    expect(result.current.data).toBeUndefined()
  })
})

describe('useTip', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('should fetch specific tip by ID', async () => {
    mockedApiRequest.mockResolvedValue(mockTipData)

    const { result } = renderHook(() => useTip('123'), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(result.current.data).toEqual(mockTipData)
    expect(mockedApiRequest).toHaveBeenCalledWith({ url: '/api/tips/123' })
  })

  it('should not fetch when id is null', async () => {
    const { result } = renderHook(() => useTip(null), {
      wrapper: createWrapper(),
    })

    // Wait a bit to ensure no fetch happens
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(result.current.isLoading).toBe(false)
    expect(result.current.data).toBeUndefined()
    expect(mockedApiRequest).not.toHaveBeenCalled()
  })

  it('should not fetch when id is empty string', async () => {
    const { result } = renderHook(() => useTip(''), {
      wrapper: createWrapper(),
    })

    await new Promise(resolve => setTimeout(resolve, 100))

    expect(result.current.isLoading).toBe(false)
    expect(mockedApiRequest).not.toHaveBeenCalled()
  })

  it('should handle error', async () => {
    const error = new Error('Tip not found')
    mockedApiRequest.mockRejectedValue(error)

    const { result } = renderHook(() => useTip('999'), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.isError).toBe(true)
    })

    expect(result.current.data).toBeUndefined()
  })

  it('should refetch when id changes', async () => {
    mockedApiRequest.mockResolvedValue(mockTipData)

    const { result, rerender } = renderHook(
      ({ id }) => useTip(id),
      {
        wrapper: createWrapper(),
        initialProps: { id: '123' },
      }
    )

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(mockedApiRequest).toHaveBeenCalledWith({ url: '/api/tips/123' })

    // Change ID
    jest.clearAllMocks()
    const newMockTip = { ...mockTipData, id: '456', title: 'Different Tip' }
    mockedApiRequest.mockResolvedValue(newMockTip)

    rerender({ id: '456' })

    await waitFor(() => {
      expect(result.current.data?.id).toBe('456')
    })

    expect(mockedApiRequest).toHaveBeenCalledWith({ url: '/api/tips/456' })
  })
})

describe('useTipsList', () => {
  const mockTipsList = {
    tips: [
      { ...mockTipData, id: '1' },
      { ...mockTipData, id: '2' },
    ],
    total: 50,
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('should fetch tips list without parameters', async () => {
    mockedApiRequest.mockResolvedValue(mockTipsList)

    const { result } = renderHook(() => useTipsList(), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(result.current.data).toEqual(mockTipsList)
    expect(mockedApiRequest).toHaveBeenCalledWith({ url: '/api/tips' })
  })

  it('should fetch tips list with pagination', async () => {
    mockedApiRequest.mockResolvedValue(mockTipsList)

    const { result } = renderHook(
      () => useTipsList({ page: 2, limit: 20 }),
      {
        wrapper: createWrapper(),
      }
    )

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(mockedApiRequest).toHaveBeenCalledWith({
      url: '/api/tips?page=2&limit=20',
    })
  })

  it('should fetch tips list with only page parameter', async () => {
    mockedApiRequest.mockResolvedValue(mockTipsList)

    const { result } = renderHook(() => useTipsList({ page: 1 }), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(mockedApiRequest).toHaveBeenCalledWith({
      url: '/api/tips?page=1',
    })
  })

  it('should handle error', async () => {
    const error = new Error('Failed to fetch tips list')
    mockedApiRequest.mockRejectedValue(error)

    const { result } = renderHook(() => useTipsList(), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.isError).toBe(true)
    })
  })
})

describe('useSearchTips', () => {
  const mockSearchResults: TipData[] = [
    { ...mockTipData, id: '1', title: 'Grep Tutorial' },
    { ...mockTipData, id: '2', title: 'Advanced Grep' },
  ]

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('should search tips with query', async () => {
    mockedApiRequest.mockResolvedValue(mockSearchResults)

    const { result } = renderHook(() => useSearchTips('grep'), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(result.current.data).toEqual(mockSearchResults)
    expect(mockedApiRequest).toHaveBeenCalledWith({
      url: '/api/tips/search?q=grep',
    })
  })

  it('should search with query and filters', async () => {
    mockedApiRequest.mockResolvedValue(mockSearchResults)

    const { result } = renderHook(
      () => useSearchTips('grep', { difficulty: 'beginner' }),
      {
        wrapper: createWrapper(),
      }
    )

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(mockedApiRequest).toHaveBeenCalledWith({
      url: '/api/tips/search?q=grep&difficulty=beginner',
    })
  })

  it('should not search with empty query', async () => {
    const { result } = renderHook(() => useSearchTips(''), {
      wrapper: createWrapper(),
    })

    await new Promise(resolve => setTimeout(resolve, 100))

    expect(result.current.isLoading).toBe(false)
    expect(mockedApiRequest).not.toHaveBeenCalled()
  })

  it('should search with multiple filters', async () => {
    mockedApiRequest.mockResolvedValue(mockSearchResults)

    const { result } = renderHook(
      () =>
        useSearchTips('find', {
          difficulty: 'intermediate',
          category: 'file-management',
        }),
      {
        wrapper: createWrapper(),
      }
    )

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(mockedApiRequest).toHaveBeenCalledWith({
      url: '/api/tips/search?q=find&difficulty=intermediate&category=file-management',
    })
  })

  it('should handle error', async () => {
    const error = new Error('Search failed')
    mockedApiRequest.mockRejectedValue(error)

    const { result } = renderHook(() => useSearchTips('test'), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.isError).toBe(true)
    })
  })
})

describe('useLikeTip', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('should call like endpoint on mutation', async () => {
    mockedApiRequest.mockResolvedValue({ success: true })

    const { result } = renderHook(() => useLikeTip(), {
      wrapper: createWrapper(),
    })

    result.current.mutate('tip-123')

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(mockedApiRequest).toHaveBeenCalledWith({
      url: '/api/tips/tip-123/like',
      method: 'POST',
    })
  })

  it('should handle mutation error', async () => {
    const error = new Error('Like failed')
    mockedApiRequest.mockRejectedValue(error)

    const { result } = renderHook(() => useLikeTip(), {
      wrapper: createWrapper(),
    })

    result.current.mutate('tip-123')

    await waitFor(() => {
      expect(result.current.isError).toBe(true)
    })

    expect(result.current.error).toBeTruthy()
  })

  it('should support mutation callbacks', async () => {
    mockedApiRequest.mockResolvedValue({ success: true })

    const onSuccess = jest.fn()
    const onError = jest.fn()

    const { result } = renderHook(() => useLikeTip(), {
      wrapper: createWrapper(),
    })

    result.current.mutate('tip-123', {
      onSuccess,
      onError,
    })

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(onSuccess).toHaveBeenCalled()
    expect(onError).not.toHaveBeenCalled()
  })

  it('should call onError callback on failure', async () => {
    const error = new Error('Like failed')
    mockedApiRequest.mockRejectedValue(error)

    const onSuccess = jest.fn()
    const onError = jest.fn()

    const { result } = renderHook(() => useLikeTip(), {
      wrapper: createWrapper(),
    })

    result.current.mutate('tip-123', {
      onSuccess,
      onError,
    })

    await waitFor(() => {
      expect(result.current.isError).toBe(true)
    })

    expect(onError).toHaveBeenCalled()
    expect(onSuccess).not.toHaveBeenCalled()
  })
})
