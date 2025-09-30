# Day 7: State Management & Data Fetching Setup Guide

## Overview

Day 7에서는 Linux Daily Tips 프론트엔드에 상태 관리 및 데이터 페칭 시스템을 구축했습니다.

## Installed Packages

### Production Dependencies (이미 설치됨)
- `zustand@4.4.6` - 클라이언트 상태 관리
- `@tanstack/react-query@5.59.20` - 서버 상태 관리
- `axios@1.6.0` - HTTP 클라이언트

### Development Dependencies (신규 설치)
- `@tanstack/react-query-devtools@5.90.2` - React Query 개발자 도구

## Project Structure

```
frontend/
├── lib/
│   ├── stores/                     # Zustand Stores
│   │   ├── themeStore.ts          # Theme state (persisted)
│   │   ├── userStore.ts           # User authentication state (persisted)
│   │   ├── appStore.ts            # UI state (transient)
│   │   └── index.ts               # Store exports
│   │
│   ├── api/                        # API Client
│   │   ├── client.ts              # Axios configuration & interceptors
│   │   ├── endpoints.ts           # API endpoint definitions
│   │   ├── services/              # API service modules (future)
│   │   └── index.ts               # API exports
│   │
│   ├── providers/                  # React Providers
│   │   ├── QueryProvider.tsx      # React Query provider
│   │   └── index.ts               # Provider exports
│   │
│   └── hooks/                      # Custom Hooks
│       ├── useTips.ts             # Tips-related hooks
│       └── index.ts               # Hook exports
│
├── components/
│   └── common/                     # Common Components
│       ├── ErrorBoundary.tsx      # Error boundary component
│       ├── LoadingSpinner.tsx     # Loading spinner variants
│       ├── ErrorMessage.tsx       # Error message component
│       └── index.ts               # Common component exports
│
└── .env.local.example              # Environment variables template
```

## Usage Examples

### 1. Zustand Stores

#### Theme Store (Persisted)
```tsx
'use client';

import { useThemeStore } from '@/lib/stores';

export function ThemeToggle() {
  const { theme, setTheme } = useThemeStore();

  return (
    <button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>
      Toggle Theme: {theme}
    </button>
  );
}
```

#### User Store (Persisted)
```tsx
'use client';

import { useUserStore } from '@/lib/stores';

export function UserProfile() {
  const { user, isAuthenticated, setUser, logout } = useUserStore();

  if (!isAuthenticated) {
    return <div>Please login</div>;
  }

  return (
    <div>
      <h2>Welcome, {user?.displayName}</h2>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

#### App Store (Transient UI State)
```tsx
'use client';

import { useAppStore } from '@/lib/stores';

export function Sidebar() {
  const { isSidebarOpen, toggleSidebar } = useAppStore();

  return (
    <aside className={isSidebarOpen ? 'open' : 'closed'}>
      <button onClick={toggleSidebar}>Close</button>
      {/* Sidebar content */}
    </aside>
  );
}
```

### 2. React Query Hooks

#### Fetching Today's Tip
```tsx
'use client';

import { useTodayTip } from '@/lib/hooks';
import { LoadingSpinner, ErrorMessage } from '@/components/common';

export function TodayTipSection() {
  const { data: tip, isLoading, error } = useTodayTip();

  if (isLoading) {
    return <LoadingSpinner text="Loading today's tip..." />;
  }

  if (error) {
    return (
      <ErrorMessage
        type="error"
        title="Failed to load tip"
        message={error.message}
        onRetry={() => window.location.reload()}
      />
    );
  }

  return (
    <div>
      <h2>{tip?.title}</h2>
      <p>{tip?.description}</p>
    </div>
  );
}
```

#### Searching Tips
```tsx
'use client';

import { useState } from 'react';
import { useSearchTips } from '@/lib/hooks';

export function TipSearch() {
  const [query, setQuery] = useState('');
  const { data: tips, isLoading, error } = useSearchTips(query, {
    difficulty: 'Beginner',
  });

  return (
    <div>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search tips..."
      />

      {isLoading && <LoadingSpinner />}

      {tips?.map((tip) => (
        <div key={tip.id}>
          <h3>{tip.title}</h3>
        </div>
      ))}
    </div>
  );
}
```

### 3. API Client Direct Usage

```tsx
import { apiRequest, API_ENDPOINTS } from '@/lib/api';
import type { TipData } from '@/lib/types';

// Direct API call (use React Query hooks instead when possible)
async function fetchTipById(id: string): Promise<TipData> {
  try {
    const tip = await apiRequest<TipData>({
      url: API_ENDPOINTS.TIPS.BY_ID(id),
      method: 'GET',
    });
    return tip;
  } catch (error) {
    console.error('Failed to fetch tip:', error);
    throw error;
  }
}
```

### 4. Error Boundary Usage

```tsx
import { ErrorBoundary } from '@/components/common';

export default function MyPage() {
  return (
    <ErrorBoundary
      onError={(error, errorInfo) => {
        // Log to error reporting service
        console.error('Error caught:', error, errorInfo);
      }}
    >
      <YourComponent />
    </ErrorBoundary>
  );
}
```

### 5. Loading Components

```tsx
import {
  LoadingSpinner,
  FullPageLoader,
  InlineLoader
} from '@/components/common';

// Standard loading spinner
<LoadingSpinner size="md" text="Loading..." />

// Full page loader
<FullPageLoader text="Initializing application..." />

// Inline loader (for buttons)
<button disabled>
  <InlineLoader className="mr-2" />
  Saving...
</button>
```

## Environment Variables

Create `.env.local` from `.env.local.example`:

```bash
cp .env.local.example .env.local
```

Required variables:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Development Workflow

### 1. Start Development Server
```bash
npm run dev
```

### 2. Access React Query DevTools
- Open your app at http://localhost:3000
- Look for the React Query DevTools button in the bottom-right corner (development only)
- Click to inspect queries, mutations, and cache

### 3. Type Checking
```bash
npm run type-check
```

### 4. Build for Production
```bash
npm run build
```

## Key Features

### React Query Configuration
- **Stale Time**: 5 minutes (data is considered fresh for 5 minutes)
- **Cache Time**: 10 minutes (inactive queries are removed after 10 minutes)
- **Retry**: 1 attempt with exponential backoff
- **Refetch on Window Focus**: Production only
- **DevTools**: Development only

### API Client Features
- **Base URL**: Configurable via environment variables
- **Timeout**: 30 seconds default
- **Authentication**: Auto-injects JWT token from localStorage
- **Request Logging**: Development environment only
- **Error Handling**: Centralized error processing
- **Interceptors**: Request/response interceptors for auth and logging

### Zustand Stores
- **themeStore**: Persisted to localStorage
- **userStore**: Persisted to localStorage
- **appStore**: Transient (not persisted)

## Best Practices

### 1. Use React Query for Server State
```tsx
// ✅ Good
const { data, isLoading } = useTodayTip();

// ❌ Avoid
const [data, setData] = useState(null);
useEffect(() => { fetchData().then(setData); }, []);
```

### 2. Use Zustand for Client State
```tsx
// ✅ Good
const { isSidebarOpen, toggleSidebar } = useAppStore();

// ❌ Avoid passing UI state through props multiple levels
```

### 3. Centralize API Endpoints
```tsx
// ✅ Good
import { API_ENDPOINTS } from '@/lib/api';
const url = API_ENDPOINTS.TIPS.BY_ID(id);

// ❌ Avoid hardcoding URLs
const url = `/api/tips/${id}`;
```

### 4. Handle Errors Gracefully
```tsx
// ✅ Good
if (error) {
  return <ErrorMessage message={error.message} onRetry={refetch} />;
}

// ❌ Avoid silent failures
if (error) return null;
```

## Next Steps (Week 2)

1. **Backend Integration**: Connect to actual FastAPI backend
2. **Authentication Flow**: Implement login/logout with JWT
3. **Create Service Modules**:
   - `lib/api/services/tipsService.ts`
   - `lib/api/services/authService.ts`
   - `lib/api/services/draftsService.ts`
4. **Additional Hooks**:
   - `useAuth()` for authentication
   - `useStats()` for statistics
   - `useDrafts()` for draft management
5. **Mutations**: Implement create/update/delete operations
6. **Optimistic Updates**: Add optimistic UI updates for better UX

## Troubleshooting

### Issue: Peer Dependency Conflicts
**Solution**: Use `--legacy-peer-deps` flag
```bash
npm install <package> --legacy-peer-deps
```

### Issue: Query Not Refetching
**Solution**: Check `staleTime` and `enabled` options
```tsx
const { data } = useQuery({
  queryKey: ['tips'],
  queryFn: fetchTips,
  staleTime: 1000 * 60 * 5, // 5 minutes
  enabled: true, // ensure query is enabled
});
```

### Issue: Store State Not Persisting
**Solution**: Ensure `persist` middleware is used
```tsx
export const useStore = create<State>()(
  persist(
    (set) => ({ /* state */ }),
    { name: 'storage-key' }
  )
);
```

## References

- [React Query Documentation](https://tanstack.com/query/latest/docs/react/overview)
- [Zustand Documentation](https://docs.pmnd.rs/zustand/getting-started/introduction)
- [Axios Documentation](https://axios-http.com/docs/intro)
- [Next.js Documentation](https://nextjs.org/docs)

---

**Day 7 Complete!** 🎉

State management and data fetching infrastructure is now ready for Week 2 backend integration.
