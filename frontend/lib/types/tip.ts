/**
 * Linux Daily Tips - Frontend Type Definitions
 *
 * 백엔드 데이터 모델과 동기화된 TypeScript 인터페이스 정의
 * Backend Models: TipData, DraftWeek, TerminalSetup
 */

// 난이도 레벨 타입
export type DifficultyLevel = 'Beginner' | 'Intermediate' | 'Advanced'

// 팁 카테고리 타입
export type TipCategory =
  | 'File Management'
  | 'System Monitoring'
  | 'Networking'
  | 'Process Management'
  | 'Text Processing'
  | 'Package Management'
  | 'Security'
  | 'Search'
  | 'Archive'
  | 'Permissions'

// 터미널 설정 인터페이스 (TerminalSetup 모델과 연동)
export interface TerminalSetup {
  id: string
  tipId: number
  presetFiles: Array<{
    path: string
    content: string
    permissions: string
  }>
  workingDirectory: string
  environmentVars: Record<string, string>
  initialCommands: string[]
  createdAt: string
  updatedAt: string
}

// 개별 팁 데이터 인터페이스 (TipData 모델과 연동)
export interface TipData {
  id: number
  title: string
  description: string
  content: string // 마크다운 형식의 상세 내용
  command: string // 주요 명령어
  difficulty: DifficultyLevel
  category: TipCategory
  estimatedTime: string // "5 min", "10 min" 형식
  tags: string[]

  // 터미널 관련 설정
  terminalSetup?: TerminalSetup

  // 메타데이터
  publishDate: string // ISO 8601 형식
  lastUpdated: string // ISO 8601 형식
  viewCount: number
  likeCount: number
  isPublished: boolean

  // SEO 및 소셜 미디어
  slug: string // URL-friendly 제목
  metaDescription?: string
  socialImageUrl?: string
}

// 일주일치 드래프트 데이터 (DraftWeek 모델과 연동)
export interface DraftWeek {
  id: string
  weekNumber: number // 연도 내 주차 (1-52)
  year: number
  startDate: string // ISO 8601 형식
  endDate: string // ISO 8601 형식

  // 7개의 일일 팁 드래프트
  tips: TipData[]

  // 승인 워크플로우
  status: 'draft' | 'pending_review' | 'approved' | 'rejected' | 'published'
  createdBy: 'llm_auto' | 'manual'
  reviewedBy?: string // 관리자 ID
  reviewedAt?: string // ISO 8601 형식
  publishedAt?: string // ISO 8601 형식

  // LLM 생성 메타데이터
  llmModel?: string // 'gpt-4', 'claude-3' 등
  generationPrompt?: string
  generationDate?: string // ISO 8601 형식

  // 검토 노트
  reviewNotes?: string
  rejectionReason?: string
}

// API 응답을 위한 기본 인터페이스
export interface ApiResponse<T> {
  success: boolean
  data: T
  message?: string
  error?: string
  timestamp: string
}

// 페이지네이션 인터페이스
export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number
    limit: number
    totalItems: number
    totalPages: number
    hasNext: boolean
    hasPrevious: boolean
  }
}

// 통계 데이터 인터페이스
export interface StatsData {
  totalTips: number
  activeUsers: number
  completionRate: number // 백분율 (0-100)
  dailyActiveUsers: number
  weeklyActiveUsers: number
  monthlyActiveUsers: number
  popularCategories: Array<{
    category: TipCategory
    count: number
    percentage: number
  }>
  difficultyDistribution: Array<{
    difficulty: DifficultyLevel
    count: number
    percentage: number
  }>
}

// 사용자 진행 상황 (향후 Phase 2에서 사용)
export interface UserProgress {
  userId: string
  completedTips: number[]
  bookmarkedTips: number[]
  currentStreak: number
  longestStreak: number
  lastActivityDate: string // ISO 8601 형식
  totalTimeSpent: number // 분 단위
  achievements: string[]
  skillLevel: DifficultyLevel
}

// 검색 쿼리 인터페이스
export interface SearchQuery {
  query?: string
  category?: TipCategory
  difficulty?: DifficultyLevel
  tags?: string[]
  dateFrom?: string
  dateTo?: string
  sortBy?: 'date' | 'popularity' | 'difficulty' | 'title'
  sortOrder?: 'asc' | 'desc'
  page?: number
  limit?: number
}

// 터미널 세션 인터페이스 (Phase 1 MVP용)
export interface TerminalSession {
  id: string
  tipId?: number
  userId?: string // 익명 사용자의 경우 null
  status: 'active' | 'idle' | 'terminated'
  startedAt: string // ISO 8601 형식
  lastActivityAt: string // ISO 8601 형식
  commandHistory: Array<{
    command: string
    output: string
    timestamp: string
    exitCode: number
  }>
  workingDirectory: string
  environmentInfo: {
    containerImage: string
    memory: string
    cpu: string
  }
}

// 에러 타입 정의
export interface ApiError {
  code: string
  message: string
  field?: string // 유효성 검사 에러의 경우
  details?: Record<string, any>
}