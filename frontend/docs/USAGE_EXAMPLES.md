# Day 7 기능 사용 예시

이 문서는 Day 7에서 구현된 상태 관리 및 데이터 페칭 기능의 실전 사용 예시를 제공합니다.

---

## 목차
1. [Zustand Stores](#zustand-stores)
2. [React Query Hooks](#react-query-hooks)
3. [API Client](#api-client)
4. [Error Handling](#error-handling)
5. [Loading States](#loading-states)
6. [Complete Page Examples](#complete-page-examples)

---

## Zustand Stores

### 1. Theme Store (테마 관리)

```typescript
'use client';

import { useThemeStore } from '@/lib/stores';
import { Moon, Sun, Monitor } from 'lucide-react';

export function ThemeToggle() {
  const { theme, setTheme } = useThemeStore();

  return (
    <div className="flex gap-2">
      <button
        onClick={() => setTheme('light')}
        className={`p-2 rounded ${theme === 'light' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
      >
        <Sun className="w-4 h-4" />
      </button>
      <button
        onClick={() => setTheme('dark')}
        className={`p-2 rounded ${theme === 'dark' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
      >
        <Moon className="w-4 h-4" />
      </button>
      <button
        onClick={() => setTheme('system')}
        className={`p-2 rounded ${theme === 'system' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
      >
        <Monitor className="w-4 h-4" />
      </button>
    </div>
  );
}
```

### 2. User Store (사용자 인증)

```typescript
'use client';

import { useUserStore } from '@/lib/stores';
import { useEffect } from 'react';
import { LogOut, User } from 'lucide-react';

export function UserProfile() {
  const { user, isAuthenticated, setUser, logout } = useUserStore();

  useEffect(() => {
    // 페이지 로드 시 토큰 확인
    const token = localStorage.getItem('auth-token');
    if (token && !isAuthenticated) {
      // 토큰으로 사용자 정보 가져오기
      fetchUserInfo(token).then(setUser);
    }
  }, []);

  if (!isAuthenticated) {
    return (
      <button className="btn-primary">
        <User className="w-4 h-4" />
        Login
      </button>
    );
  }

  return (
    <div className="flex items-center gap-3">
      <img
        src={user?.avatarUrl || '/default-avatar.png'}
        alt={user?.displayName}
        className="w-8 h-8 rounded-full"
      />
      <span className="text-sm font-medium">{user?.displayName}</span>
      <button onClick={logout} className="btn-secondary">
        <LogOut className="w-4 h-4" />
      </button>
    </div>
  );
}

async function fetchUserInfo(token: string) {
  // API 호출 로직
  return null;
}
```

### 3. App Store (UI 상태)

```typescript
'use client';

import { useAppStore } from '@/lib/stores';
import { Menu, X } from 'lucide-react';

export function MobileMenu() {
  const { isSidebarOpen, toggleSidebar } = useAppStore();

  return (
    <>
      {/* 모바일 메뉴 버튼 */}
      <button onClick={toggleSidebar} className="md:hidden">
        <Menu className="w-6 h-6" />
      </button>

      {/* 사이드바 */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-900 transform transition-transform ${
          isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="p-4">
          <button onClick={toggleSidebar} className="mb-4">
            <X className="w-6 h-6" />
          </button>
          <nav>
            <ul className="space-y-2">
              <li><a href="/">Home</a></li>
              <li><a href="/tips">Tips</a></li>
              <li><a href="/terminal">Terminal</a></li>
              <li><a href="/admin">Admin</a></li>
            </ul>
          </nav>
        </div>
      </aside>

      {/* 오버레이 */}
      {isSidebarOpen && (
        <div
          onClick={toggleSidebar}
          className="fixed inset-0 bg-black/50 z-40"
        />
      )}
    </>
  );
}
```

---

## React Query Hooks

### 1. Today's Tip (단일 데이터 조회)

```typescript
'use client';

import { useTodayTip } from '@/lib/hooks';
import { LoadingSpinner, ErrorMessage } from '@/components/common';
import { Terminal } from 'lucide-react';

export function TodayTipCard() {
  const { data: tip, isLoading, error, refetch } = useTodayTip();

  if (isLoading) {
    return (
      <div className="card p-8">
        <LoadingSpinner size="lg" text="Loading today's tip..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="card p-8">
        <ErrorMessage
          type="error"
          title="Failed to load tip"
          message={error.message}
          onRetry={refetch}
        />
      </div>
    );
  }

  if (!tip) {
    return (
      <div className="card p-8">
        <ErrorMessage
          type="info"
          message="No tip available today. Check back tomorrow!"
        />
      </div>
    );
  }

  return (
    <div className="card p-8">
      <div className="flex items-center gap-2 mb-4">
        <Terminal className="w-5 h-5 text-blue-600" />
        <h2 className="text-2xl font-bold">{tip.title}</h2>
      </div>

      <div className="flex gap-2 mb-4">
        <span className="badge badge-blue">{tip.difficulty}</span>
        <span className="badge badge-gray">{tip.category}</span>
      </div>

      <p className="text-gray-700 dark:text-gray-300 mb-6">
        {tip.description}
      </p>

      <div className="terminal-container">
        <pre><code>{tip.command}</code></pre>
      </div>

      {tip.explanation && (
        <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <h3 className="font-semibold mb-2">Explanation:</h3>
          <p className="text-sm">{tip.explanation}</p>
        </div>
      )}
    </div>
  );
}
```

### 2. Recent Tips (리스트 조회)

```typescript
'use client';

import { useRecentTips } from '@/lib/hooks';
import { LoadingSpinner, ErrorMessage } from '@/components/common';
import Link from 'next/link';
import { Calendar, TrendingUp } from 'lucide-react';

export function RecentTipsList({ limit = 5 }: { limit?: number }) {
  const { data: tips, isLoading, error } = useRecentTips(limit);

  if (isLoading) {
    return <LoadingSpinner size="md" text="Loading recent tips..." />;
  }

  if (error) {
    return (
      <ErrorMessage
        type="error"
        message="Failed to load recent tips"
      />
    );
  }

  if (!tips || tips.length === 0) {
    return (
      <ErrorMessage
        type="info"
        message="No tips available yet"
      />
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-4">
        <TrendingUp className="w-5 h-5 text-blue-600" />
        <h3 className="text-xl font-bold">Recent Tips</h3>
      </div>

      {tips.map(tip => (
        <Link
          key={tip.id}
          href={`/tips/${tip.id}`}
          className="block card p-4 hover:shadow-lg transition-shadow"
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h4 className="font-semibold mb-1">{tip.title}</h4>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                {tip.description.substring(0, 100)}...
              </p>
              <div className="flex gap-2">
                <span className="badge badge-sm">{tip.difficulty}</span>
                <span className="badge badge-sm">{tip.category}</span>
              </div>
            </div>
            <div className="flex items-center gap-1 text-sm text-gray-500">
              <Calendar className="w-4 h-4" />
              {new Date(tip.publishedAt).toLocaleDateString()}
            </div>
          </div>
        </Link>
      ))}
    </div>
  );
}
```

### 3. Search Tips (검색 + 필터)

```typescript
'use client';

import { useState } from 'react';
import { useSearchTips } from '@/lib/hooks';
import { LoadingSpinner, InlineError } from '@/components/common';
import { Search, Filter } from 'lucide-react';
import type { DifficultyLevel, TipCategory } from '@/lib/types';

export function TipSearchBar() {
  const [query, setQuery] = useState('');
  const [difficulty, setDifficulty] = useState<DifficultyLevel | ''>('');
  const [category, setCategory] = useState<TipCategory | ''>('');

  const { data: results, isLoading, error } = useSearchTips(query, {
    ...(difficulty && { difficulty }),
    ...(category && { category }),
  });

  return (
    <div className="space-y-4">
      {/* 검색 입력 */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search Linux tips..."
          className="input pl-10"
        />
        {isLoading && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            <LoadingSpinner size="sm" />
          </div>
        )}
      </div>

      {/* 필터 */}
      <div className="flex gap-3">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-gray-500" />
          <select
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value as DifficultyLevel)}
            className="select"
          >
            <option value="">All Levels</option>
            <option value="Beginner">Beginner</option>
            <option value="Intermediate">Intermediate</option>
            <option value="Advanced">Advanced</option>
          </select>
        </div>

        <select
          value={category}
          onChange={(e) => setCategory(e.target.value as TipCategory)}
          className="select"
        >
          <option value="">All Categories</option>
          <option value="File Management">File Management</option>
          <option value="System Monitoring">System Monitoring</option>
          <option value="Process Management">Process Management</option>
          <option value="Networking">Networking</option>
          <option value="Text Processing">Text Processing</option>
        </select>
      </div>

      {/* 결과 */}
      {error && <InlineError message={error.message} />}

      {results && results.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm text-gray-600">
            Found {results.length} results
          </p>
          {results.map(tip => (
            <TipCard key={tip.id} tip={tip} />
          ))}
        </div>
      )}

      {results && results.length === 0 && (
        <p className="text-center text-gray-500 py-8">
          No tips found. Try a different search term.
        </p>
      )}
    </div>
  );
}
```

### 4. Mutation Example (데이터 수정)

```typescript
'use client';

import { useLikeTip } from '@/lib/hooks';
import { useState } from 'react';
import { Heart } from 'lucide-react';
import { InlineLoader } from '@/components/common';
import toast from 'react-hot-toast';

export function TipLikeButton({ tipId, initialLikes = 0 }: {
  tipId: string;
  initialLikes?: number;
}) {
  const [likes, setLikes] = useState(initialLikes);
  const [isLiked, setIsLiked] = useState(false);

  const { mutate: likeTip, isPending } = useLikeTip();

  const handleLike = () => {
    if (isLiked) {
      toast.error('You already liked this tip');
      return;
    }

    likeTip(tipId, {
      onSuccess: () => {
        setLikes(prev => prev + 1);
        setIsLiked(true);
        toast.success('Thanks for liking this tip!');
      },
      onError: (error) => {
        toast.error(`Failed to like: ${error.message}`);
      }
    });
  };

  return (
    <button
      onClick={handleLike}
      disabled={isPending || isLiked}
      className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
        isLiked
          ? 'bg-red-100 text-red-600 cursor-not-allowed'
          : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
      }`}
    >
      {isPending ? (
        <InlineLoader />
      ) : (
        <Heart className={`w-4 h-4 ${isLiked ? 'fill-current' : ''}`} />
      )}
      <span>{likes}</span>
    </button>
  );
}
```

---

## API Client

### 직접 API 호출

```typescript
import { apiRequest, API_ENDPOINTS, buildUrl } from '@/lib/api';
import type { TipData } from '@/lib/types';

// 1. 간단한 GET 요청
export async function fetchAllTips() {
  try {
    const tips = await apiRequest<TipData[]>({
      url: API_ENDPOINTS.TIPS.LIST,
      method: 'GET',
    });
    return tips;
  } catch (error) {
    console.error('Failed to fetch tips:', error);
    throw error;
  }
}

// 2. 쿼리 파라미터 포함
export async function fetchTipsByCategory(category: string, limit: number = 10) {
  const url = buildUrl(API_ENDPOINTS.TIPS.BY_CATEGORY(category), { limit });
  return await apiRequest<TipData[]>({ url });
}

// 3. POST 요청 (인증 필요)
export async function approveDraft(draftId: string, notes?: string) {
  return await apiRequest({
    url: API_ENDPOINTS.DRAFTS.APPROVE(draftId),
    method: 'POST',
    data: { notes },
  });
}

// 4. 복잡한 검색 쿼리
export async function searchTipsAdvanced(params: {
  query: string;
  difficulty?: string;
  category?: string;
  page?: number;
  limit?: number;
}) {
  const url = buildUrl(API_ENDPOINTS.TIPS.SEARCH, params);
  return await apiRequest<{ tips: TipData[]; total: number }>({ url });
}
```

---

## Error Handling

### 1. Error Boundary 사용

```typescript
'use client';

import { ErrorBoundary } from '@/components/common';
import { AlertTriangle } from 'lucide-react';

export default function TipsPage() {
  return (
    <ErrorBoundary
      fallback={
        <div className="container py-12 text-center">
          <AlertTriangle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h1 className="text-2xl font-bold mb-2">Page Error</h1>
          <p className="text-gray-600">
            This page encountered an error. Please refresh or go back.
          </p>
        </div>
      }
      onError={(error, errorInfo) => {
        // Send to error tracking service
        console.error('Page Error:', error, errorInfo);
      }}
    >
      <TipsContent />
    </ErrorBoundary>
  );
}
```

### 2. Error Message Variants

```typescript
import { ErrorMessage, InlineError } from '@/components/common';

export function ErrorExamples() {
  return (
    <div className="space-y-4">
      {/* 일반 에러 */}
      <ErrorMessage
        type="error"
        title="Connection Failed"
        message="Could not connect to the server."
        onRetry={() => console.log('Retry')}
      />

      {/* 경고 */}
      <ErrorMessage
        type="warning"
        title="Limited Access"
        message="Some features are not available in demo mode."
      />

      {/* 정보 */}
      <ErrorMessage
        type="info"
        title="New Update Available"
        message="A new version is available. Please refresh the page."
      />

      {/* 심각한 에러 */}
      <ErrorMessage
        type="critical"
        title="System Error"
        message="A critical error occurred. Please contact support."
      />

      {/* 폼 인라인 에러 */}
      <div>
        <label>Email</label>
        <input type="email" className="input" />
        <InlineError message="Please enter a valid email address" />
      </div>
    </div>
  );
}
```

---

## Loading States

### 1. Loading Spinner Variants

```typescript
import {
  LoadingSpinner,
  FullPageLoader,
  InlineLoader
} from '@/components/common';

export function LoadingExamples() {
  return (
    <div className="space-y-8">
      {/* 작은 스피너 */}
      <LoadingSpinner size="sm" />

      {/* 중간 스피너 */}
      <LoadingSpinner size="md" text="Loading..." />

      {/* 큰 스피너 */}
      <LoadingSpinner size="lg" text="Please wait..." />

      {/* 매우 큰 스피너 */}
      <LoadingSpinner size="xl" text="Preparing your content..." />

      {/* 전체 페이지 로딩 */}
      {showFullPageLoader && (
        <FullPageLoader text="Loading application..." />
      )}

      {/* 버튼 내 인라인 로딩 */}
      <button className="btn-primary" disabled>
        <InlineLoader className="mr-2" />
        Processing...
      </button>
    </div>
  );
}
```

---

## Complete Page Examples

### 1. Tips List Page

```typescript
'use client';

import { useTipsList } from '@/lib/hooks';
import { useState } from 'react';
import { LoadingSpinner, ErrorMessage } from '@/components/common';
import { ChevronLeft, ChevronRight } from 'lucide-react';

export default function TipsListPage() {
  const [page, setPage] = useState(1);
  const limit = 20;

  const { data, isLoading, error, refetch } = useTipsList({ page, limit });

  if (isLoading) {
    return (
      <div className="container py-12">
        <LoadingSpinner size="xl" text="Loading tips..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="container py-12">
        <ErrorMessage
          type="error"
          title="Failed to load tips"
          message={error.message}
          onRetry={refetch}
        />
      </div>
    );
  }

  const { tips, total } = data || { tips: [], total: 0 };
  const totalPages = Math.ceil(total / limit);

  return (
    <div className="container py-12">
      <header className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Linux Tips</h1>
        <p className="text-gray-600">
          Browse all {total} tips to improve your Linux skills
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {tips.map(tip => (
          <TipCard key={tip.id} tip={tip} />
        ))}
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-center gap-4 mt-12">
        <button
          onClick={() => setPage(p => Math.max(1, p - 1))}
          disabled={page === 1}
          className="btn-secondary"
        >
          <ChevronLeft className="w-4 h-4" />
          Previous
        </button>

        <span className="text-sm text-gray-600">
          Page {page} of {totalPages}
        </span>

        <button
          onClick={() => setPage(p => Math.min(totalPages, p + 1))}
          disabled={page === totalPages}
          className="btn-secondary"
        >
          Next
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
```

### 2. Tip Detail Page

```typescript
'use client';

import { useTip } from '@/lib/hooks';
import { useParams } from 'next/navigation';
import { LoadingSpinner, ErrorMessage } from '@/components/common';
import { Calendar, Tag, TrendingUp } from 'lucide-react';

export default function TipDetailPage() {
  const params = useParams();
  const tipId = params?.id as string;

  const { data: tip, isLoading, error, refetch } = useTip(tipId);

  if (isLoading) {
    return (
      <div className="container py-12">
        <LoadingSpinner size="xl" text="Loading tip..." />
      </div>
    );
  }

  if (error || !tip) {
    return (
      <div className="container py-12">
        <ErrorMessage
          type="error"
          title="Tip not found"
          message="The requested tip could not be found."
          onRetry={refetch}
        />
      </div>
    );
  }

  return (
    <div className="container py-12">
      <article className="max-w-4xl mx-auto">
        {/* Header */}
        <header className="mb-8">
          <div className="flex items-center gap-2 mb-4">
            <span className="badge badge-blue">{tip.difficulty}</span>
            <span className="badge badge-gray">{tip.category}</span>
          </div>

          <h1 className="text-4xl font-bold mb-4">{tip.title}</h1>

          <div className="flex items-center gap-4 text-sm text-gray-600">
            <div className="flex items-center gap-1">
              <Calendar className="w-4 h-4" />
              {new Date(tip.publishedAt).toLocaleDateString()}
            </div>
            <div className="flex items-center gap-1">
              <Tag className="w-4 h-4" />
              {tip.category}
            </div>
            <div className="flex items-center gap-1">
              <TrendingUp className="w-4 h-4" />
              {tip.difficulty}
            </div>
          </div>
        </header>

        {/* Content */}
        <div className="prose dark:prose-invert max-w-none">
          <p className="text-lg">{tip.description}</p>

          {/* Command */}
          <div className="terminal-container my-8">
            <div className="terminal-header">
              <span>bash</span>
            </div>
            <pre><code>{tip.command}</code></pre>
          </div>

          {/* Explanation */}
          {tip.explanation && (
            <section className="my-8">
              <h2>Explanation</h2>
              <p>{tip.explanation}</p>
            </section>
          )}

          {/* Example Output */}
          {tip.exampleOutput && (
            <section className="my-8">
              <h2>Example Output</h2>
              <div className="terminal-container">
                <pre><code>{tip.exampleOutput}</code></pre>
              </div>
            </section>
          )}

          {/* Related Commands */}
          {tip.relatedCommands && tip.relatedCommands.length > 0 && (
            <section className="my-8">
              <h2>Related Commands</h2>
              <ul>
                {tip.relatedCommands.map((cmd, idx) => (
                  <li key={idx}>
                    <code>{cmd}</code>
                  </li>
                ))}
              </ul>
            </section>
          )}
        </div>

        {/* Actions */}
        <footer className="mt-12 pt-8 border-t">
          <div className="flex items-center justify-between">
            <TipLikeButton tipId={tip.id} />
            <button className="btn-secondary">
              Share
            </button>
          </div>
        </footer>
      </article>
    </div>
  );
}
```

---

## Best Practices

### 1. Always Handle Loading & Error States
```typescript
const { data, isLoading, error } = useQuery(...);

// ✅ Good: Handle all states
if (isLoading) return <LoadingSpinner />;
if (error) return <ErrorMessage message={error.message} />;
if (!data) return <ErrorMessage message="No data" />;

// ❌ Bad: Only handle success case
return <div>{data.title}</div>;
```

### 2. Use Type Safety
```typescript
// ✅ Good: Typed API response
const { data } = useTodayTip(); // data: TipData | undefined

// ❌ Bad: Untyped response
const response = await fetch('/api/tips/today');
const data = await response.json(); // data: any
```

### 3. Optimize Re-renders
```typescript
// ✅ Good: Selective subscription
const { theme } = useThemeStore();

// ❌ Bad: Subscribe to entire store
const store = useThemeStore();
return <div>{store.theme}</div>;
```

### 4. Error Recovery
```typescript
// ✅ Good: Provide retry option
<ErrorMessage
  message={error.message}
  onRetry={() => refetch()}
/>

// ❌ Bad: No recovery path
<ErrorMessage message={error.message} />
```

---

이 예시들은 Day 7에서 구현된 모든 기능을 실전에서 사용하는 방법을 보여줍니다. 각 예시는 프로덕션 준비가 된 코드로, 바로 프로젝트에 적용할 수 있습니다.
