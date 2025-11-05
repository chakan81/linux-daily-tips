/**
 * Terminal API Client
 *
 * API functions for terminal session management.
 */

import { apiRequest } from './client';
import { API_ENDPOINTS } from './endpoints';

/**
 * Terminal Session Response
 */
export interface TerminalSessionResponse {
  session_id: string;
  container_id: string;
  ws_url: string;
  status: string;
  expires_at: string;
}

/**
 * Create Session Request
 */
export interface CreateSessionRequest {
  tip_id?: string;
  session_data?: Record<string, any>;
}

/**
 * Create a new terminal session
 *
 * @param tipId - Optional tip ID to load pre-configured environment
 * @param sessionData - Optional additional session configuration
 * @returns Terminal session information including WebSocket URL
 *
 * @example
 * const session = await createTerminalSession('tip_12345');
 * console.log(session.ws_url); // ws://localhost:8000/api/v1/terminal/ws/session_xyz
 */
export async function createTerminalSession(
  tipId?: string,
  sessionData?: Record<string, any>
): Promise<TerminalSessionResponse> {
  const requestData: CreateSessionRequest = {};

  if (tipId) {
    requestData.tip_id = tipId;
  }

  if (sessionData) {
    requestData.session_data = sessionData;
  }

  return apiRequest<TerminalSessionResponse>({
    method: 'POST',
    url: API_ENDPOINTS.TERMINAL.CREATE_SESSION,
    data: requestData,
  });
}

/**
 * Delete a terminal session
 *
 * @param sessionId - Session ID to terminate
 * @returns Success response
 *
 * @example
 * await deleteTerminalSession('session_xyz');
 */
export async function deleteTerminalSession(sessionId: string): Promise<void> {
  return apiRequest<void>({
    method: 'DELETE',
    url: API_ENDPOINTS.TERMINAL.DESTROY(sessionId),
  });
}

/**
 * Get WebSocket URL for a session
 *
 * @param sessionId - Session ID
 * @returns Full WebSocket URL
 *
 * @example
 * const wsUrl = getWebSocketUrl('session_xyz');
 * // ws://localhost:8000/api/v1/terminal/ws/session_xyz
 */
export function getWebSocketUrl(sessionId: string): string {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const wsProtocol = apiUrl.startsWith('https') ? 'wss' : 'ws';
  const baseUrl = apiUrl.replace(/^https?:\/\//, '');

  return `${wsProtocol}://${baseUrl}${API_ENDPOINTS.TERMINAL.WS(sessionId)}`;
}
