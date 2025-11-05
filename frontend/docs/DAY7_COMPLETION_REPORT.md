# Day 7 완료 보고서: 상태 관리 및 데이터 페칭 설정

**작업일**: 2025-10-01
**상태**: ✅ 완료

---

## 목차
1. [개요](#개요)
2. [설치된 패키지](#설치된-패키지)
3. [생성된 파일 목록](#생성된-파일-목록)
4. [핵심 기능 구현](#핵심-기능-구현)
5. [사용법 예시](#사용법-예시)
6. [다음 단계](#다음-단계)

---

## 개요

Day 7에서는 프론트엔드 애플리케이션의 상태 관리 및 데이터 페칭 인프라를 완성했습니다. 다음 4가지 핵심 기능이 구현되었습니다:

1. **Zustand 상태 관리 시스템**
2. **React Query (TanStack Query) 데이터 페칭**
3. **Axios 기반 API 클라이언트**
4. **에러 바운더리 및 로딩 컴포넌트**

---

## 설치된 패키지

### 주요 의존성

| 패키지 | 버전 | 용도 |
|--------|------|------|
| `zustand` | 4.5.7 | 클라이언트 상태 관리 |
| `@tanstack/react-query` | 5.90.2 | 서버 상태 관리 |
| `@tanstack/react-query-devtools` | 5.90.2 | React Query 개발 도구 |
| `axios` | 1.12.2 | HTTP 클라이언트 |
| `react-hot-toast` | 2.4.1 | 토스트 알림 (이미 설치됨) |
| `next-themes` | 0.4.6 | 테마 관리 (이미 설치됨) |

### 호환성
- **React 19**: 모든 패키지가 React 19와 정상 작동
- **Next.js 15**: App Router와 완벽 호환
- **TypeScript 5.2**: 완전한 타입 안전성 보장

---

## 생성된 파일 목록

### 1. 상태 관리 (Zustand Stores)

```
lib/stores/
├── index.ts                 # 통합 export
├── themeStore.ts           # 테마 상태 관리
├── userStore.ts            # 사용자 인증 상태
└── appStore.ts             # 전역 UI 상태
```

**주요 기능**:
- LocalStorage 자동 영속화 (theme, user)
- TypeScript 타입 안전성
- 직관적인 hook 기반 API

### 2. API 클라이언트

```
lib/api/
├── index.ts                # 통합 export
├── client.ts               # Axios 인스턴스 및 설정
├── endpoints.ts            # API 엔드포인트 정의
└── services/
    └── index.ts            # 서비스 레이어 (향후 확장)
```

**주요 기능**:
- Request/Response Interceptors
- 자동 인증 토큰 관리
- 에러 처리 및 로깅
- 타입 안전한 엔드포인트 정의

### 3. React Query 설정

```
lib/providers/
├── index.ts                # 통합 export
└── QueryProvider.tsx       # React Query 설정
```

**주요 기능**:
- 캐시 전략 설정 (staleTime, gcTime)
- 자동 재시도 로직
- DevTools 통합 (개발 환경에만)

### 4. Custom Hooks

```
lib/hooks/
├── index.ts                # 통합 export
└── useTips.ts             # Tips 관련 React Query hooks
```

**포함된 Hooks**:
- `useTodayTip()` - 오늘의 팁
- `useRecentTips(limit)` - 최근 팁 목록
- `useTip(id)` - 특정 팁 조회
- `useTipsList(params)` - 페이지네이션 팁 목록
- `useSearchTips(query, filters)` - 팁 검색
- `useLikeTip()` - 팁 좋아요 (mutation 예시)

### 5. 에러 처리 및 로딩 컴포넌트

```
components/common/
├── index.ts                # 통합 export
├── ErrorBoundary.tsx       # React Error Boundary
├── LoadingSpinner.tsx      # 로딩 스피너 컴포넌트
└── ErrorMessage.tsx        # 에러 메시지 컴포넌트
```

**주요 기능**:
- ErrorBoundary: 전역 에러 처리
- LoadingSpinner: 다양한 크기 옵션 (sm, md, lg, xl)
- ErrorMessage: 4가지 타입 (error, warning, info, critical)
- 접근성 완벽 지원 (ARIA 속성)

### 6. 환경 변수 예시

```
frontend/
└── .env.local.example      # 환경 변수 템플릿
```

---

## 핵심 기능 구현

### 1. Zustand 상태 관리

#### Theme Store
```typescript
import { useThemeStore } from '@/lib/stores';

function ThemeToggle() {
  const { theme, setTheme } = useThemeStore();

  return (
    <button onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}>
      Toggle Theme
    </button>
  );
}
```

#### User Store
```typescript
import { useUserStore } from '@/lib/stores';

function UserProfile() {
  const { user, isAuthenticated, logout } = useUserStore();

  if (!isAuthenticated) return <Login />;

  return (
    <div>
      <p>Welcome, {user?.displayName}</p>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

#### App Store
```typescript
import { useAppStore } from '@/lib/stores';

function Sidebar() {
  const { isSidebarOpen, toggleSidebar } = useAppStore();

  return (
    <aside className={isSidebarOpen ? 'open' : 'closed'}>
      <button onClick={toggleSidebar}>Close</button>
      {/* Sidebar content */}
    </aside>
  );
}
```

### 2. React Query 데이터 페칭

#### Today's Tip
```typescript
import { useTodayTip } from '@/lib/hooks';
import { LoadingSpinner, ErrorMessage } from '@/components/common';

function TodayTipCard() {
  const { data: tip, isLoading, error } = useTodayTip();

  if (isLoading) return <LoadingSpinner size="lg" text="Loading today's tip..." />;
  if (error) return <ErrorMessage type="error" message={error.message} />;
  if (!tip) return <ErrorMessage type="info" message="No tip available today" />;

  return (
    <div className="tip-card">
      <h2>{tip.title}</h2>
      <p>{tip.description}</p>
      <code>{tip.command}</code>
    </div>
  );
}
```

#### Recent Tips with Pagination
```typescript
import { useRecentTips } from '@/lib/hooks';

function RecentTipsList() {
  const { data: tips, isLoading, error, refetch } = useRecentTips(10);

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage type="error" message={error.message} onRetry={refetch} />;

  return (
    <div>
      {tips?.map(tip => (
        <TipCard key={tip.id} tip={tip} />
      ))}
    </div>
  );
}
```

#### Search with Filters
```typescript
import { useState } from 'react';
import { useSearchTips } from '@/lib/hooks';

function TipSearch() {
  const [query, setQuery] = useState('');
  const { data: results, isLoading } = useSearchTips(query, {
    difficulty: 'Beginner',
    category: 'File Management'
  });

  return (
    <div>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search tips..."
      />
      {isLoading && <InlineLoader />}
      {results?.map(tip => <TipCard key={tip.id} tip={tip} />)}
    </div>
  );
}
```

#### Mutation Example (Like Tip)
```typescript
import { useLikeTip } from '@/lib/hooks';
import toast from 'react-hot-toast';

function TipLikeButton({ tipId }: { tipId: string }) {
  const { mutate: likeTip, isPending } = useLikeTip();

  const handleLike = () => {
    likeTip(tipId, {
      onSuccess: () => {
        toast.success('Tip liked!');
      },
      onError: (error) => {
        toast.error(`Failed to like: ${error.message}`);
      }
    });
  };

  return (
    <button onClick={handleLike} disabled={isPending}>
      {isPending ? <InlineLoader /> : '👍'} Like
    </button>
  );
}
```

### 3. API 클라이언트 사용법

#### 직접 API 호출
```typescript
import { apiRequest, API_ENDPOINTS, buildUrl } from '@/lib/api';

// GET 요청
async function fetchTips() {
  const tips = await apiRequest<TipData[]>({
    url: API_ENDPOINTS.TIPS.LIST,
    method: 'GET',
  });
  return tips;
}

// POST 요청 (인증 필요)
async function approveDraft(draftId: string) {
  return await apiRequest({
    url: API_ENDPOINTS.DRAFTS.APPROVE(draftId),
    method: 'POST',
  });
}

// 쿼리 파라미터 포함
async function searchTips(query: string) {
  return await apiRequest({
    url: buildUrl(API_ENDPOINTS.TIPS.SEARCH, { q: query, limit: 20 }),
  });
}
```

### 4. 에러 처리

#### Error Boundary
```typescript
import { ErrorBoundary } from '@/components/common';

function App() {
  return (
    <ErrorBoundary
      onError={(error, errorInfo) => {
        // Log to error reporting service
        console.error('App Error:', error, errorInfo);
      }}
    >
      <YourApp />
    </ErrorBoundary>
  );
}
```

#### Error Message Components
```typescript
import { ErrorMessage, InlineError } from '@/components/common';

// 전체 에러 메시지
<ErrorMessage
  type="error"
  title="Failed to load data"
  message="Could not connect to the server. Please try again."
  onRetry={() => refetch()}
  onDismiss={() => setError(null)}
/>

// 폼 인라인 에러
<InlineError message="This field is required" />
```

### 5. 로딩 상태

#### Loading Spinner Variants
```typescript
import { LoadingSpinner, FullPageLoader, InlineLoader } from '@/components/common';

// 일반 로딩
<LoadingSpinner size="md" text="Loading..." />

// 전체 페이지 로딩
<FullPageLoader text="Preparing your content..." />

// 버튼 내 인라인 로딩
<button disabled={isLoading}>
  {isLoading && <InlineLoader />}
  Submit
</button>
```

---

## 사용법 예시

### 완전한 페이지 예시

```typescript
'use client';

import { useTodayTip } from '@/lib/hooks';
import { LoadingSpinner, ErrorMessage } from '@/components/common';
import { useAppStore } from '@/lib/stores';

export default function TodayTipPage() {
  const { data: tip, isLoading, error, refetch } = useTodayTip();
  const { isGlobalLoading, setGlobalLoading } = useAppStore();

  if (isLoading || isGlobalLoading) {
    return (
      <div className="container py-12">
        <LoadingSpinner size="xl" text="Loading today's Linux tip..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="container py-12">
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
      <div className="container py-12">
        <ErrorMessage
          type="info"
          title="No tip available"
          message="Check back tomorrow for a new Linux tip!"
        />
      </div>
    );
  }

  return (
    <div className="container py-12">
      <article className="max-w-4xl mx-auto">
        <header>
          <h1 className="text-4xl font-bold mb-4">{tip.title}</h1>
          <div className="flex gap-2 mb-6">
            <span className="badge">{tip.difficulty}</span>
            <span className="badge">{tip.category}</span>
          </div>
        </header>

        <section className="prose dark:prose-invert">
          <p>{tip.description}</p>

          <div className="terminal-container">
            <pre><code>{tip.command}</code></pre>
          </div>

          {tip.explanation && (
            <div className="mt-6">
              <h3>Explanation</h3>
              <p>{tip.explanation}</p>
            </div>
          )}
        </section>
      </article>
    </div>
  );
}
```

---

## 설정 확인

### TypeScript 타입 체크
```bash
npm run type-check
```
**결과**: ✅ 에러 없음

### 개발 서버 실행
```bash
npm run dev
```
**결과**: ✅ 정상 동작 (http://localhost:3000)

### React Query DevTools
개발 모드에서 자동으로 활성화됩니다. 페이지 우측 하단에서 React Query 아이콘을 클릭하여 접근 가능합니다.

---

## 환경 변수 설정

### .env.local 생성
```bash
cp .env.local.example .env.local
```

### 필수 환경 변수
```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# API Timeout (optional)
NEXT_PUBLIC_API_TIMEOUT=30000

# Enable DevTools (optional)
NEXT_PUBLIC_ENABLE_DEVTOOLS=true
```

---

## 디렉토리 구조 (Day 7 후)

```
frontend/
├── app/
│   ├── layout.tsx                 # ✅ QueryProvider, ErrorBoundary 통합
│   ├── page.tsx
│   └── globals.css
├── components/
│   ├── common/                    # ✅ 새로 추가
│   │   ├── ErrorBoundary.tsx
│   │   ├── LoadingSpinner.tsx
│   │   ├── ErrorMessage.tsx
│   │   └── index.ts
│   ├── sections/
│   └── ui/
├── lib/
│   ├── api/                       # ✅ 새로 추가
│   │   ├── client.ts
│   │   ├── endpoints.ts
│   │   ├── index.ts
│   │   └── services/
│   ├── hooks/                     # ✅ 새로 추가
│   │   ├── useTips.ts
│   │   └── index.ts
│   ├── providers/                 # ✅ 새로 추가
│   │   ├── QueryProvider.tsx
│   │   └── index.ts
│   ├── stores/                    # ✅ 새로 추가
│   │   ├── themeStore.ts
│   │   ├── userStore.ts
│   │   ├── appStore.ts
│   │   └── index.ts
│   ├── types/
│   └── utils.ts
├── docs/                          # ✅ 새로 추가
│   └── DAY7_COMPLETION_REPORT.md
├── .env.local.example             # ✅ 새로 추가
├── package.json
└── tsconfig.json
```

---

## 성능 및 최적화

### React Query 캐싱 전략
- **staleTime**: 5분 (tips 데이터)
- **gcTime**: 10분 (가비지 컬렉션)
- **retry**: 1회 (실패 시 1번만 재시도)
- **refetchOnWindowFocus**: 프로덕션에만 활성화

### Zustand 영속화
- **themeStore**: localStorage에 자동 저장
- **userStore**: localStorage에 자동 저장 (보안 강화 필요)
- **appStore**: 메모리에만 저장 (일시적 UI 상태)

### 번들 크기
- **Zustand**: ~1.2KB (gzipped)
- **React Query**: ~14KB (gzipped)
- **Axios**: ~13KB (gzipped)

총 증가: ~28KB (매우 효율적)

---

## 다음 단계 (Week 2: 백엔드 연동 준비)

### Day 8-9: 백엔드 API 구현
1. **FastAPI 서버 설정**
   - PostgreSQL 연동
   - Tips CRUD API 구현
   - 인증 시스템 구축

2. **API 통합 테스트**
   - Frontend ↔ Backend 연동 검증
   - API 엔드포인트 동기화
   - 에러 처리 개선

### Day 10-11: Terminal Emulator 구현
1. **xterm.js 통합**
   - 웹 터미널 컴포넌트 구현
   - WebSocket 연결 설정
   - 터미널 세션 관리

2. **Sandbox 환경 구축**
   - Docker 기반 터미널 환경
   - 보안 격리 (chroot, resource limits)
   - 세션 타임아웃 관리

### Day 12-14: LLM 연동
1. **OpenAI/Claude API 통합**
   - 주간 Draft 자동 생성
   - 난이도 분류 자동화
   - 카테고리 태깅

2. **관리자 승인 워크플로우**
   - Draft 관리 페이지
   - 승인/거절 인터페이스
   - 일정 관리 시스템

---

## 참고 자료

### 공식 문서
- [Zustand Documentation](https://docs.pmnd.rs/zustand/getting-started/introduction)
- [TanStack Query Documentation](https://tanstack.com/query/latest/docs/react/overview)
- [Axios Documentation](https://axios-http.com/docs/intro)
- [Next.js App Router](https://nextjs.org/docs/app)

### 프로젝트 문서
- [Frontend CLAUDE.md](/frontend/CLAUDE.md) - 프론트엔드 가이드
- [프로젝트 요구사항](/docs/requirements.md) - 전체 시스템 요구사항
- [루트 CLAUDE.md](/CLAUDE.md) - 프로젝트 개요

---

## 완료 체크리스트

- [x] **Zustand 설치 및 설정**
  - [x] themeStore 구현
  - [x] userStore 구현
  - [x] appStore 구현
  - [x] TypeScript 타입 정의

- [x] **React Query 설정**
  - [x] QueryProvider 구현
  - [x] DevTools 통합
  - [x] 기본 쿼리 옵션 설정

- [x] **API 클라이언트 구현**
  - [x] Axios 인스턴스 생성
  - [x] Request/Response Interceptors
  - [x] 에러 처리 로직
  - [x] API 엔드포인트 정의

- [x] **Custom Hooks 작성**
  - [x] useTodayTip
  - [x] useRecentTips
  - [x] useTip
  - [x] useTipsList
  - [x] useSearchTips
  - [x] useLikeTip (mutation 예시)

- [x] **에러 처리 컴포넌트**
  - [x] ErrorBoundary
  - [x] ErrorMessage
  - [x] InlineError

- [x] **로딩 컴포넌트**
  - [x] LoadingSpinner
  - [x] FullPageLoader
  - [x] InlineLoader

- [x] **환경 변수 설정**
  - [x] .env.local.example 생성
  - [x] API_URL 설정

- [x] **Layout 통합**
  - [x] QueryProvider 추가
  - [x] ErrorBoundary 추가
  - [x] Toaster 설정

- [x] **TypeScript 타입 체크**
  - [x] 모든 파일 타입 에러 없음

- [x] **문서화**
  - [x] 완료 보고서 작성
  - [x] 사용법 예시 추가
  - [x] 다음 단계 계획

---

## 요약

Day 7에서 구현된 상태 관리 및 데이터 페칭 시스템은 다음과 같은 장점을 제공합니다:

### 주요 장점
1. **타입 안전성**: 모든 코드에 TypeScript 타입 정의
2. **확장성**: 쉽게 새로운 store/hook 추가 가능
3. **성능**: 효율적인 캐싱 및 재사용
4. **개발자 경험**: DevTools, 에러 처리, 로딩 상태 완벽 지원
5. **유지보수성**: 명확한 파일 구조 및 문서화

### 준비 완료 사항
- ✅ 백엔드 API 연동 준비 완료
- ✅ 실시간 데이터 페칭 시스템
- ✅ 전역 상태 관리 인프라
- ✅ 에러 처리 및 사용자 피드백 시스템

**Day 7 작업이 성공적으로 완료되었습니다!** 🎉

이제 Week 2로 넘어가 백엔드 API와 통합할 준비가 되었습니다.
