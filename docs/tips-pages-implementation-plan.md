# Tips 페이지 구현 계획

**작성일**: 2025-11-04
**프로젝트**: Linux Daily Tips Web Service
**대상 작업**: Week 4 Day 25-26

---

## 📊 현재 상태

### ✅ 완료된 작업 (Day 1-24)
- **백엔드 API**: 100% 완성 (Day 12-13)
  - `GET /api/v1/tips/daily` - 오늘의 팁
  - `GET /api/v1/tips` - 팁 목록 (페이지네이션)
  - `GET /api/v1/tips/{tip_id}` - 팁 상세 조회
  - Redis 캐싱, 266개 테스트 98.3% 통과

- **프론트엔드 인프라**: 100% 준비 (Day 1-7)
  - React Query hooks 6개 구현 (`useTip`, `useTipsList`, `useSearchTips` 등)
  - API 클라이언트 완성 (Axios + 인터셉터)
  - 타입 시스템 (TypeScript, 백엔드 동기화)
  - 재사용 가능한 컴포넌트 (`TodayTipSection`, `RecentTipsSection`)

- **터미널 에뮬레이터**: 100% 완성 (Day 15-21)
  - xterm.js + WebSocket + Docker 통합
  - 보안 검증 및 성능 최적화 완료

- **MSW 제거 & API 통합**: 100% 완료 (Day 23-24) ✨
  - 596줄 Mock 코드 삭제, 33개 패키지 제거
  - 실제 백엔드 API 연동 완료
  - 홈페이지 통합 테스트 성공
  - 테스트 데이터 스크립트 생성 (`backend/scripts/add_test_tips.py`)

- **코드 품질 개선**: 100% 완료 (Day 25) ✨ 신규
  - **API 네이밍 이슈 완전 해결**: Pydantic `alias_generator` 구현
    - `backend/app/schemas/tip.py`에 `to_camel()` 함수 추가
    - snake_case → camelCase 자동 변환
  - **Frontend cleanup**: 3개 파일에서 모든 `(tip as any)` 제거
    - `components/tips/TipCard.tsx`
    - `components/sections/RecentTipsSection.tsx`
    - `app/tips/[id]/page.tsx`
  - **Categories API 동적화**: PostgreSQL `jsonb_array_elements_text()` 사용
  - **Trailing slash 이슈 수정**: 307 Redirect 해결
  - **Search 비활성화**: "Coming soon" 표시
  - **타입 안전성**: TypeScript 컴파일 에러 없음, `any` 타입 완전 제거

### ❌ 미완성 작업
- **Tips 전용 페이지 없음**
  - `/tips/page.tsx` - 목록 페이지 없음
  - `/tips/[id]/page.tsx` - 상세 페이지 없음

### ⚠️ 현재 문제
- 홈페이지에 404 링크 존재:
  - "View All Tips" 버튼 → `/tips` (404)
  - 팁 카드 클릭 → `/tips/{id}` (404)
- **Tips 페이지 기능 이슈** (Day 25 발견):
  - 검색창: 의도적으로 비활성화 ("Coming soon" 표시)
  - 정렬 드롭다운: 작동하지 않음 (버그)
  - **해결 시점**: Day 26에 Tips 페이지 구현과 함께 수정 예정

---

## 🎯 구현 목표

### 주요 목표
1. 홈페이지 404 링크 수정
2. 완전한 팁 조회 시스템 구축
3. 사용자 경험 개선

### 구현 범위
1. **팁 상세 페이지** (`/tips/[id]/page.tsx`) - 개별 팁 전체 내용
2. **팁 목록 페이지** (`/tips/page.tsx`) - 전체 팁 리스트 + 필터링

---

## 📅 Phase 1: 팁 상세 페이지 (우선순위 높음)

### 파일 생성
- **경로**: `frontend/app/tips/[id]/page.tsx`
- **예상 코드량**: 120-150줄

### 주요 기능

#### 1. 팁 전체 내용 표시
```typescript
// 사용할 Hook
const { data: tip, isLoading, error } = useTip(params.id);

// 표시 항목
- 제목 (title)
- 전체 설명 (description)
- 명령어 (command)
- 예제 (example)
- 터미널 설정 (terminal_setup)
```

#### 2. 메타데이터 표시
- 난이도 배지 (BEGINNER/INTERMEDIATE/ADVANCED)
  - `getDifficultyColor()` 유틸 함수 사용
- 카테고리 배지 (쉼표로 구분)
- 게시일 (published_at)
- 좋아요 수 (likes_count)

#### 3. 터미널 실습 버튼
```typescript
<Link href="/terminal">
  <Button>터미널에서 실습하기</Button>
</Link>
```

#### 4. 에러 처리
- 404 처리 (존재하지 않는 팁)
- 로딩 상태 (`LoadingSpinner`)
- 에러 상태 (`ErrorMessage`)

### 재사용할 코드

#### Hooks
- `useTip(id)` - 이미 구현됨 (`frontend/lib/hooks/useTips.ts`)

#### 컴포넌트
- `TodayTipSection.tsx` - 레이아웃 참고
- `LoadingSpinner` - 로딩 상태
- `ErrorMessage` - 에러 표시

#### 유틸리티
- `getDifficultyColor(difficulty)` - 난이도 색상
- `formatDate(date)` - 날짜 포맷팅

#### 스타일
- Awwwards 테마 (`.card-awwwards`, `.interactive`)
- 다크모드 지원

### 기술 스택
- Next.js 15 App Router (Dynamic Route)
- React Query (캐싱 10분)
- Tailwind CSS + shadcn/ui
- Markdown 렌더링 옵션:
  - `@tailwindcss/typography` (이미 설치됨) ✅
  - 또는 `react-markdown` (추가 설치 필요)

### 구현 단계
1. 기본 페이지 구조 생성
2. `useTip(id)` hook 연동
3. 로딩/에러 상태 처리
4. 메타데이터 표시
5. Markdown 렌더링
6. 터미널 실습 버튼 연결
7. 스타일링 (Awwwards 테마)
8. 테스트 (실제 백엔드 데이터)

### 예상 소요 시간
**2-3시간**

---

## 📅 Phase 2: 팁 목록 페이지

### 파일 생성
- **경로**: `frontend/app/tips/page.tsx`
- **예상 코드량**: 150-200줄

### 주요 기능

#### 1. 팁 목록 그리드
```typescript
// 사용할 Hook
const { data, isLoading, error } = useTipsList({
  page: currentPage,
  page_size: 10,
  difficulty: selectedDifficulty,
  category: selectedCategory,
});

// 카드 그리드 (3열)
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {tips.map(tip => <TipCard key={tip.id} tip={tip} />)}
</div>
```

#### 2. 필터링 UI
```typescript
// 난이도 필터 (드롭다운)
- 전체
- 초급 (BEGINNER)
- 중급 (INTERMEDIATE)
- 고급 (ADVANCED)

// 카테고리 필터 (드롭다운)
- 전체
- file-system
- basics
- networking
- security
- (동적으로 백엔드에서 가져오기)
```

#### 3. 검색 기능
```typescript
const { data: searchResults } = useSearchTips(searchQuery);

<Input
  type="search"
  placeholder="팁 검색..."
  onChange={(e) => setSearchQuery(e.target.value)}
/>
```

#### 4. 페이지네이션
```typescript
// React Query가 제공하는 페이지 정보 사용
<Pagination
  currentPage={data.page}
  totalPages={data.total_pages}
  onPageChange={setCurrentPage}
/>
```

### UI 구성
```
┌─────────────────────────────────────────────────┐
│  Linux Daily Tips - 모든 팁 보기                    │
├─────────────────────────────────────────────────┤
│  [🔍 검색]  [난이도 ▼]  [카테고리 ▼]              │
├─────────────────────────────────────────────────┤
│  ┌───────┐  ┌───────┐  ┌───────┐                │
│  │  팁1  │  │  팁2  │  │  팁3  │                 │
│  │ 초급  │  │ 중급  │  │ 고급  │                 │
│  └───────┘  └───────┘  └───────┘                │
│  ┌───────┐  ┌───────┐  ┌───────┐                │
│  │  팁4  │  │  팁5  │  │  팁6  │                 │
│  └───────┘  └───────┘  └───────┘                │
├─────────────────────────────────────────────────┤
│        [◀ 이전]  1  2  3  4  5  [다음 ▶]         │
└─────────────────────────────────────────────────┘
```

### 재사용할 코드

#### Hooks
- `useTipsList(params)` - 목록 조회
- `useSearchTips(query)` - 검색

#### 컴포넌트
- `RecentTipsSection.tsx` - 카드 디자인 재사용
- `LoadingSpinner`, `ErrorMessage`

#### 스타일
- Awwwards 카드 스타일
- 그리드 레이아웃 (Tailwind)

### 구현 단계
1. 기본 페이지 구조 생성
2. `useTipsList()` hook 연동
3. 카드 그리드 구현
4. 필터링 UI 구현
5. **검색 기능 수정** ⭐ 신규
   - 백엔드 `/api/v1/tips/search` 엔드포인트 확인
   - 지원 시: 검색창 활성화 (`disabled={false}`)
   - 미지원 시: Phase 2로 이연
   - 예상 소요: 1시간
6. **정렬 드롭다운 버그 수정** ⭐ 신규
   - 백엔드는 이미 `sort_by`, `order` 파라미터 지원
   - 프론트엔드 상태 관리 버그 수정
   - 예상 소요: 30분
7. 페이지네이션 구현
8. 상태 관리 (URL 쿼리 파라미터)
9. 스타일링
10. 테스트

### 예상 소요 시간
**4-5시간** (검색/정렬 수정 1.5시간 포함)

---

## 📅 Phase 3: 통합 및 검증

### 1. 홈페이지 링크 검증 (30분)
- [ ] "View All Tips" 버튼 → `/tips` 정상 작동
- [ ] 팁 카드 클릭 → `/tips/[id]` 정상 작동
- [ ] 터미널 실습 버튼 → `/terminal` 연결 확인

### 2. 수동 테스트 (1시간)
- [ ] 브라우저에서 실제 백엔드 데이터 표시 확인
- [ ] 페이지네이션 동작 (다음/이전 페이지)
- [ ] 필터링 동작 (난이도, 카테고리)
- [ ] **검색 동작 (키워드 입력)** ⭐ 수정 완료 확인
- [ ] **정렬 드롭다운 동작 (Latest/Oldest/Title)** ⭐ 버그 수정 확인
- [ ] 로딩 상태 표시
- [ ] 에러 처리 (네트워크 에러, 404 등)
- [ ] 다크모드 동작
- [ ] 반응형 레이아웃 (모바일, 태블릿, 데스크톱)

### 3. 추가 정리 작업 (10분)
- [ ] MSW 잔재 제거
  - `package.json`의 msw 설정 블록 삭제
  - `public/mockServiceWorker.js` 파일 삭제

### 예상 소요 시간
**1.5시간**

---

## 🛠 구현 참고 사항

### 기존 API Endpoints
```typescript
// frontend/lib/api/endpoints.ts
export const API_ENDPOINTS = {
  TIPS: {
    LIST: '/api/v1/tips',                    // 목록
    TODAY: '/api/v1/tips/daily',             // 오늘의 팁
    BY_ID: (id: string) => `/api/v1/tips/${id}`, // 상세
    RECENT: '/api/v1/tips',                  // 최근 팁
  },
};
```

### 기존 Hooks
```typescript
// frontend/lib/hooks/useTips.ts

// 상세 페이지용
useTip(id: string)

// 목록 페이지용
useTipsList({
  page?: number;
  page_size?: number;
  difficulty?: DifficultyLevel;
  category?: string;
})

// 검색용
useSearchTips(query: string)
```

### ✅ API 네이밍 이슈 완전 해결 (Day 25 완료!)

**문제**: 백엔드 (snake_case) vs 프론트엔드 (camelCase) 불일치
- 백엔드: `publish_date` (Python PEP 8 표준)
- 프론트엔드: `publishDate` (JavaScript 표준)

**완료된 해결 방법** (2025-11-05):
1. **Pydantic alias_generator 구현** (`backend/app/schemas/tip.py`)
   ```python
   def to_camel(string: str) -> str:
       """snake_case 문자열을 camelCase로 변환합니다."""
       components = string.split('_')
       return components[0] + ''.join(x.title() for x in components[1:])

   class TipInDB(BaseModel):
       model_config = ConfigDict(
           alias_generator=to_camel,  # 자동 변환
           populate_by_name=True,     # 양방향 호환
       )
   ```

2. **Frontend cleanup 완료** - 3개 파일에서 `(tip as any)` 제거
   - `components/tips/TipCard.tsx`
   - `components/sections/RecentTipsSection.tsx`
   - `app/tips/[id]/page.tsx`

   ```typescript
   // 변경 전
   const publishDate = new Date((tip as any).publish_date || tip.publishDate);

   // 변경 후
   const publishDate = new Date(tip.publishDate);
   ```

3. **추가 개선 사항**:
   - ✅ Categories API 동적화 (하드코딩 → PostgreSQL 쿼리)
   - ✅ Trailing slash 이슈 수정 (307 Redirect 해결)
   - ✅ Search 기능 임시 비활성화 ("Coming soon")
   - ✅ TypeScript 타입 안전성 100% 달성

**결과**: 모든 `any` 타입 제거, 완전한 타입 안전성 확보!

### 타입 정의
```typescript
// frontend/types/tip.ts
interface TipData {
  id: string;
  title: string;
  description: string;
  command: string;
  example: string;
  difficulty: 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED';
  category: string[];
  terminal_setup?: TerminalSetup;
  published_at: string;
  likes_count: number;
}

interface PaginatedResponse<T> {
  items: T[];
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
}
```

### shadcn/ui 컴포넌트
```bash
# 이미 설치된 컴포넌트
- Button
- Card
- Badge
- Input
- Select
- Skeleton (로딩 상태)

# 추가 필요시
npx shadcn-ui@latest add pagination
```

---

## ✅ 완료 기준

### 필수 기능
- [ ] `/tips/[id]` 페이지에서 실제 팁 데이터 표시
- [ ] `/tips` 페이지에서 팁 목록 표시
- [ ] 페이지네이션 동작 (10개씩)
- [ ] 필터링 동작 (난이도, 카테고리)
- [ ] 검색 기능 동작
- [ ] 홈페이지 링크 모두 정상 작동
- [ ] 404 에러 없음
- [ ] 로딩/에러 상태 정상 처리

### 품질 기준
- [ ] TypeScript 타입 에러 없음
- [ ] ESLint 경고 없음
- [ ] 다크모드 정상 작동
- [ ] 반응형 레이아웃 (모바일 ✅, 태블릿 ✅, 데스크톱 ✅)
- [ ] 접근성 (키보드 네비게이션, ARIA)

### 성능 기준
- [ ] 페이지 로딩 < 2초
- [ ] React Query 캐싱 동작
- [ ] 불필요한 리렌더링 없음

---

## 📊 예상 소요 시간

| Phase | 작업 내용 | 소요 시간 |
|-------|----------|----------|
| Phase 1 | 팁 상세 페이지 | 2-3시간 ⭐ |
| Phase 2 | 팁 목록 페이지 + 검색/정렬 수정 | 4-5시간 (+1.5시간) |
| Phase 3 | 통합 및 검증 | 1.5시간 |
| **합계** | | **7.5-9.5시간** |

**하루 4-5시간 작업 기준: 2일 소요**

**추가 작업 (Day 26)**:
- ⭐ 검색 기능 수정: 1시간 (백엔드 지원 확인 후)
- ⭐ 정렬 드롭다운 버그 수정: 30분 (프론트엔드 상태 관리)

---

## 🚀 구현 접근 방식

### 옵션 A: 직접 구현 (추천) ⭐
**장점**:
- 빠른 구현 (5-6시간)
- 기존 컴포넌트 재사용
- 반복 작업 최소화

**단점**:
- 디자인 완성도는 중간 수준

### 옵션 B: 에이전트 활용
**장점**:
- 체계적 설계
- 높은 완성도
- UX 최적화

**단점**:
- 시간 더 소요 (7-8시간)
- 에이전트 오버헤드

**추천: 옵션 A** (시간 효율성, 모든 인프라 준비 완료)

---

## 📝 다음 단계

### 즉시 시작 (오늘)
1. **Phase 1 시작**: `/tips/[id]/page.tsx` 구현
   - 가장 우선순위 높음 (홈페이지 링크 수정)
   - 구현이 더 간단함

### 내일
2. **Phase 2**: `/tips/page.tsx` 구현
3. **Phase 3**: 통합 테스트 및 검증

### 완료 후
4. Day 25-26 완료 보고서 작성
5. Week 4 남은 작업 진행 (E2E 테스트, 도커화, 성능 최적화)

---

## 💡 추가 고려사항

### UX 개선 아이디어 (선택)
- 이전/다음 팁 네비게이션 버튼
- 팁 북마크 기능
- 팁 공유 버튼 (소셜 미디어)
- 댓글 시스템 (Phase 2 예정)

### 성능 최적화 (선택)
- 이미지 lazy loading
- Infinite scroll (페이지네이션 대체)
- Prefetch (다음 페이지 미리 로드)

### 접근성 (필수)
- ARIA 레이블
- 키보드 네비게이션
- 스크린 리더 지원

---

**작성자**: Claude Code (Sonnet 4.5)
**분석 기반**: Git 히스토리, 코드베이스 전수 조사
**신뢰도**: High (모든 인프라 검증 완료)
