import { useRef, useCallback, useEffect } from 'react';
import { Terminal } from '@xterm/xterm';

/**
 * useTerminalInput Hook
 *
 * 터미널 사용자 입력 처리
 * - Enter 키: 명령어 전송
 * - Backspace: 문자 삭제
 * - Ctrl+C: 인터럽트 신호 전송
 * - 일반 문자: 버퍼에 추가 및 화면 출력
 */
export function useTerminalInput(
  terminal: Terminal | null,
  sendCommand: ((cmd: string) => void) | null
) {
  const currentLineRef = useRef<string>('');

  /**
   * Enter 키 처리: 현재 라인을 명령어로 전송
   */
  const handleEnter = useCallback(() => {
    if (!terminal) return;

    terminal.write('\r\n');
    const command = currentLineRef.current;
    currentLineRef.current = '';

    if (command.trim() && sendCommand) {
      sendCommand(command);
    }
  }, [terminal, sendCommand]);

  /**
   * Backspace 키 처리: 마지막 문자 삭제
   */
  const handleBackspace = useCallback(() => {
    if (!terminal) return;

    if (currentLineRef.current.length > 0) {
      currentLineRef.current = currentLineRef.current.slice(0, -1);
      terminal.write('\b \b');
    }
  }, [terminal]);

  /**
   * Ctrl+C 처리: 인터럽트 신호 전송
   */
  const handleCtrlC = useCallback(() => {
    if (!terminal) return;

    terminal.write('^C\r\n');
    currentLineRef.current = '';
    if (sendCommand) {
      sendCommand('\u0003'); // Send interrupt signal
    }
  }, [terminal, sendCommand]);

  /**
   * 일반 문자 입력 처리: 버퍼에 추가 및 화면 출력
   */
  const handleRegularInput = useCallback((data: string) => {
    if (!terminal) return;

    currentLineRef.current += data;
    terminal.write(data);
  }, [terminal]);

  /**
   * 입력 데이터 라우팅
   *
   * @param data 키보드 입력 문자열
   */
  const handleInput = useCallback((data: string) => {
    if (data === '\r') {
      // Enter key
      handleEnter();
    } else if (data === '\u007F') {
      // Backspace
      handleBackspace();
    } else if (data === '\u0003') {
      // Ctrl+C
      handleCtrlC();
    } else if (data.charCodeAt(0) < 32) {
      // Ignore other control characters for now
      return;
    } else {
      // Regular character
      handleRegularInput(data);
    }
  }, [handleEnter, handleBackspace, handleCtrlC, handleRegularInput]);

  /**
   * 터미널 onData 이벤트 등록
   */
  useEffect(() => {
    if (!terminal) return;

    const disposable = terminal.onData(handleInput);
    return () => disposable.dispose();
  }, [terminal, handleInput]);

  return {
    currentLine: currentLineRef.current,
    handleInput,
  };
}
