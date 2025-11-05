import { useCallback, useRef, useEffect } from 'react';
import { Terminal } from '@xterm/xterm';

/**
 * useTerminalWebSocketMessages Hook
 *
 * WebSocket 메시지 처리 (레이스 컨디션 해결)
 * - output: 터미널 출력
 * - error: 에러 메시지 표시
 * - 터미널 초기화 전에 받은 메시지는 버퍼에 저장 후 나중에 출력
 */
export function useTerminalWebSocketMessages(terminal: Terminal | null) {
  // 터미널 준비 전에 받은 메시지 버퍼
  const messageBufferRef = useRef<any[]>([]);

  /**
   * 실제 메시지 처리 함수
   */
  const processMessage = useCallback((message: any, term: Terminal) => {
    console.log('[Terminal] Processing message:', message.type, message.data);

    switch (message.type) {
      case 'output':
        if (message.data) {
          term.write(message.data);
        }
        break;
      case 'error':
        term.writeln(`\r\n\x1b[1;31mError: ${message.message || 'Unknown error'}\x1b[0m\r\n`);
        break;
    }
  }, []);

  /**
   * 터미널이 준비되면 버퍼의 모든 메시지 출력
   */
  useEffect(() => {
    if (!terminal) return;

    // 버퍼에 쌓인 메시지 모두 출력
    if (messageBufferRef.current.length > 0) {
      console.log(`[Terminal] Flushing ${messageBufferRef.current.length} buffered messages`);
      messageBufferRef.current.forEach(msg => processMessage(msg, terminal));
      messageBufferRef.current = [];
    }
  }, [terminal, processMessage]);

  /**
   * WebSocket 메시지 핸들러
   *
   * @param message WebSocket으로 수신한 메시지 객체
   */
  const handleMessage = useCallback((message: any) => {
    if (!terminal) {
      // 터미널이 아직 준비되지 않았으면 버퍼에 저장
      console.log('[Terminal] Terminal not ready, buffering message:', message.type);
      messageBufferRef.current.push(message);
      return;
    }

    // 터미널이 준비되었으면 즉시 처리
    processMessage(message, terminal);
  }, [terminal, processMessage]);

  return { handleMessage };
}
