'use client';

/**
 * TerminalEmulator Component
 *
 * A web-based terminal emulator using xterm.js.
 * Connects to a backend terminal session via WebSocket and provides
 * an interactive command-line interface in the browser.
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import { Terminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import { useTerminalWebSocket, WebSocketMessage } from '@/lib/hooks';
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
  const xtermRef = useRef<Terminal | null>(null);
  const fitAddonRef = useRef<FitAddon | null>(null);
  const currentLineRef = useRef<string>('');
  const sendCommandRef = useRef<((command: string) => void) | null>(null);

  // State
  const [isReady, setIsReady] = useState(false);

  // WebSocket message handler callback
  const handleMessage = useCallback((message: any) => {
    if (!xtermRef.current) return;

    const terminal = xtermRef.current;
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
  }, []);

  // WebSocket connection
  const { isConnected, isConnecting, error, sendCommand, disconnect, lastMessage } = useTerminalWebSocket(wsUrl, {
    onMessage: handleMessage,
  });

  // Update sendCommand ref whenever it changes
  sendCommandRef.current = sendCommand;

  /**
   * Initialize xterm.js terminal
   */
  useEffect(() => {
    if (!terminalRef.current) return;

    // Create terminal instance
    const terminal = new Terminal(TERMINAL_CONFIG);
    const fitAddon = new FitAddon();

    // Load addons
    terminal.loadAddon(fitAddon);

    // Open terminal in DOM
    terminal.open(terminalRef.current);

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

    setIsReady(true);

    // Handle user input
    terminal.onData((data) => {
      // Handle special keys
      if (data === '\r') {
        // Enter key - send command
        terminal.write('\r\n');
        const command = currentLineRef.current;
        currentLineRef.current = '';

        if (command.trim() && sendCommandRef.current) {
          sendCommandRef.current(command);
        }
      } else if (data === '\u007F') {
        // Backspace
        if (currentLineRef.current.length > 0) {
          currentLineRef.current = currentLineRef.current.slice(0, -1);
          terminal.write('\b \b');
        }
      } else if (data === '\u0003') {
        // Ctrl+C
        terminal.write('^C\r\n');
        currentLineRef.current = '';
        if (sendCommandRef.current) {
          sendCommandRef.current('\u0003'); // Send interrupt signal
        }
      } else if (data.charCodeAt(0) < 32) {
        // Ignore other control characters for now
        return;
      } else {
        // Regular character
        currentLineRef.current += data;
        terminal.write(data);
      }
    });

    // Handle window resize
    const handleResize = () => {
      if (fitAddonRef.current) {
        try {
          fitAddonRef.current.fit();
        } catch (err) {
          console.warn('Error fitting terminal:', err);
        }
      }
    };

    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      terminal.dispose();
      xtermRef.current = null;
      fitAddonRef.current = null;
    };
  }, []); // ✅ 빈 배열: 터미널은 한 번만 초기화

  /**
   * Handle connection status changes
   */
  useEffect(() => {
    if (!xtermRef.current) return;

    const terminal = xtermRef.current;

    if (isConnected) {
      // 우측 하단에 연결 상태 표시가 있으므로 터미널에 중복 메시지 출력하지 않음
      // Race condition 방지: 백엔드 프롬프트와 겹치지 않도록 함
      terminal.focus();
    } else if (isConnecting) {
      terminal.writeln('\x1b[90mConnecting...\x1b[0m');
    } else if (error) {
      terminal.writeln(`\r\n\x1b[1;31mConnection Error: ${error}\x1b[0m\r\n`);
    }
  }, [isConnected, isConnecting, error]);

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
