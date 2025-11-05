import { useRef, useCallback, useEffect } from 'react';
import { Terminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';

export interface TerminalConfig {
  cursorBlink?: boolean;
  theme?: Record<string, string>;
  fontSize?: number;
  fontFamily?: string;
  fontWeight?: number;
  fontWeightBold?: number;
  lineHeight?: number;
  letterSpacing?: number;
  rows?: number;
  cols?: number;
  scrollback?: number;
  allowTransparency?: boolean;
  convertEol?: boolean;
}

/**
 * useTerminal Hook
 *
 * xterm.js 터미널 생명주기 관리
 * - 터미널 인스턴스 생성 및 초기화
 * - FitAddon을 통한 자동 리사이즈
 * - 윈도우 리사이즈 이벤트 처리
 * - 정리(cleanup)
 */
export function useTerminal(config: TerminalConfig) {
  const xtermRef = useRef<Terminal | null>(null);
  const fitAddonRef = useRef<FitAddon | null>(null);

  /**
   * 터미널 초기화
   *
   * @param container DOM 컨테이너 요소
   * @returns 생성된 Terminal 인스턴스
   */
  const initializeTerminal = useCallback((container: HTMLDivElement) => {
    const terminal = new Terminal(config);
    const fitAddon = new FitAddon();

    // Load addons
    terminal.loadAddon(fitAddon);

    // Open terminal in DOM
    terminal.open(container);

    // Store refs
    xtermRef.current = terminal;
    fitAddonRef.current = fitAddon;

    // Fit terminal to container (after next frame to ensure renderer is ready)
    requestAnimationFrame(() => {
      try {
        fitAddon.fit();
      } catch (err) {
        console.warn('Error fitting terminal on initial load:', err);
      }
    });

    // Write welcome message
    terminal.writeln('\x1b[1;32mLinux Daily Tips Terminal\x1b[0m');
    terminal.writeln('\x1b[90mConnecting to session...\x1b[0m');
    terminal.writeln('');

    return terminal;
  }, [config]);

  /**
   * 터미널 정리(dispose)
   */
  const disposeTerminal = useCallback(() => {
    if (xtermRef.current) {
      xtermRef.current.dispose();
      xtermRef.current = null;
      fitAddonRef.current = null;
    }
  }, []);

  /**
   * 터미널 리사이즈
   */
  const fitTerminal = useCallback(() => {
    if (fitAddonRef.current) {
      try {
        fitAddonRef.current.fit();
      } catch (err) {
        console.warn('Error fitting terminal:', err);
      }
    }
  }, []);

  /**
   * 윈도우 리사이즈 이벤트 핸들러 등록
   */
  useEffect(() => {
    window.addEventListener('resize', fitTerminal);
    return () => {
      window.removeEventListener('resize', fitTerminal);
    };
  }, [fitTerminal]);

  return {
    terminal: xtermRef.current,
    fitAddon: fitAddonRef.current,
    initializeTerminal,
    disposeTerminal,
    fitTerminal,
  };
}
