/**
 * useTerminalWebSocket Hook
 *
 * Custom React hook for managing WebSocket connections to terminal sessions.
 * Handles connection lifecycle, message sending/receiving, and automatic reconnection.
 */

import { useEffect, useRef, useState, useCallback } from 'react';

/**
 * WebSocket message types
 */
export type WebSocketMessageType = 'command' | 'ping' | 'output' | 'error' | 'pong';

/**
 * WebSocket message structure
 */
export interface WebSocketMessage {
  type: WebSocketMessageType;
  data?: string;
  exit_code?: number;
  code?: string;
  message?: string;
}

/**
 * WebSocket connection states
 */
export type ConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'error';

/**
 * Hook return type
 */
export interface UseTerminalWebSocketReturn {
  isConnected: boolean;
  isConnecting: boolean;
  error: string | null;
  sendCommand: (command: string) => void;
  disconnect: () => void;
  lastMessage: WebSocketMessage | null;
}

/**
 * Hook configuration
 */
interface UseTerminalWebSocketConfig {
  pingInterval?: number; // Ping interval in milliseconds (default: 30000)
  reconnectAttempts?: number; // Max reconnection attempts (default: 3)
  reconnectDelay?: number; // Delay between reconnection attempts in ms (default: 1000)
  onMessage?: (message: WebSocketMessage) => void; // Callback for immediate message handling
}

const DEFAULT_CONFIG: UseTerminalWebSocketConfig = {
  pingInterval: 30000, // 30 seconds
  reconnectAttempts: 3,
  reconnectDelay: 1000,
  onMessage: undefined,
};

/**
 * Custom hook for terminal WebSocket connections
 *
 * @param wsUrl - WebSocket URL (null to disable connection)
 * @param config - Optional configuration
 * @returns WebSocket connection state and control functions
 *
 * @example
 * const { isConnected, sendCommand, lastMessage } = useTerminalWebSocket(
 *   'ws://localhost:8000/api/v1/terminal/ws/session_xyz'
 * );
 *
 * useEffect(() => {
 *   if (lastMessage?.type === 'output') {
 *     console.log('Terminal output:', lastMessage.data);
 *   }
 * }, [lastMessage]);
 *
 * sendCommand('ls -la');
 */
export function useTerminalWebSocket(
  wsUrl: string | null,
  config: UseTerminalWebSocketConfig = {}
): UseTerminalWebSocketReturn {
  const mergedConfig = { ...DEFAULT_CONFIG, ...config };

  // State
  const [status, setStatus] = useState<ConnectionStatus>('disconnected');
  const [error, setError] = useState<string | null>(null);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);

  // Refs
  const wsRef = useRef<WebSocket | null>(null);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const isManualDisconnectRef = useRef(false);
  const onMessageRef = useRef(mergedConfig.onMessage); // 최신 onMessage 콜백 참조

  // Update onMessage ref when it changes
  useEffect(() => {
    onMessageRef.current = mergedConfig.onMessage;
  }, [mergedConfig.onMessage]);

  /**
   * Clear ping interval
   */
  const clearPingInterval = useCallback(() => {
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }
  }, []);

  /**
   * Start ping interval
   */
  const startPingInterval = useCallback(() => {
    clearPingInterval();

    pingIntervalRef.current = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        try {
          wsRef.current.send(JSON.stringify({ type: 'ping' }));
        } catch (err) {
          console.error('Failed to send ping:', err);
        }
      }
    }, mergedConfig.pingInterval);
  }, [clearPingInterval, mergedConfig.pingInterval]);

  /**
   * Send command to terminal
   */
  const sendCommand = useCallback((command: string) => {
    if (!wsRef.current) {
      console.error('WebSocket not initialized');
      return;
    }

    if (wsRef.current.readyState !== WebSocket.OPEN) {
      console.error('WebSocket not connected');
      return;
    }

    try {
      const message: WebSocketMessage = {
        type: 'command',
        data: command,
      };

      wsRef.current.send(JSON.stringify(message));
    } catch (err) {
      console.error('Failed to send command:', err);
      setError('Failed to send command');
    }
  }, []);

  /**
   * Manually disconnect WebSocket
   */
  const disconnect = useCallback(() => {
    isManualDisconnectRef.current = true;
    clearPingInterval();

    if (wsRef.current) {
      wsRef.current.close(1000, 'Manual disconnect');
      wsRef.current = null;
    }

    setStatus('disconnected');
    setError(null);
  }, [clearPingInterval]);

  /**
   * Connect to WebSocket
   */
  const connect = useCallback(() => {
    if (!wsUrl) return;
    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    if (isManualDisconnectRef.current) return;

    try {
      setStatus('connecting');
      setError(null);

      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected');
        setStatus('connected');
        setError(null);
        reconnectAttemptsRef.current = 0;
        startPingInterval();
      };

      ws.onmessage = (event) => {
        try {
          console.log('[WS] Raw message received:', event.data);
          const message: WebSocketMessage = JSON.parse(event.data);
          console.log('[WS] Parsed message:', message);

          // Call onMessage callback immediately if provided
          // Use ref to always get the latest callback
          if (onMessageRef.current) {
            onMessageRef.current(message);
          }

          setLastMessage(message);

          // Handle different message types
          switch (message.type) {
            case 'output':
              // Output will be handled by the component
              break;
            case 'error':
              console.error('Terminal error:', message.message);
              setError(message.message || 'Terminal error occurred');
              break;
            case 'pong':
              // Pong received, connection is alive
              break;
            default:
              console.warn('Unknown message type:', message.type);
          }
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      ws.onerror = (event) => {
        console.error('WebSocket error:', event);
        setStatus('error');
        setError('WebSocket connection error');
      };

      ws.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason);
        clearPingInterval();
        wsRef.current = null;

        // Attempt reconnection if not manual disconnect
        const maxAttempts = mergedConfig.reconnectAttempts ?? 3;
        if (!isManualDisconnectRef.current && reconnectAttemptsRef.current < maxAttempts) {
          reconnectAttemptsRef.current += 1;
          console.log(`Reconnection attempt ${reconnectAttemptsRef.current}/${maxAttempts}`);

          setTimeout(() => {
            if (!isManualDisconnectRef.current) {
              connect();
            }
          }, mergedConfig.reconnectDelay);
        } else {
          setStatus('disconnected');
          const maxAttempts = mergedConfig.reconnectAttempts ?? 3;
          if (reconnectAttemptsRef.current >= maxAttempts) {
            setError('Failed to reconnect after multiple attempts');
          }
        }
      };
    } catch (err) {
      console.error('Failed to create WebSocket:', err);
      setStatus('error');
      setError('Failed to create WebSocket connection');
    }
  }, [wsUrl, startPingInterval, clearPingInterval, mergedConfig.reconnectAttempts, mergedConfig.reconnectDelay]);

  /**
   * Effect: Connect when wsUrl changes
   */
  useEffect(() => {
    if (wsUrl) {
      isManualDisconnectRef.current = false;
      connect();
    }

    // Cleanup on unmount or wsUrl change
    return () => {
      isManualDisconnectRef.current = true;
      clearPingInterval();

      if (wsRef.current) {
        wsRef.current.close(1000, 'Component unmounted');
        wsRef.current = null;
      }
    };
  }, [wsUrl, connect, clearPingInterval]);

  return {
    isConnected: status === 'connected',
    isConnecting: status === 'connecting',
    error,
    sendCommand,
    disconnect,
    lastMessage,
  };
}
