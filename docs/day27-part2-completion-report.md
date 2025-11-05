# Day 27 Part 2 완료 보고서

**날짜**: 2025-11-05
**작업**: Frontend Dockerization + E2E Testing
**상태**: ✅ **완료** (100%)

---

## 📋 작업 요약

Next.js rewrites 프록시 방식으로 Frontend-Backend API 연동 완료 및 E2E 테스트 100% 통과 달성.

---

## 🎯 달성한 목표

### 1. ✅ E2E 테스트 100% 통과 (22/22)
- **이전**: 8/22 통과 (36%)
- **현재**: 22/22 통과 (100%) 🎉
- **테스트 시간**: 50.5초

### 2. ✅ 브라우저 API 연동 완료
- 홈페이지에서 오늘의 팁 정상 표시
- 최근 팁 5개 카드 정상 표시
- 모든 API 요청 200 OK 응답

### 3. ✅ Docker 환경 변수 설정 완료
- `NEXT_PUBLIC_API_URL=""` (빈 문자열)
- `API_BACKEND_URL=http://backend:8000`
- Next.js rewrites 프록시로 `/api/*` → `backend:8000/api/*` 자동 전달

---

## 🔧 수행한 작업

### Step 1: next.config.js 수정
**문제**: `||` 연산자가 빈 문자열을 falsy로 취급하여 폴백 값 사용

**파일**: `frontend/next.config.js` (31-39줄)

**수정 전**:
```javascript
env: {
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  NEXT_PUBLIC_APP_ENV: process.env.NEXT_PUBLIC_APP_ENV || 'development',
},
```

**수정 후**:
```javascript
// Environment variables validation
// NOTE: NEXT_PUBLIC_* variables are automatically exposed to the browser
// Empty string is allowed for NEXT_PUBLIC_API_URL (uses Next.js rewrites proxy)
env: {
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL !== undefined
    ? process.env.NEXT_PUBLIC_API_URL
    : 'http://localhost:8000',
  NEXT_PUBLIC_APP_ENV: process.env.NEXT_PUBLIC_APP_ENV || 'development',
},
```

**이유**: `!== undefined` 체크로 변경하여 빈 문자열 `""`을 허용

### Step 2: Frontend 컨테이너 재빌드
```bash
docker-compose stop frontend && \
docker-compose rm -f frontend && \
docker-compose up -d --build frontend
```

**빌드 시간**: ~40초

### Step 3: 환경 변수 검증
```bash
# 컨테이너 내부 환경 변수 확인
$ docker-compose exec -T frontend node -e "console.log('NEXT_PUBLIC_API_URL:', JSON.stringify(process.env.NEXT_PUBLIC_API_URL))"
NEXT_PUBLIC_API_URL: ""  ✅

$ docker-compose exec -T frontend node -e "console.log('API_BACKEND_URL:', process.env.API_BACKEND_URL)"
API_BACKEND_URL: http://backend:8000  ✅
```

### Step 4: E2E 테스트 재실행
```bash
$ docker-compose exec -T frontend npx playwright test --project=chromium

Running 22 tests using 3 workers

  ✓  22 passed (50.5s)
```

**통과한 테스트**:
- Homepage (5개): 로드, 오늘의 팁, 최근 팁, View All Tips, 통계, CTA
- Terminal (6개): 로드, 세션 생성, ls/pwd/echo 실행, 세션 종료, 다중 명령어
- Tips Page (11개): 로드, 검색, 필터, 정렬, 페이지네이션, 상세 이동 등

### Step 5: 브라우저 수동 테스트 (Playwright MCP)
```bash
# 브라우저 접속: http://localhost:3000
```

**검증 결과**:
1. **환경 변수**: `✅ Environment variables validated successfully: {NEXT_PUBLIC_API_URL: , ...}`
2. **API 요청**:
   - `GET /api/v1/tips/daily` → 200 OK
   - `GET /api/v1/tips?page=1&page_size=3` → 200 OK
3. **UI 렌더링**:
   - 오늘의 팁: "ls 명령어로 파일 목록 보기" (beginner, file-system)
   - 최근 팁: 5개 카드 정상 표시
   - 모든 버튼 및 링크 정상 작동

---

## 📊 테스트 결과 비교

| 항목 | 이전 (Day 27 Part 1) | 현재 (Day 27 Part 2) | 개선율 |
|------|----------------------|----------------------|--------|
| **E2E 테스트** | 8/22 (36%) | 22/22 (100%) | **+178%** 🚀 |
| **브라우저 API** | ❌ 실패 (404) | ✅ 성공 (200) | **100%** |
| **환경 변수** | ❌ localhost:8000 | ✅ "" (빈 문자열) | **100%** |
| **Docker 통합** | ⚠️ 부분 작동 | ✅ 완전 작동 | **100%** |

---

## 🛠️ 기술 상세

### Next.js Rewrites 프록시 동작 원리

1. **클라이언트 (브라우저)**:
   - `NEXT_PUBLIC_API_URL=""` (빈 문자열)
   - Axios baseURL: `""` → 상대 경로 사용
   - API 요청: `/api/v1/tips/daily`

2. **Next.js 서버 (SSR/Middleware)**:
   - `rewrites()` 함수가 `/api/*` 요청을 감지
   - `API_BACKEND_URL=http://backend:8000` 사용
   - 프록시: `/api/v1/tips/daily` → `http://backend:8000/api/v1/tips/daily`

3. **백엔드 (FastAPI)**:
   - 요청 수신: `GET /api/v1/tips/daily`
   - 응답: 200 OK, JSON 데이터

4. **클라이언트 (브라우저)**:
   - Next.js 서버로부터 프록시된 응답 수신
   - React Query 캐싱 및 렌더링

### 환경 변수 우선순위

```
1. next.config.js env (가장 높음)
2. .env.local
3. process.env (docker-compose)
```

**핵심**: `next.config.js`의 `env` 섹션에서 `!== undefined` 체크가 필수!

---

## 📚 수정한 파일

| 파일 | 변경 내용 | 상태 |
|------|----------|------|
| `frontend/next.config.js` | `env` 섹션 수정 (빈 문자열 허용) | ✅ |
| `frontend/.env.local` | `NEXT_PUBLIC_API_URL=` 설정 (Day 27 Part 1) | ✅ |
| `docker-compose.yml` | 환경 변수 추가 (Day 27 Part 1) | ✅ |

---

## 🎓 학습한 교훈

### 1. JavaScript Falsy 값 처리
```javascript
// ❌ 잘못된 방법
const value = process.env.VAR || 'default';
// 빈 문자열 ""은 falsy이므로 'default' 사용

// ✅ 올바른 방법
const value = process.env.VAR !== undefined ? process.env.VAR : 'default';
// undefined만 체크하여 빈 문자열 허용
```

### 2. Next.js 환경 변수 우선순위
- `next.config.js` env > `.env.local` > `process.env`
- 클라이언트 번들에 포함되는 `NEXT_PUBLIC_*` 변수는 빌드 타임에 결정됨
- 컨테이너 재빌드 시 `.next` 폴더 캐시 주의

### 3. Docker 네트워크 vs localhost
- 브라우저 (호스트): `localhost:8000` → host의 8000 포트
- Docker 컨테이너: `localhost:8000` → 컨테이너 자신의 8000 포트
- 해결: Next.js rewrites로 서버 사이드 프록시 구현

### 4. Playwright E2E 테스트
- Docker 내부에서 실행되는 Playwright는 Docker 네트워크 사용
- 브라우저와 동일한 환경 변수 필요 (`NEXT_PUBLIC_*`)
- Next.js rewrites로 브라우저/Playwright 양쪽 지원

---

## 🚀 다음 단계 (Day 28)

### 1. 성능 최적화
- [ ] Lighthouse 점수 측정 (목표: 90+)
- [ ] 번들 사이즈 분석 (`ANALYZE=true npm run build`)
- [ ] 코드 분할 (Code Splitting) 적용
- [ ] 이미지 최적화 (Next.js Image component)

### 2. 문서화
- [ ] 사용자 가이드 작성
- [ ] API 문서 업데이트
- [ ] 배포 가이드 작성

### 3. 최종 점검
- [ ] 모든 페이지 수동 테스트
- [ ] 접근성 검사 (WCAG 2.1 AA)
- [ ] 보안 검사 (OWASP Top 10)

---

## 📈 프로젝트 진행률

### Phase 1 (MVP): **92% 완료** (90/98 작업)

#### ✅ Week 1 완료 (Day 1-7): 100%
- 프론트엔드 인프라 (Next.js 16, TypeScript, Tailwind CSS, shadcn/ui)
- 상태 관리 시스템 (Zustand + React Query)
- API 클라이언트 (Axios + 25+ endpoints)

#### ✅ Week 2 완료 (Day 8-14): 100%
- FastAPI 백엔드 개발 (234개 테스트 98.3% 통과)
- PostgreSQL 데이터베이스 스키마 및 ORM
- Redis 캐싱 및 JWT 인증
- Google OAuth 2.0

#### ✅ Week 3 완료 (Day 15-21): 100%
- 터미널 에뮬레이터 (xterm.js + WebSocket + Docker)
- 보안 강화 (네트워크 격리, 리소스 제한)
- 성능 최적화 (세션 생성 < 2초, 명령어 < 1초)

#### ✅ Week 4 진행 중 (Day 22-27): **92% 완료** (23/25 작업)
- ✅ Day 22-24: MSW 제거 및 API 통합 (12개)
- ✅ Day 25: 코드 품질 개선 (3개)
- ✅ Day 26: Tips 페이지 구현 (6개)
- ✅ **Day 27: E2E 테스트 & Docker 완전 통합** (2개) ⭐ **오늘 완료!**
  - ✅ 검색/정렬 API TDD 구현 (Day 27 Part 1)
  - ✅ E2E 테스트 22/22 통과 (Day 27 Part 2)
- ⏳ Day 28: 성능 최적화 & 문서화 (2개)

---

## 🎉 결론

**Day 27 Part 2 성과**:
- ✅ **E2E 테스트 100% 통과** (22/22, 50.5초)
- ✅ **브라우저 API 완전 작동** (오늘의 팁 + 최근 팁 5개)
- ✅ **Docker 환경 완전 통합** (Frontend + Backend + DB)
- ✅ **Next.js rewrites 프록시 완성** (브라우저/Playwright 양쪽 지원)

**핵심 교훈**:
- JavaScript falsy 값 처리에 주의 (`||` vs `!== undefined`)
- Next.js 환경 변수 우선순위 이해 (`next.config.js` > `.env.local`)
- Docker 네트워크 vs localhost 차이 이해
- Next.js rewrites로 서버 사이드 프록시 구현

**다음 목표**:
- Day 28: 성능 최적화 (Lighthouse 90+) 및 최종 문서화

---

**작성일**: 2025-11-05 20:50 (KST)
**작성자**: Claude Code
**소요 시간**: 약 15분 (next.config.js 수정 → 재빌드 → 테스트 → 검증)
