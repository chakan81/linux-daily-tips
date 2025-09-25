/**
 * Linux Daily Tips - Type Exports
 *
 * 프론트엔드에서 사용할 모든 타입 정의를 중앙 집중식으로 export
 * 백엔드 데이터 모델과 동기화된 TypeScript 인터페이스
 */

// ===== 핵심 데이터 타입 =====
export type {
  DifficultyLevel,
  TipCategory,
  TipData,
  TerminalSetup,
  DraftWeek,
  StatsData,
  UserProgress,
  SearchQuery,
  TerminalSession,
  ApiResponse,
  PaginatedResponse,
  ApiError,
} from './tip'

// ===== API 통신 타입 =====
export type {
  // Daily Tips API
  DailyTipResponse,
  TipsListResponse,
  TipDetailResponse,
  TipSearchRequest,
  TipSearchResponse,
  StatsResponse,

  // Admin API
  AdminLoginRequest,
  AdminLoginResponse,
  DraftWeeksResponse,
  ApproveDraftRequest,
  ApproveDraftResponse,
  RejectDraftRequest,
  RejectDraftResponse,

  // Terminal API
  CreateTerminalRequest,
  CreateTerminalResponse,
  TerminalWebSocketMessage,
  TerminalCommandMessage,
  TerminalOutputMessage,
  TerminalStatusMessage,
  TerminalStatusResponse,
  TerminateTerminalResponse,

  // LLM API (Phase 2)
  GenerateWeekRequest,
  GenerateWeekResponse,

  // HTTP Client
  ApiClientConfig,
  RequestConfig,

  // Error Types
  ApiErrorResponse,
  NetworkError,
  ValidationError,
  AuthenticationError,
  AuthorizationError,
  ApiError as ApiErrorUnion,

  // React Query
  QueryOptions,
  MutationOptions,

  // Utility Types
  ExtractApiData,
  ExtractPaginatedData,
  PartialExcept,
  ApiCreateRequest,
  ApiUpdateRequest,
} from './api'

// ===== 컴포넌트 Props 타입 =====

// TipCard 컴포넌트 Props
export interface TipCardProps {
  tip: TipData
  variant?: 'default' | 'compact' | 'featured'
  showCategory?: boolean
  showDifficulty?: boolean
  showEstimatedTime?: boolean
  onClick?: (tip: TipData) => void
  className?: string
}

// DifficultyBadge 컴포넌트 Props
export interface DifficultyBadgeProps {
  difficulty: DifficultyLevel
  size?: 'sm' | 'md' | 'lg'
  variant?: 'default' | 'outline' | 'minimal'
  className?: string
}

// TerminalEmulator 컴포넌트 Props
export interface TerminalEmulatorProps {
  sessionId?: string
  tipId?: number
  autoConnect?: boolean
  onCommand?: (command: string) => void
  onOutput?: (output: string) => void
  onError?: (error: string) => void
  onStatusChange?: (status: 'connected' | 'disconnected' | 'terminated') => void
  className?: string
  height?: string | number
}

// SearchFilters 컴포넌트 Props
export interface SearchFiltersProps {
  query: SearchQuery
  onQueryChange: (query: Partial<SearchQuery>) => void
  categories: TipCategory[]
  difficulties: DifficultyLevel[]
  className?: string
}

// StatsCard 컴포넌트 Props
export interface StatsCardProps {
  title: string
  value: string | number
  description?: string
  icon?: React.ComponentType<{ className?: string }>
  trend?: {
    value: number
    label: string
    isPositive: boolean
  }
  className?: string
}

// Pagination 컴포넌트 Props
export interface PaginationProps {
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
  showFirstLast?: boolean
  showPrevNext?: boolean
  maxVisiblePages?: number
  className?: string
}

// ===== Hook 반환 타입 =====

// useTip 훅
export interface UseTipReturn {
  tip: TipData | null
  isLoading: boolean
  error: ApiError | null
  refetch: () => void
}

// useTipsList 훅
export interface UseTipsListReturn {
  tips: TipData[]
  pagination: PaginatedResponse<TipData>['pagination'] | null
  isLoading: boolean
  error: ApiError | null
  refetch: () => void
  loadMore: () => void
  hasMore: boolean
}

// useTerminalSession 훅
export interface UseTerminalSessionReturn {
  session: TerminalSession | null
  isConnected: boolean
  isLoading: boolean
  error: ApiError | null
  sendCommand: (command: string) => void
  connect: () => void
  disconnect: () => void
  commandHistory: TerminalSession['commandHistory']
}

// useStats 훅
export interface UseStatsReturn {
  stats: StatsData | null
  isLoading: boolean
  error: ApiError | null
  refetch: () => void
  lastUpdated: string | null
}

// ===== Form 타입 =====

// 검색 폼
export interface SearchFormData {
  query: string
  category: TipCategory | 'all'
  difficulty: DifficultyLevel | 'all'
  tags: string[]
}

// 관리자 로그인 폼
export interface AdminLoginFormData {
  username: string
  password: string
  remember?: boolean
}

// 드래프트 리뷰 폼
export interface DraftReviewFormData {
  action: 'approve' | 'reject'
  notes: string
  publishDate?: string
  regenerate?: boolean // reject 시에만
}

// ===== Context 타입 =====

// Theme Context
export interface ThemeContextType {
  theme: 'light' | 'dark' | 'system'
  setTheme: (theme: 'light' | 'dark' | 'system') => void
  resolvedTheme: 'light' | 'dark'
}

// Auth Context (Phase 2)
export interface AuthContextType {
  user: {
    id: string
    username: string
    role: 'admin' | 'super_admin'
  } | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (credentials: AdminLoginRequest) => Promise<void>
  logout: () => void
  refreshToken: () => Promise<void>
}

// ===== 유틸리티 타입 =====

// React Event 핸들러 타입
export type EventHandler<T = HTMLElement> = (event: React.MouseEvent<T>) => void
export type ChangeHandler<T = HTMLInputElement> = (event: React.ChangeEvent<T>) => void
export type FormSubmitHandler = (event: React.FormEvent<HTMLFormElement>) => void

// 공통 컴포넌트 Props
export interface BaseComponentProps {
  className?: string
  children?: React.ReactNode
  'data-testid'?: string
}

// 로딩 상태를 가진 컴포넌트
export interface LoadableComponentProps extends BaseComponentProps {
  isLoading?: boolean
  loadingText?: string
  error?: string | null
  retry?: () => void
}