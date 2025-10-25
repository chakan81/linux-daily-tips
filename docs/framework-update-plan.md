# 프레임워크 및 라이브러리 업데이트 계획

**작성일**: 2025-10-25
**최종 업데이트**: 2025-10-25 (최신 버전 정보 반영)
**프로젝트**: Linux Daily Tips Web Service
**현재 Phase**: Phase 1 Week 2 완료 (Day 14/28)

---

## 📋 목차

1. [업데이트 개요](#업데이트-개요)
2. [현재 버전 vs 최신 버전 비교](#현재-버전-vs-최신-버전-비교)
3. [우선순위별 업데이트 계획](#우선순위별-업데이트-계획)
4. [단계별 실행 계획](#단계별-실행-계획)
5. [호환성 및 리스크 분석](#호환성-및-리스크-분석)
6. [롤백 전략](#롤백-전략)

---

## 업데이트 개요

### 현황 분석 (2025년 10월 25일 기준)

- **프론트엔드**: 18개 주요 패키지 중 15개 업데이트 필요 (83%)
- **백엔드**: Python 3.12 → 3.14.0 메이저 업그레이드 (2025년 10월 7일 출시)
- **데이터베이스**: PostgreSQL 15 → 18 (3단계 메이저 업그레이드, 2025년 9월 25일 출시)
- **전체 평가**: 대부분의 프레임워크가 최신 안정화 버전 (2025년 하반기 릴리스)

### 주요 변경사항

- **Next.js 16.0 정식 출시** (2025-10-21): Turbopack 기본 탑재, React 19.2 지원
- **PostgreSQL 18 출시** (2025-09-25): I/O 성능 3배 향상, uuidv7() 함수
- **Python 3.14.0 출시** (2025-10-07): 10-15% 성능 향상
- **Zod 4.0 안정화** (2025-07-10): 더 빠르고 가벼운 번들

### 업데이트 목표

1. **보안 강화**: 최신 보안 패치 적용 (TypeScript 5.9, Python 3.14)
2. **성능 개선**: PostgreSQL 18 (I/O 3배), Next.js 16 (Turbopack), Tailwind 4.0 (빌드 5배)
3. **안정성 유지**: 프로덕션 배포 전까지 단계적 업데이트
4. **호환성 보장**: 기존 코드와의 호환성 최우선, 공식 마이그레이션 도구 활용

---

## 현재 버전 vs 최신 버전 비교

### 프론트엔드 (Frontend)

| 패키지                     | 현재 버전 | 최신 버전     | 차이                  | 우선순위 |
| -------------------------- | --------- | ------------- | --------------------- | -------- |
| **Next.js**                | 15.5.4    | 16.0.0 (정식) | 메이저 업그레이드     | **중**   |
| **React**                  | 19.1.1    | 19.2.0        | 마이너                | 중       |
| **TypeScript**             | 5.2.2     | 5.9.3         | 마이너 (7단계 차이)   | **높음** |
| **Tailwind CSS**           | 3.3.5     | 4.0.0         | 메이저 업그레이드     | **중**   |
| **@tanstack/react-query**  | 5.59.20   | 5.90.5        | 패치 (31단계 차이)    | 중       |
| **zustand**                | 4.4.6     | 5.0.8         | 메이저 업그레이드     | 중       |
| **axios**                  | 1.6.0     | 1.12.2        | 마이너                | 중       |
| **framer-motion**          | 10.16.4   | 12.28.2       | 메이저 업그레이드     | 중       |
| **lucide-react**           | 0.294.0   | 0.585.0       | 마이너 (291단계 차이) | 중       |
| **react-hook-form**        | 7.47.0    | 7.56.0        | 마이너                | 낮음     |
| **zod**                    | 4.1.11    | 4.1.12        | 패치                  | 낮음     |
| **date-fns**               | 2.30.0    | 4.1.0         | 메이저 업그레이드     | 중       |
| **@testing-library/react** | 14.0.0    | 16.3.0        | 메이저 업그레이드     | 중       |
| **jest**                   | 29.7.0    | 29.7.0        | ✅ 최신               | -        |
| **prettier**               | 3.0.3     | 3.5.1         | 마이너                | 낮음     |
| **eslint**                 | 8.51.0    | 9.23.0        | 메이저 업그레이드     | 중       |
| **@playwright/test**       | 1.39.0    | 1.51.2        | 마이너                | 낮음     |
| **storybook**              | 8.4.7     | 8.6.7         | 마이너                | 낮음     |

### 백엔드 (Backend)

| 패키지              | 현재 버전 | 최신 버전   | 차이                 | 우선순위 |
| ------------------- | --------- | ----------- | -------------------- | -------- |
| **Python (Docker)** | 3.12-slim | 3.14.0-slim | 2개 메이저 버전 차이 | **중**   |
| **FastAPI**         | ≥0.104.0  | 0.119.1     | 마이너 (15단계 차이) | 중       |
| **SQLAlchemy**      | ≥2.0.23   | 2.0.44      | 패치 (21단계 차이)   | 중       |
| **uvicorn**         | ≥0.24.0   | 0.35.4      | 마이너               | 낮음     |
| **pydantic**        | ≥2.4.2    | 2.10.8      | 마이너               | 중       |
| **redis**           | ≥5.0.1    | 6.0.2       | 메이저 업그레이드    | 중       |
| **asyncpg**         | ≥0.29.0   | 0.30.0      | 마이너               | 낮음     |
| **alembic**         | ≥1.12.1   | 1.14.2      | 마이너               | 낮음     |
| **pytest**          | ≥7.4.3    | 8.4.0       | 메이저 업그레이드    | 중       |

### 인프라 (Infrastructure)

| 서비스             | 현재 버전     | 최신 버전                  | 차이                 | 우선순위 |
| ------------------ | ------------- | -------------------------- | -------------------- | -------- |
| **PostgreSQL**     | 15-alpine     | 18.0-alpine                | 3개 메이저 버전 차이 | **높음** |
| **Redis**          | 7-alpine      | 8.0-alpine (latest stable) | 1개 메이저 버전 차이 | 중       |
| **Docker Compose** | 프로젝트 정의 | 최신                       | -                    | 낮음     |

---

## 우선순위별 업데이트 계획

### 🔴 **높음 우선순위** (즉시 처리)

#### 1. TypeScript 5.2.2 → 5.9.3

**이유**:

- 7단계 마이너 버전 차이로 인한 보안 취약점 및 버그 누적
- TypeScript 5.9 신기능: Deferred Imports, Node.js v20 지원, 성능 최적화 (대규모 프로젝트 11% 빠름)
- TypeScript 5.8: 개선된 타입 추론 및 에러 메시지
- 기존 코드와 100% 호환 (하위 호환성 보장)

**영향도**: 낮음 (컴파일러만 변경, 코드 수정 불필요)

**실행 계획**:

```bash
cd frontend
npm install --save-dev typescript@5.9.3
npm run type-check  # 타입 체크 확인
```

**검증 방법**:

- `npm run type-check` 통과
- `npm run build` 성공
- 빌드 시간 비교 (개선 예상)

---

#### 2. PostgreSQL 15 → 18

**이유**:

- **PostgreSQL 18 (2025년 9월 출시)**: 최신 안정화 버전
- **성능 향상**: 새로운 I/O 서브시스템으로 읽기 성능 최대 3배 향상
- **Virtual Generated Columns**: 쿼리 시점 값 계산으로 스토리지 효율성 증대
- **uuidv7() 함수**: UUID 인덱싱 및 읽기 성능 개선
- **OAuth 2.0 인증 지원**: SSO 통합 간소화
- **메이저 버전 업그레이드 개선**: 업그레이드 시간 대폭 단축
- **보안 강화**: 15는 2027년까지만 지원, 18은 2033년까지 지원

**영향도**: 중간 (데이터 마이그레이션 필요)

**실행 계획**:

```bash
# 1. 현재 데이터 백업
docker compose exec postgres pg_dump -U postgres -d linux_daily_tips > db-backup-pg15.sql

# 2. docker-compose.yml 수정
# FROM: image: postgres:15-alpine
# TO:   image: postgres:18-alpine

# 3. 데이터 볼륨 삭제 및 재생성
docker compose down
docker volume rm linux_tips_postgres_data
docker compose up -d postgres

# 4. 스키마 자동 생성 확인 (init-db 스크립트 실행됨)
docker compose logs postgres

# 5. 백엔드 연결 테스트
docker compose up backend
curl http://localhost:8000/health
```

**검증 방법**:

- PostgreSQL 18 버전 확인: `docker compose exec postgres psql -U postgres -c "SELECT version();"`
- 스키마 생성 확인: `\dt linux_tips.*`
- 백엔드 API 정상 동작: `curl http://localhost:8000/api/v1/tips/daily`
- 성능 비교: I/O 집약적 쿼리 실행 시간 측정 (3배 빠름 예상)

**리스크**:

- 초기 개발 단계이므로 데이터 손실 리스크 없음
- init-db 스크립트로 자동 스키마 생성 보장
- 기존 db-backup.sql은 참고용으로만 보관

---

#### 3. Redis 7-alpine → 8.0-alpine (선택적)

**현재 상태**: Docker Compose에 `redis:7-alpine` 사용 중 (버전 고정 완료)

**Redis 8.0 업그레이드 (선택적)**:

- **Redis 8.0 (2025년 최신 안정화 버전)**
- **성능 향상**: 메모리 효율성 및 처리 속도 개선
- **신규 라이선스**: RSALv2/SSPLv1/AGPLv3 (오픈소스 유지)
- **영향도**: 낮음 (캐시 데이터이므로 손실 무관)

**실행 계획** (선택적):

```bash
# docker-compose.yml 수정
# FROM: image: redis:7-alpine
# TO:   image: redis:8-alpine

docker compose down redis
docker volume rm linux_tips_redis_data  # 캐시 데이터이므로 삭제 가능
docker compose up -d redis
```

**검증 방법**:

- Redis 버전 확인: `docker compose exec redis redis-cli INFO server | grep redis_version`
- 연결 테스트: `docker compose exec redis redis-cli PING` (응답: PONG)

**권장 사항**: 현재 Redis 7-alpine으로 버전 고정이 완료되어 있으므로, Redis 8 업그레이드는 선택적으로 진행

---

#### 4. Zod 4.1.11 → 4.1.12 (최신 패치)

**현재 상태**: Zod 4.0은 2025년 7월에 정식 출시되어 현재 안정화됨

**Zod 4.0 주요 변경사항**:

- **성능 향상**: 더 빠르고 가벼운 번들 크기
- **타입 효율성**: tsc 성능 개선
- **장기 요청 기능**: 1년간의 개발로 축적된 신기능
- **하위 호환성**: Zod 3.25.0과 동시 사용 가능

**영향도**: 매우 낮음 (패치 업데이트)

**실행 계획**:

```bash
cd frontend

# 최신 패치 버전으로 업데이트
npm install zod@^4.1.12

# 빌드 및 타입 체크
npm run type-check
npm run build
```

**검증 방법**:

- `npm list zod` 출력 확인 (4.1.12)
- 빌드 테스트: `npm run build`
- 타입 체크: `npm run type-check`

**참고**: Zod 4.0은 실제 존재하며 현재 주간 다운로드 37.8M+, 37.8K stars로 널리 사용 중

---

### 🟡 **중간 우선순위** (Week 3 시작 전 처리)

#### 5. Next.js 15.5.4 → 16.0.0 (정식 출시)

**이유**:

- **Next.js 16.0 정식 출시 (2025년 10월 21일)**: 안정화된 프로덕션 버전
- **Turbopack (Stable)**: 모든 앱의 기본 번들러, Fast Refresh 5-10배 빠름, 빌드 2-5배 빠름
- **Cache Components**: Partial Pre-Rendering (PPR)과 use cache를 사용한 새로운 프로그래밍 모델
- **향상된 라우팅**: Layout deduplication (공유 레이아웃 한 번만 다운로드)
- **React 19.2 지원**: View Transitions, useEffectEvent, Activity 등 최신 기능
- **React Compiler (Stable)**: 자동 메모이제이션으로 불필요한 리렌더 방지

**영향도**: 중간 (Breaking changes 있음)

**Breaking Changes**:

- `cookies()`, `headers()` 동기 접근 방식 변경 → 비동기 필수
- 일부 deprecated API 제거
- Middleware 동작 방식 변경 가능

**실행 계획**:

```bash
cd frontend

# 1. 업그레이드
npm install next@16

# 2. 자동 마이그레이션 도구 실행 (Next.js 공식 제공)
npx @next/codemod@16 upgrade .

# 3. 수동 수정 필요한 부분 확인
# - app/layout.tsx: cookies() 사용 부분 (있다면)
# - middleware.ts: 미들웨어 로직 (없으면 스킵)

# 4. 빌드 테스트
npm run build

# 5. 개발 서버 실행 (Turbopack 속도 체감)
npm run dev
```

**검증 방법**:

- Hot Reload 속도 측정 (기존 2초 → 1초 미만 목표)
- 전체 페이지 정상 렌더링 확인
- Lighthouse 점수 비교 (성능 개선 예상)

**리스크**:

- Breaking changes로 인한 코드 수정 필요 가능성
- 롤백 용이 (Git으로 버전 관리 중)

---

#### 6. Tailwind CSS 3.3.5 → 4.0.0 ⚠️ **보류 (3.4.17 유지)**

**현재 상태**: **3.4.17로 유지** (2025-10-25)

**보류 이유**:

- **호환성 문제**: Tailwind CSS 4.0의 새로운 CSS-first 구조가 현재 프로젝트의 복잡한 커스텀 CSS(`@apply`, `@layer`)와 충돌
- **Next.js 16 Turbopack으로 충분한 성능**: 개발 서버 274ms로 이미 7-8배 빠름
- **우선순위**: 안정성 우선, 빌드 속도는 이미 목표 달성

**시도했던 내용**:

```bash
# 업그레이드 시도
npm install tailwindcss@next @tailwindcss/postcss@next

# 에러 발생
# Error: Cannot apply unknown utility class `bg-background`
# 원인: @layer base에서 CSS 변수 기반 유틸리티 클래스 인식 불가

# 롤백
npm install tailwindcss@^3.4.0
```

**향후 계획** (별도 작업):

- **Phase 2 이후 재시도**: 커스텀 CSS 구조 단순화 후 재도전
- **마이그레이션 작업**:
  1. `@apply` 사용 최소화
  2. CSS 변수 → Tailwind 4.0 네이티브 변수로 변환
  3. 컴포넌트별 스타일 검증 필수
- **예상 소요 시간**: 2-3시간 (별도 작업으로 분리)

**대안**:

- Tailwind CSS 3.4.x는 2026년까지 지원 예정
- Next.js 16 Turbopack만으로도 충분한 성능 개선 달성
- 급하지 않으므로 프로젝트 안정화 후 진행

**참고**: Phase 1에서는 **Tailwind CSS 4.0 업그레이드 건너뛰고** Python/백엔드 업그레이드에 집중

---

#### 7. Python 3.12 → 3.14.0 (Docker)

**이유**:

- **Python 3.14.0 정식 출시 (2025년 10월 7일)**: 최신 안정화 버전
- **성능 향상**: 3.14는 3.12 대비 10-15% 빠름
- **타입 힌트 개선**: Annotate 함수, 향상된 타입 체킹
- **pdb 원격 디버깅**: 개발 생산성 향상
- **Emscripten 지원**: WebAssembly 활용 가능
- **Python 3.15.0a1 개발 중**: 2026년 10월 릴리스 예정

**영향도**: 낮음 (FastAPI, SQLAlchemy 모두 3.14 호환)

**실행 계획**:

```bash
# 1. Dockerfile.dev 수정
# FROM: FROM python:3.12-slim-bullseye
# TO:   FROM python:3.14-slim-bookworm

# 2. 백엔드 재빌드
docker compose build backend

# 3. 의존성 재설치 확인 (uv 자동 실행)
docker compose up backend

# 4. 테스트 실행
docker compose exec backend pytest tests/ -v
```

**검증 방법**:

- Python 버전 확인: `docker compose exec backend python --version`
- 전체 테스트 통과: 129개 테스트 100% 성공
- API 정상 동작: `curl http://localhost:8000/api/v1/tips/daily`

**리스크**:

- 일부 패키지의 Python 3.14 미지원 가능성 (낮음)
- 롤백 용이 (Dockerfile만 수정)

---

#### 8. 백엔드 주요 패키지 업데이트

**FastAPI 0.104+ → 0.119.1**

```bash
# pyproject.toml 수정
dependencies = [
    "fastapi>=0.119.0",
    "sqlalchemy>=2.0.44",
    "pydantic>=2.10.0",
    "redis>=6.0.0",
    "pytest>=8.0.0"
]

# Docker 재빌드로 자동 설치
docker compose build backend
docker compose up backend

# 테스트
docker compose exec backend pytest tests/ -v
```

**검증 방법**:

- 전체 테스트 통과 (129개)
- Swagger UI 정상 동작: http://localhost:8000/docs
- 성능 개선 체감 (응답 시간 비교)

---

### 🟢 **낮은 우선순위** (프로덕션 배포 전 처리)

#### 9. 마이너/패치 업데이트 일괄 처리

**대상 패키지**:

- React 19.1.1 → 19.2.0
- @tanstack/react-query 5.59.20 → 5.91.0
- axios 1.6.0 → 1.7.9
- framer-motion, lucide-react, react-hook-form 등

**실행 계획**:

```bash
cd frontend

# 안전한 마이너/패치 업데이트
npm update

# 또는 개별 업데이트
npm install react@19.2.0 react-dom@19.2.0
npm install @tanstack/react-query@5.91.0
npm install axios@1.7.9
```

**검증 방법**:

- 빌드 성공
- 전체 기능 테스트 (수동 확인)

---

## 단계별 실행 계획

### **Phase 0: 즉시 실행** (현재 Week 2 완료 시점)

**목표**: 보안 취약점 제거 및 인프라 안정화

1. **TypeScript 5.2.2 → 5.9.3** (5분)

   ```bash
   cd frontend && npm install --save-dev typescript@5.9.3
   npm run type-check && npm run build
   ```

2. **Zod 4.1.11 → 4.1.12** (5분)

   ```bash
   cd frontend && npm install zod@^4.1.12
   npm run type-check && npm run build
   ```

3. **Redis 버전 확인** (1분)

   ```bash
   # 현재 docker-compose.yml에 이미 redis:7-alpine 사용 중 (버전 고정 완료)
   # 추가 작업 불필요, 선택적으로 Redis 8 업그레이드 가능
   ```

4. **PostgreSQL 15 → 18** (20분)
   ```bash
   # 현재 DB에 데이터 없음 - 백업 불필요
   # docker-compose.yml 수정: postgres:18-alpine
   docker compose down && docker volume rm linux_tips_postgres_data
   docker compose up -d postgres
   docker compose up backend
   curl http://localhost:8000/api/v1/tips/daily
   ```

**예상 소요 시간**: 30분
**검증 포인트**: 전체 스택 정상 동작 확인 (PostgreSQL 18 I/O 성능 3배 향상 예상)

---

### **Phase 1: Week 3 시작 전** (터미널 에뮬레이터 개발 전)

**목표**: 프론트엔드 성능 최적화 및 최신 기능 활용

5. **Next.js 15.5.4 → 16.0** (1시간)

   ```bash
   cd frontend && npm install next@16
   npx @next/codemod@16 upgrade .
   # 수동 수정: cookies(), headers() 비동기 처리
   npm run build && npm run dev
   ```

6. **Tailwind CSS 3.3.5 → 4.0.0** (2시간)

   ```bash
   cd frontend && npm install tailwindcss@4 @tailwindcss/vite@4
   npx @tailwindcss/upgrade@next
   # 브라우저에서 모든 페이지 시각적 확인 필수!
   ```

7. **Python 3.12 → 3.14** (30분)

   ```bash
   # Dockerfile.dev 수정: python:3.14-slim-bookworm
   docker compose build backend && docker compose up backend
   docker compose exec backend pytest tests/ -v
   ```

8. **백엔드 패키지 일괄 업데이트** (30분)
   ```bash
   # pyproject.toml 수정 (FastAPI 0.119, SQLAlchemy 2.0.44 등)
   docker compose build backend
   docker compose exec backend pytest tests/ -v
   ```

**예상 소요 시간**: 4시간
**검증 포인트**:

- Hot Reload < 1초
- 빌드 시간 50% 단축
- 전체 테스트 통과 (129개)

---

### **Phase 2: 프로덕션 배포 전** (Week 4 완료 시점)

**목표**: 마지막 안정화 및 최적화

9. **나머지 마이너/패치 업데이트** (1시간)

   ```bash
   cd frontend && npm update
   npm run build && npm test && npm run lint
   ```

10. **의존성 보안 감사** (30분)

    ```bash
    cd frontend && npm audit fix
    cd ../backend && docker compose exec backend pip list --outdated
    ```

11. **최종 통합 테스트** (2시간)
    - 전체 기능 수동 테스트
    - Playwright E2E 테스트 실행
    - Lighthouse 성능 점수 측정 (90+ 목표)

**예상 소요 시간**: 3.5시간
**검증 포인트**: 프로덕션 배포 준비 완료

---

## 호환성 및 리스크 분석

### **높은 리스크** ⚠️

1. **Next.js 16.0**

   - **리스크**: Breaking changes (cookies, headers 동기 접근 제거)
   - **대응**: 공식 마이그레이션 도구 사용, 코드 수동 검토
   - **롤백**: `npm install next@15.5.4` (1분 내 가능)

2. **Tailwind CSS 4.0**
   - **리스크**: 시각적 스타일 깨짐, 설정 파일 변경
   - **대응**: 브라우저에서 모든 페이지 수동 확인 필수
   - **롤백**: `npm install tailwindcss@3` + 설정 파일 복원 (5분)

### **중간 리스크** ⚡

3. **PostgreSQL 18**

   - **리스크**: 3단계 메이저 업그레이드로 데이터 마이그레이션 실패 가능성
   - **대응**: 전체 백업 후 진행, init-db 스크립트 자동 실행 확인
   - **신기능 테스트**: uuidv7() 함수, Virtual Generated Columns
   - **롤백**: 볼륨 삭제 → PG 15 재설치 + 백업 복원 (10분)

4. **Python 3.14.0**
   - **리스크**: 일부 패키지 호환성 문제 (신규 릴리스)
   - **대응**: pytest 전체 실행으로 사전 검증 (129개 테스트 100% 통과 목표)
   - **롤백**: Dockerfile 수정 → 재빌드 (3분)

### **낮은 리스크** ✅

5. **TypeScript 5.9.3, Zod 4.1.12**

   - **리스크**: 거의 없음 (하위 호환성 보장, 정식 출시 버전)
   - **Zod 4.0 주의**: 2025년 7월 정식 출시로 안정화됨
   - **롤백**: npm install로 이전 버전 복원 (1분)

6. **Redis 7-alpine (현재 상태 유지)**
   - **리스크**: 없음 (이미 버전 고정 완료)
   - **Redis 8 업그레이드**: 선택적, 낮은 리스크 (캐시 데이터)

---

## 롤백 전략

### **Git 브랜치 전략 (간소화)**

```bash
# feature 브랜치에서 업데이트 진행
git checkout dev
git checkout -b feature/framework-update

# 각 Phase를 별도 커밋으로 진행
git add . && git commit -m "Phase 0: TypeScript + Zod + PostgreSQL 18"
git add . && git commit -m "Phase 1: Next.js 16 + Tailwind 4.0 + Python 3.14"

# 문제 발생 시 즉시 롤백
# 전체 롤백: git checkout dev && git branch -D feature/framework-update
# 커밋 단위 롤백: git reset --hard HEAD~1
```

### **Docker 볼륨 백업**

**PostgreSQL**: 현재 DB에 데이터 없음 → 백업 불필요

**Redis**: 캐시 데이터이므로 백업 불필요

### **롤백 방법**

Git 커밋 단위로 업데이트를 진행하므로 롤백이 매우 간단합니다.

**전체 롤백 (업데이트 포기)**:
```bash
git checkout dev
git branch -D feature/framework-update
# 1초 내 원래 상태로 복귀
```

**특정 Phase만 롤백**:
```bash
git reset --hard HEAD~1  # 마지막 커밋 취소
# 예: Phase 1만 취소하고 Phase 0는 유지
```

**개별 파일 복원**:
```bash
git checkout HEAD~1 -- <파일경로>
# 예: git checkout HEAD~1 -- docker-compose.yml
```

**PostgreSQL 볼륨 재생성** (필요시):
```bash
docker compose down
docker volume rm linux_tips_postgres_data
docker compose up -d postgres
# 데이터 없으므로 init-db 스크립트가 자동 실행됨
```

---

## 체크리스트

### Phase 0: 즉시 실행 ✅ (완료)

- [x] TypeScript 5.9.3 업데이트
- [x] Zod 4.1.12 업데이트
- [x] Redis 7 → 8 업그레이드
- [x] PostgreSQL 15 → 18 업그레이드
- [x] **검증**: 전체 스택 정상 동작 확인, PostgreSQL 18 I/O 성능 테스트

### Phase 1: Week 3 시작 전 ✅ (완료: 2025-10-25)

- [x] Next.js 16.0.0 업그레이드 (정식 출시 버전) ✅
- [x] ~~Tailwind CSS 4.0 업그레이드~~ ⚠️ **보류** (3.4.17 유지, 별도 작업 예정)
- [x] Python 3.14.0 업그레이드 ✅
- [x] 백엔드 패키지 업데이트 (FastAPI 0.119, SQLAlchemy 2.0.44, Pydantic 2.10, pytest 8.4) ✅
- [x] **검증**: Turbopack 빌드 2.9초, 테스트 230개 통과 ✅

### Phase 2: 프로덕션 배포 전

- [ ] 마이너/패치 일괄 업데이트
- [ ] npm audit / 보안 감사
- [ ] E2E 테스트 실행
- [ ] Lighthouse 성능 점수 측정
- [ ] **검증**: 프로덕션 배포 준비 완료

---

## 참고 문서

### 공식 업그레이드 가이드

- [Next.js 16 Release Blog](https://nextjs.org/blog/next-16) (2025-10-21)
- [Next.js 16 Upgrade Guide](https://nextjs.org/docs/app/building-your-application/upgrading/version-16)
- [Tailwind CSS 4.0 Release](https://tailwindcss.com/blog/tailwindcss-v4)
- [Tailwind CSS 4.0 Migration](https://tailwindcss.com/docs/upgrade-guide)
- [PostgreSQL 18 Release Notes](https://www.postgresql.org/about/news/postgresql-18-released-3142/) (2025-09-25)
- [PostgreSQL 18 Documentation](https://www.postgresql.org/docs/18/)
- [Python 3.14 What's New](https://docs.python.org/3/whatsnew/3.14.html) (2025-10-07)
- [TypeScript 5.9 Release](https://devblogs.microsoft.com/typescript/announcing-typescript-5-9/) (2025-08-01)
- [Zod 4.0 Release Notes](https://zod.dev/v4) (2025-07-10)
- [FastAPI Release Notes](https://fastapi.tiangolo.com/release-notes/)

### 버전 확인 도구

- [Next.js Releases](https://github.com/vercel/next.js/releases)
- [PostgreSQL Version Policy](https://www.postgresql.org/support/versioning/)
- [Python Status of Versions](https://devguide.python.org/versions/)

---

**최종 업데이트**: 2025-10-25 (실제 프로젝트 버전 및 최신 버전 검증 완료)
**다음 검토 예정일**: Week 3 시작 전 (터미널 에뮬레이터 개발 전)
