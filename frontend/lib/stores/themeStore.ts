import { create } from 'zustand';
import { persist } from 'zustand/middleware';

/**
 * Theme types
 */
export type Theme = 'light' | 'dark' | 'system';

/**
 * Theme store state interface
 */
interface ThemeState {
  theme: Theme;
  resolvedTheme: 'light' | 'dark';
  setTheme: (theme: Theme) => void;
  setResolvedTheme: (theme: 'light' | 'dark') => void;
}

/**
 * Theme Store
 *
 * Manages theme state across the application.
 * Persisted to localStorage for consistency across sessions.
 *
 * Usage:
 * ```tsx
 * const { theme, setTheme } = useThemeStore();
 * ```
 */
export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      theme: 'system',
      resolvedTheme: 'light',
      setTheme: (theme) => set({ theme }),
      setResolvedTheme: (resolvedTheme) => set({ resolvedTheme }),
    }),
    {
      name: 'theme-storage',
    }
  )
);
