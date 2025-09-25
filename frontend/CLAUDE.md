# Frontend Development Guide - Linux Daily Tips

이 문서는 Linux Daily Tips 프론트엔드 프로젝트의 현재 설정 및 개발 가이드입니다.

## 📋 프로젝트 개요

**프로젝트명**: Linux Daily Tips Frontend
**기술 스택**: Next.js 15 + TypeScript + Tailwind CSS + shadcn/ui
**개발 상태**: Day 3-4 완료 (컴포넌트 분리 및 접근성 개선 포함)

## 🛠 기술 스택 및 설정

### 핵심 기술
- **Next.js 15**: App Router, Turbopack 활성화
- **TypeScript**: Strict 모드 활성화
- **Tailwind CSS**: 커스텀 테마 (Awwwards 스타일 적용)
- **shadcn/ui**: 기본 UI 컴포넌트 시스템

### 주요 라이브러리
```json
{
  "next": "^15.0.0",
  "react": "^19.0.0",
  "typescript": "^5.6.3",
  "tailwindcss": "^3.4.15",
  "lucide-react": "^0.456.0",
  "@tailwindcss/typography": "^0.5.15"
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

## 📦 상태 관리 계획 (Day 7 예정)

### 예정된 라이브러리
- **Zustand**: 클라이언트 상태 관리
- **React Query (TanStack Query)**: 서버 상태 관리
- **Context API**: 테마 및 전역 설정

## 🚀 다음 단계 (Day 5-6)

### shadcn/ui 통합 계획
1. **shadcn/ui CLI 설치 및 설정**
2. **기본 컴포넌트 추가**: Input, Layout, Navigation 등
3. **다크모드 설정**
4. **반응형 레이아웃 컴포넌트 개발**

### 완료 기준
- [ ] shadcn/ui 기본 컴포넌트 설치 완료
- [ ] 헤더, 사이드바, 푸터 레이아웃 완성
- [ ] 다크모드 토글 기능 구현
- [ ] 반응형 디자인 검증

## ⚠️ 주의사항

### 개발 시 고려사항
1. **Next.js 15**: 최신 버전으로 예상치 못한 이슈 가능성 있음
2. **컴포넌트 분리**: 각 섹션의 독립성 유지 필수
3. **접근성**: 새로운 컴포넌트 추가 시 접근성 검증 필수
4. **타입 동기화**: 백엔드 스키마 변경 시 타입 업데이트 필요

### 성능 최적화 포인트
- 이미지 lazy loading 구현 예정
- 코드 분할 (Code Splitting) 적용 예정
- 번들 크기 최적화 예정

## 📊 현재 상태 요약

### ✅ 완료된 작업
- [x] Next.js 15 + TypeScript 프로젝트 설정
- [x] Tailwind CSS + Awwwards 테마 적용
- [x] shadcn/ui 기본 컴포넌트 (Button, Card) 설치
- [x] 컴포넌트 파일 분리 및 구조화
- [x] TypeScript 타입 시스템 구축
- [x] 접근성 개선 (WCAG 2.1 AA 수준)
- [x] Hot Reload < 2초 성능 달성

### 🔄 다음 작업
- [ ] shadcn/ui 추가 컴포넌트 설치
- [ ] 레이아웃 컴포넌트 개발
- [ ] 다크모드 구현
- [ ] 상태 관리 시스템 설정

이 문서는 프로젝트 진행에 따라 지속적으로 업데이트됩니다.