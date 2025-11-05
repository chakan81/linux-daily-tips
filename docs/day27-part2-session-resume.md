# Day 27 Part 2 - 세션 중단 및 재개 가이드

## 📋 현재 상황 요약

**날짜**: 2025-11-05
**작업**: Day 27 Part 2 - Frontend Dockerization + E2E Testing
**문제**: Playwright E2E 테스트 실패 (8/22 통과, 36%)

## 🔍 문제 분석

### 근본 원인
`next.config.js`의 `env` 섹션에서 빈 문자열을 falsy로 취급하여 폴백 값 사용:

```javascript
// ❌ 현재 코드 (문제)
env: {
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  // 빈 문자열 "" 은 falsy이므로 'http://localhost:8000'이 사용됨
}
```

### 증상
1. **브라우저에서**: `NEXT_PUBLIC_API_URL: 'http://localhost:8000'`로 설정됨 (로그 확인됨)
2. **컨테이너 내부**: `process.env.NEXT_PUBLIC_API_URL = ""`로 올바르게 설정됨
3. **Node.js fetch 테스트**: 성공 (API 200 응답)
4. **Playwright E2E 테스트**: 실패 - 브라우저가 잘못된 환경 변수 사용

## ✅ 완료된 작업

### 1. 환경 변수 설정 (docker-compose.yml)
```yaml
frontend:
  environment:
    NEXT_PUBLIC_API_URL: ""  # ✅ 빈 문자열 설정
    API_BACKEND_URL: http://backend:8000  # ✅ 서버 사이드 전용
```

### 2. 로컬 환경 파일 (.env.local)
```bash
# ✅ 빈 문자열로 설정 완료
NEXT_PUBLIC_API_URL=
NEXT_PUBLIC_BASE_URL=http://localhost:3000
```

### 3. Frontend 컨테이너 재빌드
```bash
# ✅ 완료
docker compose stop frontend && docker compose rm -f frontend && docker compose up -d --build frontend
```

### 4. 환경 변수 검증
```bash
# ✅ 컨테이너 내부에서 확인
docker compose exec -T frontend node -e "console.log('API_BACKEND_URL:', process.env.API_BACKEND_URL)"
# 출력: API_BACKEND_URL: http://backend:8000

docker compose exec -T frontend node -e "console.log('NEXT_PUBLIC_API_URL:', process.env.NEXT_PUBLIC_API_URL)"
# 출력: NEXT_PUBLIC_API_URL: (빈 문자열)
```

### 5. API 엔드포인트 테스트
```bash
# ✅ 성공
docker compose exec -T frontend node -e "fetch('http://localhost:3000/api/v1/tips/daily').then(r => r.json()).then(d => console.log(d))"
# 출력: Status: 200, Data: {...}
```

## ❌ 실패한 테스트 (8/22 통과)

### 통과한 테스트 (8개)
- ✅ 홈페이지가 정상적으로 로드된다
- ✅ 터미널 페이지가 정상적으로 로드된다
- ✅ 통계 섹션이 표시된다
- ✅ CTA 버튼이 작동한다
- ✅ 정렬 기능이 작동한다
- ✅ 페이지네이션이 작동한다
- ✅ 활성 필터를 제거할 수 있다
- ✅ "Clear All" 버튼이 모든 필터를 제거한다

### 실패한 테스트 (13개)
모든 실패는 **데이터 로딩 실패** 패턴:
- ❌ 오늘의 팁이 표시된다 (난이도 배지 없음)
- ❌ 최근 팁 섹션이 표시된다 (팁 링크 없음)
- ❌ "View All Tips" 링크가 작동한다 (버튼 없음)
- ❌ 터미널 세션을 생성할 수 있다 (.xterm-screen 없음)
- ❌ Tips 페이지가 정상적으로 로드된다 (팁 카드 없음)
- ❌ 검색 기능이 작동한다
- ❌ 난이도 필터가 작동한다
- ❌ 카테고리 필터가 작동한다
- ❌ 팁 카드를 클릭하면 상세 페이지로 이동한다
- ❌ ls/pwd/echo 명령어 실행 (터미널 로드 안됨)
- ❌ 여러 명령어를 순차적으로 실행할 수 있다

## 🔧 다음 작업 (재개 시 수행할 작업)

### Step 1: next.config.js 수정

**파일**: `frontend/next.config.js`
**위치**: 31-36줄

**현재 코드**:
```javascript
env: {
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  NEXT_PUBLIC_APP_ENV: process.env.NEXT_PUBLIC_APP_ENV || 'development',
},
```

**수정할 코드**:
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

**이유**: `||` 연산자는 빈 문자열을 falsy로 취급하므로, `!== undefined` 체크로 변경하여 빈 문자열을 허용해야 함.

### Step 2: Frontend 컨테이너 재빌드

```bash
cd /Users/chakan/Dev/WebDev/linux-daily-tips

# 컨테이너 완전 재빌드
docker compose stop frontend && docker compose rm -f frontend && docker compose up -d --build frontend

# 개발 서버 시작 대기 (약 10초)
sleep 10
```

### Step 3: 환경 변수 검증

```bash
# 로그에서 환경 변수 확인
docker compose logs frontend --tail=50 | grep "Environment variables validated"

# 기대 출력:
# ✅ Environment variables validated successfully: {
#   NEXT_PUBLIC_API_URL: '',  # ← 빈 문자열이어야 함!
#   NEXT_PUBLIC_BASE_URL: 'http://localhost:3000',
#   ...
# }
```

### Step 4: E2E 테스트 재실행

```bash
# Docker 내부에서 전체 테스트 실행
docker compose exec -T frontend npx playwright test --project=chromium

# 기대 결과: 22/22 통과 (100%)
```

### Step 5: 브라우저에서 수동 테스트

```bash
# 1. 브라우저 열기: http://localhost:3000
# 2. 개발자 도구 > Console 확인
# 3. 환경 변수 로그 확인:
#    ✅ Environment variables validated successfully: { NEXT_PUBLIC_API_URL: '' }
# 4. Network 탭에서 API 요청 확인:
#    ✅ /api/v1/tips/daily → 200 OK
```

## 📚 관련 파일

### 수정한 파일
1. `frontend/.env.local` - NEXT_PUBLIC_API_URL 빈 문자열로 설정 ✅
2. `docker-compose.yml` - NEXT_PUBLIC_API_URL="", API_BACKEND_URL 추가 ✅
3. `frontend/next.config.js` - **수정 필요** ❌ (Step 1에서 수행)

### 참고 파일
- `frontend/lib/env.ts` - 환경 변수 검증 스키마 (빈 문자열 허용 확인됨)
- `frontend/lib/api/client.ts` - Axios 클라이언트 (baseURL 설정)
- `frontend/playwright.config.ts` - Playwright 설정

## 🚨 주의사항

1. **빈 문자열 vs undefined**: JavaScript에서 `""` 는 falsy이므로 `||` 연산자 대신 `!== undefined` 사용 필수
2. **Next.js 빌드 캐시**: `.next` 폴더에 환경 변수가 캐시되므로 컨테이너 완전 재빌드 필수
3. **환경 변수 우선순위**: `.env.local` > `process.env` (docker-compose)
4. **NEXT_PUBLIC_* 변수**: 클라이언트 번들에 포함되므로 빌드 타임에 결정됨

## 📊 진행률

- **Day 27 Part 2**: 70% 완료 (3/4 단계)
  - ✅ Docker 환경 변수 설정
  - ✅ Frontend 컨테이너 빌드
  - ⏳ **next.config.js 수정 및 재빌드** ← 현재 위치
  - ⏳ E2E 테스트 100% 통과

## 🎯 최종 목표

- **E2E 테스트**: 22/22 통과 (100%)
- **브라우저**: Tips 데이터 정상 로딩
- **Playwright**: Docker 내부에서 모든 테스트 통과
- **다음 단계**: 성능 최적화 및 Lighthouse 점수 측정

---

**작성일**: 2025-11-05 20:36 (KST)
**작성자**: Claude Code (세션 중단 전)
