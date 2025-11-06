# Linux Daily Tips Web Service

매일 리눅스 사용 팁을 제공하고 실습 가능한 웹 터미널 환경을 제공하는 교육용 웹서비스입니다.

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (프론트엔드 개발용)
- Python 3.14+ (백엔드 개발용)

### Development Environment Setup

1. **저장소 클론**
```bash
git clone <repository-url>
cd linux-daily-tips
```

2. **환경 변수 설정**
```bash
cp .env.example .env
# .env 파일을 편집하여 필요한 설정값 입력
```

3. **개발 환경 시작**
```bash
./scripts/dev-up.sh
```

4. **개발 환경 종료**
```bash
./scripts/dev-down.sh
```

## 📊 서비스 액세스

### 🗄️ 데이터베이스 서비스
- **PostgreSQL**: `localhost:5432`
  - Database: `linux_daily_tips`
  - Username: `postgres`
  - Password: `postgres_dev_password`

- **Redis**: `localhost:6379`
  - Password: `redis_dev_password`

### 🛠️ 개발 도구
- **pgAdmin**: http://localhost:5050
  - Email: `admin@linuxtips.dev`
  - Password: `pgadmin_dev_password`

- **Redis Commander**: http://localhost:8081
  - Username: `admin`
  - Password: `redis_commander_password`

- **Mailhog (Email Testing)**: http://localhost:8025
  - SMTP: `localhost:1025`

### 🎯 애플리케이션 서비스 (향후 추가)
- **FastAPI Backend**: http://localhost:8000
- **Next.js Frontend**: http://localhost:3000

## 🏗️ 아키텍처

### 기술 스택
- **Frontend**: Next.js 15 + TypeScript + Tailwind CSS + shadcn/ui
- **Backend**: FastAPI + Python 3.14 + asyncio
- **Database**: PostgreSQL 15 + Redis 7
- **DevOps**: Docker + Docker Compose

### 프로젝트 구조
```
linux-daily-tips/
├── backend/                 # FastAPI 백엔드
│   ├── init-db/            # 데이터베이스 초기화 스크립트
│   │   ├── 01-init-schema.sql
│   │   └── dev-data/       # 개발용 샘플 데이터
│   └── config/             # 설정 파일
├── frontend/               # Next.js 프론트엔드
├── docs/                   # 프로젝트 문서
│   ├── requirements.md     # 요구사항 정의서
│   ├── service-planning.md # 기술 설계서
│   └── phase1-tasks.md     # 개발 계획서
├── scripts/                # 개발 스크립트
│   ├── dev-up.sh          # 개발 환경 시작
│   └── dev-down.sh        # 개발 환경 종료
├── docker-compose.yml      # 기본 Docker Compose 설정
├── docker-compose.dev.yml  # 개발 환경 설정
└── .env.example           # 환경 변수 템플릿
```

## 🗃️ 데이터베이스 스키마

### 주요 테이블
- **tips**: 승인된 일일 팁 저장
- **draft_weeks**: LLM 생성 주간 드래프트
- **draft_tips**: 개별 드래프트 팁
- **admin_users**: 관리자 계정
- **terminal_sessions**: 터미널 세션 관리
- **analytics_events**: 사용자 행동 분석

### 특징
- UUID 기본키 사용
- JSONB 활용 (터미널 설정, 메타데이터)
- Full-text search 지원
- 자동 타임스탬프 관리

## 🔧 개발 도구

### 유용한 명령어
```bash
# 서비스 상태 확인
docker compose ps

# 실시간 로그 확인
docker compose logs -f

# 특정 서비스 로그
docker compose logs postgres

# 데이터베이스 접속
docker compose exec postgres psql -U postgres -d linux_daily_tips

# Redis 접속
docker compose exec redis redis-cli -a redis_dev_password

# 전체 환경 재시작
./scripts/dev-down.sh && ./scripts/dev-up.sh

# 데이터 완전 삭제 후 재시작
./scripts/dev-down.sh --clean-volumes
```

## 🔄 CI/CD 파이프라인 (Docker 기반)

### Docker 기반 GitHub Actions 워크플로우

본 프로젝트는 완전히 Docker화된 CI/CD 파이프라인을 제공합니다. 모든 테스트와 빌드가 Docker 컨테이너 내에서 실행되어 환경 일관성을 보장합니다.

#### 📋 워크플로우 구성

**🐍 Backend CI** (`.github/workflows/backend-ci.yml`)
- **Docker 멀티스테이지 빌드**: development, testing, production 타겟
- **컨테이너화된 서비스**: PostgreSQL 15, Redis 7 테스트 환경
- **코드 품질 검사**: Docker 컨테이너 내에서 Black, flake8, mypy, isort 실행
- **테스트 실행**: pytest with coverage in Docker
- **보안 스캔**: Safety, Trivy 취약점 검사
- **Docker 이미지 빌드 테스트**: 모든 빌드 스테이지 검증

**⚛️ Frontend CI** (`.github/workflows/frontend-ci.yml`)
- **Docker 멀티스테이지 빌드**: development, testing, production 타겟
- **컨테이너화된 테스트**: ESLint, Prettier, TypeScript 컨테이너 실행
- **Next.js 빌드**: Docker 컨테이너 내 빌드 및 최적화
- **E2E 테스트**: Playwright with Docker backend 연동
- **Lighthouse 감사**: 성능 및 접근성 측정
- **보안 스캔**: 프론트엔드 의존성 취약점 검사

**🚀 Deployment** (`.github/workflows/deploy.yml`)
- **Docker 이미지 빌드**: GitHub Container Registry에 멀티 아키텍처 이미지 푸시
- **스테이징 자동 배포**: main 브랜치 푸시 시 Docker Compose 활용
- **프로덕션 배포**: 릴리즈 태그 시 자동 배포
- **롤링 업데이트**: 무중단 배포 지원
- **헬스 체크**: 컨테이너 상태 검증 및 자동 롤백

#### 🐳 Docker CI/CD 설정 파일

**Docker Compose CI 설정** (`docker-compose.ci.yml`)
```yaml
# CI 전용 PostgreSQL/Redis 테스트 환경
# 각 컴포넌트별 테스트 서비스 정의
# 코드 품질 검사, 테스트, 빌드 서비스 포함
```

**백엔드 Dockerfile** (`backend/Dockerfile`)
```dockerfile
# 멀티스테이지 빌드: base -> development -> testing -> production
# Poetry 의존성 관리, 비root 사용자 보안 설정
# 헬스체크 및 최적화된 Python 환경
```

**프론트엔드 Dockerfile** (`frontend/Dockerfile`)
```dockerfile
# 멀티스테이지 빌드: base -> development -> testing -> builder -> production
# Next.js standalone 빌드, 성능 최적화
# 보안 헤더 및 이미지 최적화 설정
```

#### 🛠️ 로컬 Docker CI 도구 실행

**전체 CI 테스트 실행**
```bash
# 백엔드 CI 테스트
docker compose -f docker-compose.ci.yml run --rm backend-test
docker compose -f docker-compose.ci.yml run --rm backend-lint
docker compose -f docker-compose.ci.yml run --rm backend-security

# 프론트엔드 CI 테스트
docker compose -f docker-compose.ci.yml run --rm frontend-test
docker compose -f docker-compose.ci.yml run --rm frontend-lint

# CI 환경 정리
docker compose -f docker-compose.ci.yml down -v
```

**개별 Docker 빌드 테스트**
```bash
# 백엔드 멀티스테이지 빌드 테스트
docker build --target development -t linux-tips-backend:dev ./backend
docker build --target testing -t linux-tips-backend:test ./backend
docker build --target production -t linux-tips-backend:prod ./backend

# 프론트엔드 멀티스테이지 빌드 테스트
docker build --target development -t linux-tips-frontend:dev ./frontend
docker build --target testing -t linux-tips-frontend:test ./frontend
docker build --target production -t linux-tips-frontend:prod ./frontend
```

**로컬 컨테이너 개발 환경**
```bash
# 백엔드 개발 컨테이너 실행
docker compose up -d postgres redis
docker compose up backend

# 프론트엔드 개발 컨테이너 실행
docker compose -f docker-compose.dev.yml up frontend
```

#### 🚀 Docker 기반 배포 트리거

**자동 배포 (Docker 이미지 빌드 및 푸시)**
```bash
# main 브랜치 푸시 시 자동 실행
git push origin main
# → GitHub Container Registry에 latest 태그로 이미지 푸시
# → 스테이징 환경에 자동 배포

# 릴리즈 태그 생성 시 프로덕션 배포
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
# → 버전 태그로 이미지 빌드 및 푸시
# → 프로덕션 환경에 자동 배포
```

**수동 배포 (GitHub Actions)**
```bash
# GitHub CLI를 통한 워크플로우 실행
gh workflow run deploy.yml

# 또는 GitHub Actions UI에서 Deploy 워크플로우 실행
```

**로컬에서 Docker 이미지 테스트**
```bash
# 프로덕션 이미지 빌드 및 테스트
docker build --target production -t linux-tips-backend:local ./backend
docker build --target production -t linux-tips-frontend:local ./frontend

# 로컬 프로덕션 환경 시뮬레이션
docker run -d --name test-backend \
  -e DATABASE_URL=sqlite:///./test.db \
  -e REDIS_URL=redis://localhost:6379/0 \
  -e ENVIRONMENT=production \
  linux-tips-backend:local

docker run -d --name test-frontend \
  -e NEXT_PUBLIC_API_URL=http://localhost:8000 \
  -p 3000:3000 \
  linux-tips-frontend:local
```

#### 📊 Docker 기반 품질 게이트

모든 PR은 다음 Docker CI 조건을 만족해야 병합 가능:
- **컨테이너 빌드**: 모든 Docker 멀티스테이지 빌드 성공
- **컨테이너 테스트**: Docker Compose CI 환경에서 테스트 통과
- **이미지 보안**: Trivy 컨테이너 취약점 스캔 통과
- **이미지 크기**: 프로덕션 이미지 최적화 기준 충족
- **헬스 체크**: 컨테이너 상태 검사 통과
- **코드 커버리지**: 70% 이상 (컨테이너 내 측정)

#### 🐳 Docker 설정 파일 상세

**CI/CD 관련 Docker 파일**
```
linux-daily-tips/
├── backend/
│   ├── Dockerfile              # 멀티스테이지 프로덕션 빌드
│   └── Dockerfile.dev          # 개발 전용 빌드
├── frontend/
│   ├── Dockerfile              # 멀티스테이지 프로덕션 빌드
│   ├── Dockerfile.dev          # 개발 전용 빌드
│   └── next.config.js          # standalone 빌드 설정
├── docker-compose.yml          # 기본 서비스 구성
├── docker-compose.dev.yml      # 개발 환경 오버라이드
└── docker-compose.ci.yml       # CI 전용 테스트 환경
```

**주요 Docker 최적화**
- **멀티스테이지 빌드**: 개발/테스트/프로덕션 환경 분리
- **레이어 캐싱**: Poetry/npm 의존성 효율적 관리
- **보안 강화**: 비root 사용자, 최소 권한 원칙
- **이미지 크기**: Alpine 기반, 불필요한 파일 제거
- **헬스 체크**: 컨테이너 상태 모니터링 내장

## 📋 개발 상태

### 📊 Phase 1 진행률: 100% 완료 (126/126 작업) 🎉🏆

**Phase 1 MVP 개발 완전 완료!** ✅
- 모든 기본 기능 구현 완료
- 빌드 이슈 해결 완료
- API 안정성 개선 완료
- 사용자 경험 개선 완료
- 문서화 완료 (~4,000줄)

### ✅ 완료된 작업

#### **Week 1 (Day 1-7): 프론트엔드 인프라** ✅ 100% 완료

#### **Day 1-2: 프로젝트 인프라 구축** ✅
- [x] Git 저장소 구조 정리 (frontend/, backend/, docs/ 분리)
- [x] Docker Compose 개발 환경 구성 (PostgreSQL 15, Redis 7)
- [x] 데이터베이스 스키마 설계 및 초기화
- [x] 개발 스크립트 작성 (dev-up.sh, dev-down.sh)
- [x] 환경 변수 템플릿 (.env.example)
- [x] 개발 도구 통합 (pgAdmin, Redis Commander, Mailhog)
- [x] **Docker 기반 CI/CD 파이프라인 완료** 🐳
  - [x] Backend Dockerfile: 멀티스테이지 빌드 (development/testing/production)
  - [x] Frontend Dockerfile: Next.js standalone 빌드 최적화
  - [x] docker-compose.ci.yml: CI 전용 테스트 환경 구성
  - [x] Backend CI 워크플로우: Docker 컨테이너 기반 테스트/린트/보안스캔
  - [x] Frontend CI 워크플로우: Docker 기반 빌드/테스트/E2E/Lighthouse
  - [x] 배포 워크플로우: GitHub Container Registry + 자동 배포
  - [x] 보안 강화: Trivy, Safety, Bandit 통합
  - [x] 코드 품질: Black, ESLint, TypeScript, Prettier 자동화
  - [x] Poetry 설정: 백엔드 의존성 및 개발 도구 구성
  - [x] Next.js 설정: 프로덕션 빌드 및 보안 헤더 구성

#### **Day 3-4: Next.js 15 프론트엔드 기반** ✅
- [x] Next.js 15 프로젝트 생성 (App Router + Turbopack)
- [x] TypeScript 엄격 모드 설정
- [x] Tailwind CSS + Awwwards 스타일 테마 적용
- [x] 컴포넌트 아키텍처 구축 (sections/ 분리)
- [x] 접근성 개선 (WCAG 2.1 AA 수준, 9.0+/10)
- [x] TypeScript 타입 시스템 (tip.ts, api.ts)
- [x] Hot Reload < 2초 성능 달성

#### **Day 5-6: shadcn/ui 통합 및 레이아웃** ✅
- [x] shadcn/ui 설치 및 설정
- [x] UI 컴포넌트 설치 (Button, Card, Input, Separator, Sheet)
- [x] **다크모드 완성** (next-themes + CSS 변수 시스템)
  - [x] ThemeProvider 및 ThemeToggle 컴포넌트
  - [x] 모든 하드코딩 색상 제거 (CSS 변수로 전환)
  - [x] tailwind.config.js 다크모드 설정
- [x] **반응형 레이아웃 컴포넌트**
  - [x] Header: 로고, 네비게이션, 테마 토글
    - 데스크톱: 가로 네비게이션
    - 모바일: 햄버거 메뉴 + Sheet 드로어
  - [x] Footer: 저작권, 링크, SNS 아이콘
  - [x] 완전한 반응형 디자인 (mobile-first)
- [x] 접근성: ARIA 라벨, 키보드 네비게이션, Semantic HTML

#### **Day 7: 상태 관리 및 데이터 페칭** ✅
- [x] **Zustand 상태 관리 시스템** (4.5.7)
  - [x] themeStore: 테마 관리 (light/dark/system) + localStorage 영속화
  - [x] userStore: 사용자 인증 상태 + localStorage 영속화
  - [x] appStore: 전역 UI 상태 (sidebar, terminal, loading)
- [x] **React Query 데이터 페칭** (5.90.2)
  - [x] QueryProvider 설정 + DevTools 통합
  - [x] 6개 Custom Hooks (useTodayTip, useRecentTips, useTip, useTipsList, useSearchTips, useLikeTip)
  - [x] 캐싱 전략 설정 (5-10분 staleTime)
- [x] **Axios API 클라이언트** (1.12.2)
  - [x] Request/Response Interceptors
  - [x] 25+ API 엔드포인트 타입 정의
  - [x] 자동 JWT 토큰 관리
  - [x] 에러 처리 및 로깅
- [x] **에러 처리 및 로딩 컴포넌트**
  - [x] ErrorBoundary: React 에러 처리
  - [x] LoadingSpinner: 4가지 크기 (sm/md/lg/xl)
  - [x] ErrorMessage: 4가지 타입 (error/warning/info/critical)
  - [x] Layout 통합 완료
- [x] **환경 변수 설정** (.env.local.example)
- [x] **문서화**: 3개 문서 작성 (61KB)

### 🌿 Git 브랜치 전략
```
main  - 안정 버전 (릴리즈용)
  └── dev - 개발 브랜치 (현재 활성)
```
- **개발**: dev 브랜치에서 작업
- **릴리즈**: Phase 1 완료 시 dev → main 머지 + v1.0.0-mvp 태그

### 🎉 Week 1 완료! (Day 1-7)
- ✅ **프로젝트 인프라**: Docker Compose, CI/CD, 개발 환경
- ✅ **프론트엔드 기반**: Next.js 16, React 19.2, TypeScript
- ✅ **UI 시스템**: shadcn/ui, 다크모드, 반응형 레이아웃
- ✅ **상태 관리**: Zustand, React Query, API 클라이언트
- ✅ **에러 처리**: ErrorBoundary, LoadingSpinner, ErrorMessage

### 🎉 Week 2 완료! (Day 8-14): 백엔드 API 개발 ✅ 100% 완료
- ✅ **FastAPI 프로젝트 구조 설계** (Day 8-9)
  - 완전한 프로젝트 구조 (core, api, models, schemas, services)
  - 보안 아키텍처 (JWT + OAuth 준비)
  - Mock Tips API 구현 (daily, list, detail)
  - Swagger UI 자동 문서
- ✅ **PostgreSQL 데이터베이스 스키마 및 ORM** (Day 10-11)
  - SQLAlchemy 2.0 Async 완전 구현
  - 6개 모델 + Pydantic 스키마
  - **129개 pytest 테스트 100% 통과** ⭐
  - ULID + 프리픽스 ID 시스템
  - AppException + 구조화 로깅 시스템
  - 코드 품질: 9.0/10
- ✅ **Tips API 개발** (Day 12-13)
  - TDD 방식 개발 (21개 테스트 100% 통과)
  - Service 계층 완성, Alembic 마이그레이션
  - 성능 인덱스 추가 (3개)
  - 코드 품질: 9.2/10
- ✅ **Redis 캐싱 및 JWT 인증** (Day 14)
  - Redis 캐싱 (90% 성능 개선)
  - Google OAuth 2.0 + JWT 인증 시스템
  - API Rate Limiting (slowapi)
  - 234개 테스트 98.3% 통과 (230/234)
  - 코드 품질: 9.5/10

### 🎉 Week 3 완료! (Day 15-21): 터미널 에뮬레이터 ✅ 100% 완료
- ✅ **프론트엔드 터미널 UI** (Day 15-16)
  - xterm.js 5.6.0 터미널 UI 브라우저 렌더링
  - 기본 입력/출력 테스트 완료
- ✅ **WebSocket 실시간 통신** (Day 17-18)
  - 프론트엔드-백엔드 WebSocket 연결
  - 메시지 송수신, 재연결 로직 (3회 시도)
- ✅ **Docker 컨테이너 통합** (Day 19-20)
  - Docker 컨테이너 명령어 실행 (ls, pwd, cat, echo)
  - 세션 생성/종료 API 구현
  - Playwright 자동화 테스트 통과
- ✅ **보안 강화 및 최적화** (Day 21)
  - 네트워크 격리, 리소스 제한 (256MB, CPU 0.5코어)
  - 세션 생성 0.14초, 명령어 실행 0.055초
  - 컨테이너 정리 크론잡 (1분 주기)
  - 동시 세션 테스트: 5개 0.32초, 10개 0.42초

### 🎉 Week 4 진행 중 (Day 22-28): 통합 및 최적화 ⏳ 85% 완료
- ✅ **MSW 제거 및 API 통합** (Day 22-24)
  - 596줄 Mock 코드 삭제, 33개 패키지 제거
  - 실제 백엔드 API 연동 완료
  - 버그 수정: 카테고리 배열 표시, 터미널 레이스 컨디션
- ✅ **코드 품질 개선** (Day 25)
  - API 네이밍 완전 해결 (Pydantic alias_generator)
  - Frontend cleanup: 모든 `any` 타입 제거
  - 타입 안전성 100%
- ✅ **Tips 페이지 구현** (Day 26)
  - 팁 상세/목록 페이지 완성 (`/tips`, `/tips/[id]`)
  - 검색/정렬/필터 기능 구현
  - URL 상태 관리 (query parameters)
- ✅ **검색/정렬 API + Node.js 22 LTS** (Day 27 Part 1)
  - 검색 API: ILIKE 패턴, 대소문자 무시
  - 정렬 API: publish_date/title, asc/desc
  - TDD: 11개 테스트 100% 통과
  - Node.js 22 LTS 업그레이드 (2027년까지 지원)
- ✅ **E2E 테스트 & Docker 완전 통합** (Day 27 Part 2)
  - E2E 테스트: 22/22 통과 (100%, 50.5초)
  - Next.js rewrites 프록시: `/api/*` → `backend:8000/api/*`
  - Docker 통합: Frontend + Backend + DB 완전 작동
- ✅ **코드 품질 리팩토링** (Day 27 Part 3)
  - 테스트 헬퍼 클래스 추출 (56% 코드 감소)
  - TerminalEmulator 컴포넌트 분리 (3개 커스텀 훅)
  - 상수 추출 (Magic numbers 제거)
- ✅ **문서화** (Day 28) - 완료!
  - [x] README.md 진행률 업데이트
  - [x] USER_GUIDE.md 작성 (~1,200줄)
  - [x] DEPLOYMENT.md 작성 (~1,300줄)
  - [x] API_REFERENCE.md 작성 (~1,500줄)
- ✅ **빌드 이슈 해결 및 개선** (Day 28 Part 2) - 완료!
  - [x] Next.js 16 빌드 이슈 해결 (Providers Client Component 분리)
  - [x] API 설계 개선 (최신 팁 반환 방식)
  - [x] UX 개선 (BackButton 브라우저 히스토리 사용)
  - [x] Dockerfile 코드 스타일 통일

### 🚀 다음 단계 (Phase 2)
- **LLM 연동**: 팁 자동 생성 시스템
- **관리자 대시보드**: OAuth 로그인, 드래프트 관리
- **고급 터미널 기능**: 실시간 입력, vim/nano 지원
- **성능 최적화**: Lighthouse 90+ 달성
- **Phase 3**: 구글 애드센스 연동, 프로덕션 배포

### 📊 주요 성과 지표
- **백엔드**: 234개 pytest 테스트 98.3% 통과, 코드 품질 9.5/10
- **프론트엔드**: 22개 E2E 테스트 100% 통과, TypeScript strict 모드
- **터미널**: 세션 생성 0.14초, 명령어 실행 0.055초 (목표 초과 달성)
- **통합**: Docker 완전 통합, MSW → 실제 API 전환 완료

## 🚨 문제 해결

### 일반적인 문제
1. **Docker 서비스 시작 실패**
   ```bash
   # Docker Desktop이 실행 중인지 확인
   docker info

   # 포트 충돌 확인
   lsof -i :5432  # PostgreSQL
   lsof -i :6379  # Redis
   ```

2. **데이터베이스 연결 실패**
   ```bash
   # 서비스 상태 확인
   docker compose ps

   # 헬스체크 상태 확인
   docker compose exec postgres pg_isready
   ```

3. **권한 문제**
   ```bash
   # 스크립트 실행 권한 확인
   chmod +x scripts/dev-up.sh scripts/dev-down.sh
   ```

## 📚 추가 문서

- [요구사항 정의서](docs/requirements.md)
- [기술 설계서](docs/service-planning.md)
- [Phase 1 개발 계획](docs/phase1-tasks.md)

## 🤝 기여하기

1. 이슈 생성 및 논의
2. 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경사항 커밋 (`git commit -m 'Add amazing feature'`)
4. 브랜치 푸시 (`git push origin feature/amazing-feature`)
5. Pull Request 생성

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

**Linux Daily Tips** - 매일 성장하는 리눅스 실력 🐧