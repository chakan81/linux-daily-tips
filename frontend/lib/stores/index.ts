/**
 * Zustand Stores
 *
 * Centralized export for all Zustand stores used in the application.
 *
 * Store Types:
 * - themeStore: Theme and appearance settings (persisted)
 * - userStore: User authentication state (persisted)
 * - appStore: Transient UI state (not persisted)
 */

export { useThemeStore } from './themeStore';
export type { Theme } from './themeStore';

export { useUserStore } from './userStore';
export type { User, UserRole } from './userStore';

export { useAppStore } from './appStore';
