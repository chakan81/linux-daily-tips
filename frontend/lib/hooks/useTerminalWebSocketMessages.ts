import { useCallback } from 'react';
import { Terminal } from '@xterm/xterm';

/**
 * useTerminalWebSocketMessages Hook
 *
 * WebSocket 메시지 처리
 * - output: 터미널 출력
 * - error: 에러 메시지 표시
 */
export function useTerminalWebSocketMessages(terminal: Terminal | null) {
  /**
   * WebSocket 메시지 핸들러
   *
   * @param message WebSocket으로 수신한 메시지 객체
   */
  const handleMessage = useCallback((message: any) => {
    if (!terminal) return;

    console.log('[Terminal] Handling message:', message.type, message.data);

    switch (message.type) {
      case 'output':
        if (message.data) {
          terminal.write(message.data);
        }
        break;
      case 'error':
        terminal.writeln(`\r\n\x1b[1;31mError: ${message.message || 'Unknown error'}\x1b[0m\r\n`);
        break;
    }
  }, [terminal]);

  return { handleMessage };
}
