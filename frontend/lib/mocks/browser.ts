/**
 * MSW Browser Setup
 *
 * 브라우저 환경에서 Service Worker를 이용한 API 모킹 설정
 */

import { setupWorker } from 'msw/browser'
import { handlers } from './handlers'

/**
 * MSW Service Worker 인스턴스
 */
export const worker = setupWorker(...handlers)
