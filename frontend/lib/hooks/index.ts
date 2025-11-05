/**
 * React Hooks Module
 *
 * Custom hooks for data fetching and state management.
 */

// React Query hooks
export {
  useTodayTip,
  useRecentTips,
  useTip,
  useTipsList,
  useSearchTips,
  useLikeTip,
} from './useTips';

// WebSocket hooks
export { useTerminalWebSocket } from './useTerminalWebSocket';
export type {
  UseTerminalWebSocketReturn,
  WebSocketMessage,
  WebSocketMessageType,
  ConnectionStatus,
} from './useTerminalWebSocket';

// Terminal hooks
export { useTerminal } from './useTerminal';
export type { TerminalConfig } from './useTerminal';
export { useTerminalInput } from './useTerminalInput';
export { useTerminalWebSocketMessages } from './useTerminalWebSocketMessages';

// Add more hook exports as they are created
// export * from './useAuth';
// export * from './useStats';
// export * from './useDrafts';
