/**
 * Linux Daily Tips - Common Type Definitions
 *
 * 프로젝트 전반에서 사용되는 공통 타입 정의
 */

import { LucideIcon } from 'lucide-react'

/**
 * Custom Error with additional metadata
 */
export interface CustomError extends Error {
  statusCode?: number
  code?: string
}

/**
 * Icon component type for Lucide React icons
 */
export type IconComponent = LucideIcon

/**
 * Activity item for admin dashboard
 */
export interface Activity {
  id: number
  type: 'tip_created' | 'tip_approved' | 'user_activity' | 'system'
  message: string
  time: string
  status: 'pending' | 'approved' | 'success' | 'info'
}

/**
 * Batch review data for bulk operations
 */
export interface BatchReviewData {
  draftIds: number[]
  action: 'approve' | 'reject'
  rejectionReasons?: string[]
}

/**
 * Stats card props for dashboard
 */
export interface StatsCardProps {
  title: string
  value: string | number
  icon: IconComponent
  change?: string
  changeType?: 'positive' | 'negative' | 'neutral'
}

/**
 * Terminal WebSocket message data types
 */
export interface TerminalCommandData {
  command: string
  workingDirectory: string
}

export interface TerminalOutputData {
  output: string
  exitCode?: number
  stderr?: string
}

export interface TerminalStatusData {
  status: 'connected' | 'disconnected' | 'terminated' | 'timeout'
  reason?: string
}

export interface TerminalHeartbeatData {
  timestamp: string
}

export interface TerminalErrorData {
  message: string
  code?: string
}

/**
 * Union type for all terminal WebSocket data
 */
export type TerminalMessageData =
  | TerminalCommandData
  | TerminalOutputData
  | TerminalStatusData
  | TerminalHeartbeatData
  | TerminalErrorData

/**
 * Query parameter types for URL building
 */
export type QueryParamValue = string | number | boolean | undefined | null

export interface QueryParams {
  [key: string]: QueryParamValue | QueryParamValue[]
}

/**
 * Error details for API error responses
 */
export interface ErrorDetails {
  [key: string]: string | number | boolean | string[]
}
