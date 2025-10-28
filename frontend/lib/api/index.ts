/**
 * API Module
 *
 * Centralized export for all API-related functionality.
 */

export { apiClient, apiRequest, handleApiError } from './client';
export type { ApiErrorResponse } from './client';

export { API_ENDPOINTS, buildUrl } from './endpoints';

// Terminal API
export {
  createTerminalSession,
  deleteTerminalSession,
  getWebSocketUrl,
} from './terminal';
export type { TerminalSessionResponse, CreateSessionRequest } from './terminal';

// Re-export specific API service modules (to be created as needed)
// export * from './services';
