'use client';

/**
 * TerminalEmulator Component
 *
 * A web-based terminal emulator using xterm.js.
 * Connects to a backend terminal session via WebSocket and provides
 * an interactive command-line interface in the browser.
 */

import { useEffect, useRef, useState } from 'react';
import { useTerminalWebSocket } from '@/lib/hooks';
import { useTerminal } from '@/lib/hooks/useTerminal';
import { useTerminalInput } from '@/lib/hooks/useTerminalInput';
import { useTerminalWebSocketMessages } from '@/lib/hooks/useTerminalWebSocketMessages';
import '@xterm/xterm/css/xterm.css';

/**
 * Component props
 */
export interface TerminalEmulatorProps {
  sessionId: string;
  wsUrl: string;
  onSessionEnd?: () => void;
}

/**
 * Terminal configuration
 */
const TERMINAL_CONFIG = {
  cursorBlink: true,
  theme: {
    background: '#1e1e1e',
    foreground: '#ffffff',
    cursor: '#ffffff',
    cursorAccent: '#000000',
    selection: 'rgba(255, 255, 255, 0.3)',
    black: '#000000',
    red: '#e74856',
    green: '#16c60c',
    yellow: '#f9f1a5',
    blue: '#3b78ff',
    magenta: '#b4009e',
    cyan: '#61d6d6',
    white: '#cccccc',
    brightBlack: '#808080',
    brightRed: '#e74856',
    brightGreen: '#16c60c',
    brightYellow: '#f9f1a5',
    brightBlue: '#3b78ff',
    brightMagenta: '#b4009e',
    brightCyan: '#61d6d6',
    brightWhite: '#ffffff',
  },
  fontSize: 14,
  fontFamily: 'JetBrains Mono, Menlo, Monaco, "Courier New", monospace',
  fontWeight: 400,
  fontWeightBold: 700,
  lineHeight: 1.2,
  letterSpacing: 0,
  rows: 24,
  cols: 80,
  scrollback: 1000,
  allowTransparency: false,
  convertEol: true,
} as const;

/**
 * TerminalEmulator Component
 *
 * @example
 * <TerminalEmulator
 *   sessionId="session_xyz"
 *   wsUrl="ws://localhost:8000/api/v1/terminal/ws/session_xyz"
 *   onSessionEnd={() => console.log('Session ended')}
 * />
 */
export function TerminalEmulator({ sessionId, wsUrl, onSessionEnd }: TerminalEmulatorProps) {
  // Refs
  const terminalRef = useRef<HTMLDivElement>(null);

  // State
  const [isReady, setIsReady] = useState(false);

  // Terminal lifecycle management
  const { terminal, initializeTerminal, disposeTerminal } = useTerminal(TERMINAL_CONFIG);

  // WebSocket message handling
  const { handleMessage } = useTerminalWebSocketMessages(terminal);

  // WebSocket connection
  const { isConnected, isConnecting, error, sendCommand, disconnect } = useTerminalWebSocket(wsUrl, {
    onMessage: handleMessage,
  });

  // Terminal input handling
  useTerminalInput(terminal, sendCommand);

  /**
   * Initialize xterm.js terminal
   */
  useEffect(() => {
    if (!terminalRef.current) return;

    // Initialize terminal
    initializeTerminal(terminalRef.current);
    setIsReady(true);

    // Cleanup
    return () => {
      disposeTerminal();
    };
  }, [initializeTerminal, disposeTerminal]);

  /**
   * Handle connection status changes
   */
  useEffect(() => {
    if (!terminal) return;

    if (isConnected) {
      // 우측 하단에 연결 상태 표시가 있으므로 터미널에 중복 메시지 출력하지 않음
      // Race condition 방지: 백엔드 프롬프트와 겹치지 않도록 함
      terminal.focus();
    } else if (error) {
      terminal.writeln(`\r\n\x1b[1;31mConnection Error: ${error}\x1b[0m\r\n`);
    }
  }, [terminal, isConnected, error]);

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      // WebSocket 연결만 끊고, onSessionEnd는 호출하지 않음
      // (React Strict Mode의 이중 마운트로 인한 의도하지 않은 세션 종료 방지)
      disconnect();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="relative w-full h-full bg-[#1e1e1e] rounded-lg overflow-hidden">
      {/* Terminal container */}
      <div
        ref={terminalRef}
        className="w-full h-full p-4"
        style={{ minHeight: '400px' }}
      />

      {/* Connection status overlay */}
      {!isReady && (
        <div className="absolute inset-0 flex items-center justify-center bg-[#1e1e1e]">
          <div className="text-center">
            <div className="text-gray-400 mb-2">Initializing terminal...</div>
          </div>
        </div>
      )}

      {/* Error overlay */}
      {error && !isConnected && (
        <div className="absolute top-4 right-4 bg-red-900 text-red-100 px-4 py-2 rounded-lg text-sm">
          {error}
        </div>
      )}

      {/* Connection indicator */}
      <div className="absolute bottom-4 right-4 flex items-center gap-2 bg-gray-800 px-3 py-1 rounded-full text-xs">
        <div
          className={`w-2 h-2 rounded-full ${
            isConnected ? 'bg-green-500' : isConnecting ? 'bg-yellow-500 animate-pulse' : 'bg-red-500'
          }`}
        />
        <span className="text-gray-300">
          {isConnected ? 'Connected' : isConnecting ? 'Connecting' : 'Disconnected'}
        </span>
        <span className="text-gray-500">•</span>
        <span className="text-gray-400 font-mono">{sessionId.slice(-8)}</span>
      </div>
    </div>
  );
}
