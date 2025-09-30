import { create } from 'zustand';
import { persist } from 'zustand/middleware';

/**
 * User role types
 */
export type UserRole = 'guest' | 'admin';

/**
 * User interface
 */
export interface User {
  id: string;
  email: string;
  role: UserRole;
  displayName?: string;
  avatarUrl?: string;
}

/**
 * User store state interface
 */
interface UserState {
  user: User | null;
  isAuthenticated: boolean;
  setUser: (user: User | null) => void;
  logout: () => void;
}

/**
 * User Store
 *
 * Manages user authentication state across the application.
 * Persisted to localStorage for maintaining login sessions.
 *
 * Usage:
 * ```tsx
 * const { user, isAuthenticated, setUser, logout } = useUserStore();
 * ```
 */
export const useUserStore = create<UserState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      setUser: (user) => set({ user, isAuthenticated: !!user }),
      logout: () => set({ user: null, isAuthenticated: false }),
    }),
    {
      name: 'user-storage',
    }
  )
);
