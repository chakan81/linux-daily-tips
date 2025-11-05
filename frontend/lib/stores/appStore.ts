import { create } from 'zustand';

/**
 * App-wide UI state interface
 */
interface AppState {
  // Sidebar state (for mobile navigation)
  isSidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;

  // Terminal state
  isTerminalOpen: boolean;
  setTerminalOpen: (open: boolean) => void;
  toggleTerminal: () => void;

  // Global loading state
  isGlobalLoading: boolean;
  setGlobalLoading: (loading: boolean) => void;
}

/**
 * App Store
 *
 * Manages global UI state that doesn't need persistence.
 * This is for transient UI states like sidebar visibility, modals, etc.
 *
 * Usage:
 * ```tsx
 * const { isSidebarOpen, toggleSidebar } = useAppStore();
 * ```
 */
export const useAppStore = create<AppState>((set) => ({
  isSidebarOpen: false,
  setSidebarOpen: (open) => set({ isSidebarOpen: open }),
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),

  isTerminalOpen: false,
  setTerminalOpen: (open) => set({ isTerminalOpen: open }),
  toggleTerminal: () => set((state) => ({ isTerminalOpen: !state.isTerminalOpen })),

  isGlobalLoading: false,
  setGlobalLoading: (loading) => set({ isGlobalLoading: loading }),
}));
