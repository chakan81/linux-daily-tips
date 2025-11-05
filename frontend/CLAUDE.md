# Frontend Development Guide - Linux Daily Tips

이 문서는 Linux Daily Tips 프론트엔드 프로젝트의 현재 설정 및 개발 가이드입니다.

## 📋 프로젝트 개요

**프로젝트명**: Linux Daily Tips Frontend
**기술 스택**: Next.js 16 + TypeScript + Tailwind CSS + shadcn/ui
**개발 상태**: Week 1 완료 (Day 1-7, 상태 관리 시스템 포함)

## 🛠 기술 스택 및 설정

### 핵심 기술
- **Node.js 22 LTS**: 최신 장기 지원 버전 (2027년까지 지원)
- **Next.js 16**: App Router, Turbopack (stable), React Compiler 지원, React 19.2
- **TypeScript 5.9.3**: Strict 모드 활성화
- **Tailwind CSS 3.4.18**: 커스텀 테마 (Awwwards 스타일 적용)
- **shadcn/ui**: 기본 UI 컴포넌트 시스템

### 주요 라이브러리
```json
{
  "node": ">=22.0.0",
  "next": "^16.0.0",
  "react": "^19.2.0",
  "typescript": "5.9.3",
  "tailwindcss": "^3.4.18",
  "lucide-react": "^0.548.0",
  "@tailwindcss/typography": "^0.5.10",
  "@types/node": "^22.0.0"
}
```

### 개발 도구
- **Turbopack**: Hot Reload < 2초 달성
- **ESLint**: 코드 품질 관리
- **Prettier**: 코드 포맷팅 자동화
- **Jest + React Testing Library**: 테스트 환경

## 📁 디렉토리 구조

```
frontend/
├── app/                           # Next.js 15 App Router
│   ├── globals.css               # 글로벌 스타일 + Awwwards 테마
│   ├── layout.tsx                # 루트 레이아웃
│   ├── page.tsx                  # 홈페이지 (컴포넌트 분리됨)
│   ├── admin/
│   │   └── page.tsx             # 관리자 페이지
│   └── terminal/
│       └── page.tsx             # 터미널 에뮬레이터 페이지
├── components/
│   ├── sections/                 # 페이지 섹션 컴포넌트
│   │   ├── index.ts             # 통합 export
│   │   ├── HeroSection.tsx      # 메인 히어로 섹션
│   │   ├── TodayTipSection.tsx  # 오늘의 팁 섹션
│   │   ├── RecentTipsSection.tsx # 최근 팁 섹션
│   │   ├── StatsSection.tsx     # 통계 섹션
│   │   └── CTASection.tsx       # Call-to-Action 섹션
│   └── ui/                      # shadcn/ui 기본 컴포넌트
│       ├── button.tsx
│       └── card.tsx
├── lib/
│   ├── types/                   # TypeScript 타입 정의
│   │   ├── index.ts            # 통합 export
│   │   ├── tip.ts              # 핵심 데이터 타입
│   │   └── api.ts              # API 관련 타입
│   └── utils.ts                # 유틸리티 함수
└── public/                     # 정적 에셋
```

## 🎨 디자인 시스템

### Awwwards 스타일 테마
현재 Awwwards.com에서 영감을 받은 미니멀 디자인 적용:

- **컬러 팔레트**: Neutral grays + Accent blue
- **타이포그래피**: Inter + JetBrains Mono
- **애니메이션**: Subtle hover effects + Card interactions
- **레이아웃**: Container-based responsive design

### 주요 CSS 클래스
```css
.container-awwwards    # 표준 컨테이너 레이아웃
.card-awwwards         # 카드 스타일링
.interactive           # 인터랙티브 요소 호버 효과
.terminal-container    # 터미널 스타일링
.gradient-text         # 그라데이션 텍스트
```

## ♿ 접근성 (Accessibility)

### 구현된 접근성 기능
- **WCAG 2.1 AA 준수** 수준으로 개선됨
- **Skip Links**: 키보드 네비게이션 지원
- **ARIA 속성**: 모든 인터랙티브 요소에 적절한 라벨
- **Screen Reader**: 스크린 리더 전용 텍스트 구현
- **Semantic HTML**: 의미있는 landmark 구조
- **Keyboard Navigation**: 모든 기능 키보드 접근 가능

### 접근성 점수
- **이전**: 6.5/10
- **현재**: 9.0+/10 예상 (Code Quality Evaluator 기준)

## 🔧 개발 환경 설정

### 🐳 **Docker vs 로컬 개발 전략**
**현재 방식 (Day 1-25)**: **하이브리드 개발 환경**
- **프론트엔드**: 로컬 Node.js 환경 (`npm run dev`)
- **백엔드/DB**: Docker Compose (`docker-compose up`)
- **프로덕션**: Docker 멀티스테이지 빌드

**Phase 1 완료 (Day 26-27)**: **완전 도커화 전환**
- **전체 스택**: Docker Compose 통합 환경
- **개발/프로덕션**: 환경 일치성 보장
- **배포**: 원클릭 전체 시스템 실행

### 실행 방법

**현재 방식 (Day 1-25)**:
```bash
# 1. 백엔드 서비스 시작 (PostgreSQL + Redis + FastAPI)
docker-compose up -d

# 2. 프론트엔드 개발 서버 실행 (별도 터미널)
cd frontend
npm run dev

# 빌드 및 테스트
npm run build
npm run lint
npm test
```

**Phase 1 완료 후 (Day 26+)**:
```bash
# 전체 스택 원클릭 실행 (프론트엔드 + 백엔드 + DB)
docker-compose up

# 또는 개발 모드로 실행
docker-compose up --build
```

### 환경 변수 설정
```bash
# .env.local 파일 생성 필요
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 성능 목표
- **Hot Reload**: < 2초 ✅
- **페이지 로딩**: < 3초 (목표)
- **Lighthouse 점수**: 90+ (목표)

## 📝 TypeScript 타입 시스템

### 백엔드 동기화 타입
모든 타입은 백엔드 FastAPI 데이터 모델과 동기화됨:

```typescript
// 핵심 데이터 타입
export type DifficultyLevel = 'Beginner' | 'Intermediate' | 'Advanced'
export type TipCategory = 'File Management' | 'System Monitoring' | ...

// 주요 인터페이스
export interface TipData { ... }      # 개별 팁 데이터
export interface DraftWeek { ... }    # 드래프트 주간 데이터
export interface StatsData { ... }    # 통계 데이터
```

### API 통신 타입
```typescript
// API 응답 타입
export interface ApiResponse<T> { ... }
export interface PaginatedResponse<T> { ... }

// 에러 처리 타입
export type ApiError = NetworkError | ValidationError | ...
```

## 🧩 컴포넌트 설계 원칙

### 1. 관심사 분리
- 각 섹션을 독립적인 컴포넌트로 분리
- Props를 통한 데이터 전달
- 재사용 가능한 구조

### 2. 접근성 우선
- 모든 컴포넌트에 적절한 ARIA 속성
- 키보드 네비게이션 지원
- 스크린 리더 호환성

### 3. 타입 안전성
- TypeScript 엄격 모드 사용
- Props 인터페이스 명시적 정의
- 런타임 에러 최소화

## 📦 상태 관리 시스템 (Day 7 완료)

### 설치된 라이브러리
- **Zustand 4.5.7**: 클라이언트 상태 관리
- **React Query 5.90.2**: 서버 상태 관리 및 캐싱
- **Axios 1.12.2**: HTTP 클라이언트

### 구현된 Stores
- **themeStore**: light/dark/system 테마 관리 (영속화)
- **userStore**: 사용자 인증 상태 (영속화)
- **appStore**: 전역 UI 상태 (sidebar, terminal, loading)

### Custom Hooks
- `useTodayTip()`, `useRecentTips()`, `useTip()`, `useTipsList()`, `useSearchTips()`, `useLikeTip()`

### 공통 컴포넌트
- **ErrorBoundary**: React 에러 처리
- **LoadingSpinner**: 로딩 상태 (sm/md/lg/xl)
- **ErrorMessage**: 에러 메시지 (error/warning/info/critical)

자세한 내용은 [Day 7 완료 보고서](./docs/DAY7_COMPLETION_REPORT.md) 참고

## 🎉 Day 23-24 완료 (MSW 제거 및 API 통합)

### 주요 성과
1. **MSW 완전 제거** ✅
   - 596줄 Mock 코드 삭제 (`frontend/lib/mocks/`)
   - 33개 패키지 제거 (msw + 의존성)
   - `QueryProvider`에서 MSW 초기화 코드 제거

2. **실제 백엔드 API 연동** ✅
   - 홈페이지에서 실제 데이터 표시 확인
   - `useTodayTip()`, `useRecentTips()` hooks 실제 API 호출
   - React Query 캐싱 전략 적용 (5분 TTL)

3. **API 네이밍 이슈 임시 해결** ✅
   - 백엔드: `publish_date` (snake_case, Python 표준)
   - 프론트엔드: `publishDate` (camelCase, TypeScript 표준)
   - 임시 해결: `(tip as any).publish_date || tip.publishDate` 패턴
   - 장기 해결: Pydantic `alias_generator` (Day 25에서 완전 해결!)

4. **버그 수정** ✅
   - 카테고리 배열 표시: `Array.isArray(tip.category) ? tip.category.join(', ') : tip.category`
   - 터미널 레이스 컨디션: "Connected!" 메시지 제거

5. **통합 테스트 성공** ✅
   - 홈페이지: 오늘의 팁 + 최근 팁 3개 표시
   - 터미널: WebSocket 연결 완전 작동

### 주의사항
- **네이밍 패턴**: Tips 페이지 구현 시 `(tip as any).publish_date || tip.publishDate` 계속 사용
- **MSW 잔재**: `package.json` msw 설정 블록, `public/mockServiceWorker.js` 정리 권장 (선택)

## 🎉 Day 25 완료 (코드 품질 개선)

### 주요 성과
1. **API 네이밍 이슈 완전 해결** ✅
   - **Pydantic alias_generator 구현** (`backend/app/schemas/tip.py`)
   - `to_camel()` 함수로 snake_case → camelCase 자동 변환
   - `publish_date` → `publishDate`, `view_count` → `viewCount` 등 모든 필드 자동 변환
   - **결과**: 백엔드 API 응답이 이제 TypeScript 표준 camelCase로 제공됨!

2. **Frontend Cleanup 완료** ✅
   - 3개 파일에서 모든 `(tip as any)` 제거:
     - `components/tips/TipCard.tsx`
     - `components/sections/RecentTipsSection.tsx`
     - `app/tips/[id]/page.tsx`
   - 변경 전: `const publishDate = new Date((tip as any).publish_date || tip.publishDate);`
   - 변경 후: `const publishDate = new Date(tip.publishDate);`

3. **Categories API 동적화** ✅
   - 하드코딩 제거 → PostgreSQL 실시간 쿼리
   - `jsonb_array_elements_text()` 함수로 고유 카테고리 추출
   - `useCategories()` hook으로 프론트엔드 연동 (30분 캐싱)

4. **Trailing Slash 이슈 수정** ✅
   - 307 Redirect 문제 해결 (backend `@router.get("", ...)`)
   - Tips 페이지 필터 정상 작동 확인

5. **Search 기능 임시 비활성화** ✅
   - `disabled` prop 추가, "Search (Coming soon)" 표시
   - Phase 2에서 재구현 예정

6. **타입 안전성 100% 달성** ✅
   - `lib/types/common.ts` 타입 정의 확인 (이미 완성됨)
   - `lib/env.ts` Zod 환경 변수 검증 확인 (이미 완성됨)
   - `lib/api/client.ts` CustomError 사용 확인 (이미 완성됨)
   - TypeScript 컴파일: 에러 없음 ✅

### 코드 품질 향상
- **any 타입 완전 제거**: 프로덕션 코드에서 `as any` 사용 제거
- **환경 변수 검증**: Zod 스키마로 런타임 검증
- **API 응답 통일**: snake_case/camelCase 혼용 문제 해결
- **타입 추론 개선**: 모든 API 응답이 TypeScript 타입과 완벽 일치

### 완료 보고서
- `docs/tips-pages-implementation-plan.md` 업데이트 완료

## 🚀 다음 단계 (Week 4: Day 25-28)

### Day 25-26: Tips 페이지 구현 (최우선)
1. **팁 상세 페이지**: `/tips/[id]/page.tsx` - 개별 팁 전체 내용
2. **팁 목록 페이지**: `/tips/page.tsx` - 페이지네이션 + 필터링 + 검색
3. **홈페이지 404 링크 수정**: "View All Tips", 팁 카드 클릭

### Day 27: E2E 테스트 & 성능 최적화
1. **Playwright E2E 테스트**: 홈페이지, 터미널, Tips 페이지
2. **Lighthouse 90+ 달성**: 번들 사이즈 분석, 코드 분할

### Day 28: 완전 도커화
1. **프론트엔드 Docker**: 멀티스테이지 빌드
2. **docker-compose 통합**: 원클릭 전체 스택 실행

## ⚠️ 주의사항

### 개발 시 고려사항
1. **Next.js 16**: 최신 안정 버전 (Turbopack stable, React Compiler 지원)
2. **컴포넌트 분리**: 각 섹션의 독립성 유지 필수
3. **접근성**: 새로운 컴포넌트 추가 시 접근성 검증 필수
4. **타입 동기화**: 백엔드 스키마 변경 시 타입 업데이트 필요

### 성능 최적화 포인트
- 이미지 lazy loading 구현 예정
- 코드 분할 (Code Splitting) 적용 예정
- 번들 크기 최적화 예정

## 📊 현재 상태 요약 (Day 23-24 완료)

### ✅ 완료된 작업 (Day 1-24)
**Week 1 (Day 1-7): 프론트엔드 인프라**
- [x] Next.js 16 + React 19.2 + TypeScript 프로젝트 설정
- [x] Tailwind CSS + Awwwards 테마 적용
- [x] shadcn/ui 컴포넌트 시스템 통합
- [x] 컴포넌트 파일 분리 및 구조화 (5개 섹션)
- [x] TypeScript 타입 시스템 구축 (100% 커버리지)
- [x] 접근성 개선 (WCAG 2.1 AA 수준, 9.0+/10)
- [x] Hot Reload < 2초 성능 달성
- [x] Zustand 상태 관리 시스템 (3개 stores)
- [x] React Query 데이터 페칭 (6개 hooks)
- [x] Axios API 클라이언트 (25+ endpoints)
- [x] 에러 처리 및 로딩 컴포넌트
- [x] Layout 통합 (ErrorBoundary, QueryProvider)

**Week 2-3 (Day 8-21): 백엔드 API & 터미널**
- [x] FastAPI 백엔드 구현 (PostgreSQL 연동, 266개 테스트 100% 통과)
- [x] Terminal Emulator (xterm.js + WebSocket + Docker)

**Week 4 (Day 22-25): API 통합 & 코드 품질 개선**
- [x] MSW 완전 제거 (596줄 코드, 33개 패키지)
- [x] Frontend ↔ Backend API 통합 완료
- [x] API 네이밍 이슈 완전 해결 (Pydantic alias_generator)
- [x] Frontend cleanup (any 타입 완전 제거)
- [x] Categories API 동적화 (PostgreSQL 쿼리)
- [x] 타입 안전성 100% 달성
- [x] 홈페이지 실제 데이터 표시
- [x] API 네이밍 이슈 해결 (`publish_date` vs `publishDate`)
- [x] 터미널 WebSocket 완전 작동

### 🔄 다음 작업 (Week 4: Day 26-28)
- [ ] **Day 26: Tips 페이지 구현** - 최우선
  - [ ] 팁 상세 페이지 (`/tips/[id]/page.tsx`)
  - [ ] 팁 목록 페이지 (`/tips/page.tsx`)
  - [ ] **검색 기능 수정** ⭐ (백엔드 지원 확인 후 활성화)
  - [ ] **정렬 드롭다운 버그 수정** ⭐ (상태 관리 수정)
  - [ ] 페이지네이션 구현
  - [ ] 홈페이지 404 링크 수정
- [ ] Day 27: E2E 테스트 작성 (Playwright)
- [ ] Day 27: 성능 최적화 (Lighthouse 90+)
- [ ] Day 28: 완전 도커화 (프론트엔드 Docker)

### 📈 프로젝트 진행률
- **Phase 1 (MVP)**: 87% 완료 (71/82 작업)
  - ✅ Week 1 Frontend: 100% 완료 (17/17 작업)
  - ✅ Week 2 Backend API: 100% 완료 (26/26 작업)
  - ✅ Week 3 Terminal Emulator: 100% 완료 (16/16 작업)
  - ⏳ Week 4 통합 및 최적화: 52% 완료 (12/23 작업)
    - Day 22-25 완료 (12개)
    - Day 26 예정 (6개, 검색/정렬 수정 포함) ⭐
    - Day 27-28 예정 (5개)

이 문서는 프로젝트 진행에 따라 지속적으로 업데이트됩니다.

---

## 🤖 프론트엔드 에이전트 활용

**자주 사용할 에이전트**:
- `ui-ux-designer`: 페이지/컴포넌트 설계, 사용자 플로우 최적화, 접근성 개선
- `frontend-code-writer`: React/Next.js 컴포넌트 작성, 상태 관리, API 연동, 스타일링
- `unit-test-generator`: 유틸리티 함수, hooks, 상태 관리 로직 테스트 (선택적)
- `code-refactoring-specialist`: 컴포넌트 분리, Props drilling 해결, 성능 최적화
- `general-purpose`: 컴포넌트 사용처 검색, 전역 리네이밍

**추천 워크플로우**:
1. ui-ux-designer로 설계 → 2. frontend-code-writer로 구현 → 3. 브라우저 확인 (필수)

**주의**: UI는 반드시 실제 브라우저에서 시각적으로 확인하세요!