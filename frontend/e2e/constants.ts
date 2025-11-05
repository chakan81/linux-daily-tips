/**
 * E2E Test Constants
 *
 * 테스트에서 사용되는 타임아웃 및 대기 시간 상수
 */

export const TIMEOUTS = {
  /** WebSocket 연결 대기 시간 */
  WEBSOCKET_CONNECTION: 2000,

  /** 명령어 실행 완료 대기 시간 */
  COMMAND_EXECUTION: 1000,

  /** 세션 종료 대기 시간 */
  SESSION_TERMINATION: 1000,

  /** 명령어 시퀀스 간격 */
  COMMAND_SEQUENCE: 500,

  /** 검색 입력 debounce 시간 + 네트워크 + 렌더링 */
  SEARCH_DEBOUNCE: 10000,

  /** 필터/정렬 URL 변경 대기 시간 */
  FILTER_UPDATE: 5000,

  /** 페이지 로딩 대기 시간 */
  PAGE_LOAD: 1000,

  /** DOM 업데이트 대기 시간 */
  DOM_UPDATE: 500,

  /** 팁 카드 로드 대기 시간 */
  TIP_CARD_LOAD: 10000,

  /** 터미널 화면 표시 대기 시간 */
  TERMINAL_SCREEN_VISIBLE: 2000,
} as const;

/**
 * E2E Test Assertions
 *
 * 테스트 검증에 사용되는 상수
 */
export const SCROLL_THRESHOLD = {
  /** 페이지 상단 스크롤 임계값 (px) */
  TOP: 100,
} as const;
