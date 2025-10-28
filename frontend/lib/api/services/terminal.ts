/**
 * Terminal API Service
 *
 * Provides API methods for managing terminal sessions.
 */

import { apiRequest } from '@/lib/api/client';
import { API_ENDPOINTS } from '@/lib/api/endpoints';

/**
 * Terminal Session Response
 * Matches backend FastAPI response structure
 */
export interface TerminalSessionResponse {
  session_id: string;
  container_id: string;
  ws_url: string;
  status: string;
  expires_at: string;
}

/**
 * Terminal Session API Response
 */
export interface TerminalSessionApiResponse {
  success: boolean;
  data: TerminalSessionResponse;
  meta?: {
    timestamp: string;
  };
}

/**
 * Terminal Session Deletion Response
 */
export interface TerminalSessionDeleteResponse {
  success: boolean;
  data: {
    session_id: string;
    terminated_at: string;
    duration_seconds: number;
  };
}

/**
 * Terminal API Service
 */
export const terminalApi = {
  /**
   * Create a new terminal session
   *
   * @returns Terminal session information including WebSocket URL
   * @throws Error if session creation fails
   */
  async createSession(): Promise<TerminalSessionResponse> {
    const response = await apiRequest<TerminalSessionApiResponse>({
      method: 'POST',
      url: API_ENDPOINTS.TERMINAL.CREATE_SESSION,
    });

    return response.data;
  },

  /**
   * Delete (terminate) an existing terminal session
   *
   * @param sessionId - The session ID to terminate
   * @returns Session termination information
   * @throws Error if session deletion fails
   */
  async deleteSession(sessionId: string): Promise<TerminalSessionDeleteResponse['data']> {
    const response = await apiRequest<TerminalSessionDeleteResponse>({
      method: 'DELETE',
      url: API_ENDPOINTS.TERMINAL.DESTROY(sessionId),
    });

    return response.data;
  },
};
