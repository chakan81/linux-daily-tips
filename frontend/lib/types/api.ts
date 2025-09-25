/**
 * Linux Daily Tips - API Type Definitions
 *
 * FastAPI 백엔드와 통신을 위한 API 관련 타입 정의
 */

import {
  TipData,
  DraftWeek,
  StatsData,
  UserProgress,
  SearchQuery,
  TerminalSession,
  ApiResponse,
  PaginatedResponse,
  DifficultyLevel,
  TipCategory,
} from './tip'

// ===== API 엔드포인트 관련 타입 =====

// GET /api/tips/daily - 오늘의 팁 조회
export interface DailyTipResponse extends ApiResponse<TipData> {}

// GET /api/tips/history - 팁 목록 조회 (페이지네이션)
export interface TipsListResponse extends PaginatedResponse<TipData> {}

// GET /api/tips/{id} - 특정 팁 상세 조회
export interface TipDetailResponse extends ApiResponse<TipData> {}

// GET /api/tips/search - 팁 검색
export interface TipSearchRequest extends SearchQuery {}
export interface TipSearchResponse extends PaginatedResponse<TipData> {}

// GET /api/stats - 통계 조회
export interface StatsResponse extends ApiResponse<StatsData> {}

// ===== 관리자 API 타입 =====

// POST /api/admin/auth/login - 관리자 로그인
export interface AdminLoginRequest {
  username: string
  password: string
}

export interface AdminLoginResponse extends ApiResponse<{
  accessToken: string
  tokenType: string
  expiresIn: number
  user: {
    id: string
    username: string
    role: 'admin' | 'super_admin'
    lastLogin: string
  }
}> {}

// GET /api/admin/drafts - 드래프트 주간 목록
export interface DraftWeeksResponse extends PaginatedResponse<DraftWeek> {}

// POST /api/admin/drafts/{id}/approve - 드래프트 승인
export interface ApproveDraftRequest {
  reviewNotes?: string
  publishDate?: string // 특정 날짜에 발행하려는 경우
}

export interface ApproveDraftResponse extends ApiResponse<DraftWeek> {}

// POST /api/admin/drafts/{id}/reject - 드래프트 거부
export interface RejectDraftRequest {
  rejectionReason: string
  regenerate: boolean // 자동으로 새 드래프트 생성 여부
}

export interface RejectDraftResponse extends ApiResponse<DraftWeek> {}

// ===== 터미널 API 타입 =====

// POST /api/terminal/create - 새 터미널 세션 생성
export interface CreateTerminalRequest {
  tipId?: number // 특정 팁과 연관된 터미널 세션
  setupConfig?: {
    workingDirectory?: string
    environmentVars?: Record<string, string>
    presetFiles?: Array<{
      path: string
      content: string
      permissions?: string
    }>
  }
}

export interface CreateTerminalResponse extends ApiResponse<{
  sessionId: string
  websocketUrl: string
  expiresAt: string
}> {}

// WebSocket 메시지 타입들
export interface TerminalWebSocketMessage {
  type: 'command' | 'output' | 'error' | 'status' | 'heartbeat'
  sessionId: string
  timestamp: string
  data: any
}

export interface TerminalCommandMessage extends TerminalWebSocketMessage {
  type: 'command'
  data: {
    command: string
    workingDirectory: string
  }
}

export interface TerminalOutputMessage extends TerminalWebSocketMessage {
  type: 'output'
  data: {
    output: string
    exitCode?: number
    stderr?: string
  }
}

export interface TerminalStatusMessage extends TerminalWebSocketMessage {
  type: 'status'
  data: {
    status: 'connected' | 'disconnected' | 'terminated' | 'timeout'
    reason?: string
  }
}

// GET /api/terminal/{sessionId}/status - 터미널 세션 상태 조회
export interface TerminalStatusResponse extends ApiResponse<TerminalSession> {}

// DELETE /api/terminal/{sessionId} - 터미널 세션 종료
export interface TerminateTerminalResponse extends ApiResponse<{
  sessionId: string
  terminatedAt: string
}> {}

// ===== LLM 관련 API 타입 (Phase 2) =====

// POST /api/llm/generate-week - 일주일치 팁 생성 요청
export interface GenerateWeekRequest {
  weekNumber: number
  year: number
  focusCategories?: TipCategory[]
  difficultyDistribution?: {
    beginner: number
    intermediate: number
    advanced: number
  }
  excludeTopics?: string[]
  customPrompt?: string
}

export interface GenerateWeekResponse extends ApiResponse<DraftWeek> {}

// ===== HTTP 클라이언트 설정 타입 =====

export interface ApiClientConfig {
  baseURL: string
  timeout: number
  retries: number
  retryDelay: number
  headers?: Record<string, string>
}

export interface RequestConfig {
  timeout?: number
  retries?: number
  retryDelay?: number
  headers?: Record<string, string>
  cache?: boolean
  cacheTime?: number
}

// ===== 에러 처리 타입 =====

export interface ApiErrorResponse {
  success: false
  error: string
  message: string
  statusCode: number
  timestamp: string
  path: string
  details?: Record<string, any>
}

export interface NetworkError {
  type: 'network'
  message: string
  code?: string
  retry?: boolean
}

export interface ValidationError {
  type: 'validation'
  message: string
  field: string
  value: any
  constraint: string
}

export interface AuthenticationError {
  type: 'authentication'
  message: string
  redirectTo?: string
}

export interface AuthorizationError {
  type: 'authorization'
  message: string
  requiredRole?: string
  currentRole?: string
}

// Union type for all possible API errors
export type ApiError =
  | NetworkError
  | ValidationError
  | AuthenticationError
  | AuthorizationError

// ===== React Query 관련 타입 =====

export interface QueryOptions {
  enabled?: boolean
  refetchOnWindowFocus?: boolean
  refetchOnReconnect?: boolean
  staleTime?: number
  cacheTime?: number
  retry?: number | boolean
}

export interface MutationOptions<TData, TError, TVariables> {
  onSuccess?: (data: TData, variables: TVariables) => void
  onError?: (error: TError, variables: TVariables) => void
  onSettled?: (data: TData | undefined, error: TError | null, variables: TVariables) => void
}

// ===== 유틸리티 타입 =====

// API 응답에서 data 부분만 추출
export type ExtractApiData<T> = T extends ApiResponse<infer U> ? U : never

// 페이지네이션 응답에서 데이터 배열 추출
export type ExtractPaginatedData<T> = T extends PaginatedResponse<infer U> ? U : never

// Optional fields를 위한 유틸리티 타입
export type PartialExcept<T, K extends keyof T> = Partial<T> & Pick<T, K>

// API 요청을 위해 timestamp 등을 제외한 타입
export type ApiCreateRequest<T> = Omit<T, 'id' | 'createdAt' | 'updatedAt' | 'publishedAt'>
export type ApiUpdateRequest<T> = PartialExcept<ApiCreateRequest<T>, 'id'>