# Linux Daily Tips - API 레퍼런스

Linux Daily Tips 백엔드 REST API의 상세 사용 가이드입니다.

---

## 📚 목차

1. [개요](#-개요)
2. [인증](#-인증)
3. [공통 응답 형식](#-공통-응답-형식)
4. [엔드포인트](#-엔드포인트)
   - [Health Check](#1-health-check)
   - [Tips API](#2-tips-api)
   - [Authentication](#3-authentication-api)
   - [Terminal API](#4-terminal-api)
   - [Admin API](#5-admin-api)
5. [에러 코드](#-에러-코드)
6. [Rate Limiting](#-rate-limiting)

---

## 📖 개요

### Base URL

| 환경 | URL |
|------|-----|
| **개발** | `http://localhost:8000` |
| **프로덕션** | `https://yourdomain.com` |

### API 버전

현재 버전: **v1**

모든 엔드포인트는 `/api/v1/` 프리픽스를 사용합니다.

### 응답 형식

- **Content-Type**: `application/json`
- **인코딩**: UTF-8
- **타임존**: UTC
- **날짜 형식**: ISO 8601 (예: `2025-11-05T12:34:56Z`)

---

## 🔐 인증

### 인증 방식

**Bearer Token (JWT)**

```bash
Authorization: Bearer <access_token>
```

### 토큰 획득

```bash
# Google OAuth로 로그인
curl -X GET "http://localhost:8000/api/v1/auth/google"

# 콜백 후 access_token 획득
# access_token은 30분간 유효
```

### 인증이 필요한 엔드포인트

| 엔드포인트 | 인증 필요 |
|-----------|----------|
| `GET /health` | ❌ |
| `GET /tips/*` | ❌ |
| `POST /tips/*` | ✅ (Admin) |
| `POST /terminal/*` | ❌ |
| `POST /admin/*` | ✅ (Admin) |

---

## 📋 공통 응답 형식

### 성공 응답

```json
{
  "id": "tip_01HZ8X9G...",
  "title": "ls 명령어로 파일 목록 보기",
  "content": "...",
  "publishDate": "2025-11-05T00:00:00Z",
  "createdAt": "2025-11-05T12:34:56.123456Z",
  "updatedAt": "2025-11-05T12:34:56.123456Z"
}
```

### 에러 응답

```json
{
  "detail": {
    "code": "NOT_FOUND",
    "message": "Tip not found",
    "timestamp": "2025-11-05T12:34:56.123456Z"
  }
}
```

### 페이지네이션 응답

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "pageSize": 20,
  "totalPages": 5
}
```

---

## 🔌 엔드포인트

### 1. Health Check

#### GET /api/v1/health

시스템 상태 확인

**요청**:
```bash
curl -X GET "http://localhost:8000/api/v1/health"
```

**응답 (200 OK)**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "timestamp": "2025-11-05T12:34:56.123456Z",
  "database": "connected",
  "redis": "connected"
}
```

---

### 2. Tips API

#### 2.1. 오늘의 팁 조회

**GET /api/v1/tips/daily**

오늘 날짜의 팁을 반환합니다.

**요청**:
```bash
curl -X GET "http://localhost:8000/api/v1/tips/daily"
```

**응답 (200 OK)**:
```json
{
  "id": "tip_01HZ8X9G5KQZ...",
  "title": "ls 명령어로 파일 목록 보기",
  "content": "# ls 명령어 사용법\n\n`ls` 명령어는 현재 디렉토리의 파일과 폴더 목록을 보여줍니다...",
  "difficulty": "Beginner",
  "category": ["File Management", "Basic Commands"],
  "tags": ["ls", "directory", "files"],
  "viewCount": 42,
  "likeCount": 7,
  "publishDate": "2025-11-05T00:00:00Z",
  "createdAt": "2025-11-05T12:34:56.123456Z",
  "updatedAt": "2025-11-05T12:34:56.123456Z",
  "terminalSetup": {
    "files": {
      "documents/report.txt": "Sample report content",
      "projects/script.sh": "#!/bin/bash\necho 'Hello'"
    },
    "workingDirectory": "/home/user"
  }
}
```

**캐싱**: 24시간 (자정 이후 자동 갱신)

---

#### 2.2. 팁 목록 조회

**GET /api/v1/tips**

팁 목록을 페이지네이션과 함께 반환합니다.

**Query Parameters**:

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `page` | integer | ❌ | 1 | 페이지 번호 (1부터 시작) |
| `page_size` | integer | ❌ | 20 | 페이지당 항목 수 (최대 100) |
| `difficulty` | string | ❌ | - | 난이도 필터 (Beginner, Intermediate, Advanced) |
| `category` | string | ❌ | - | 카테고리 필터 |
| `search` | string | ❌ | - | 제목/내용 검색 (ILIKE 패턴, 대소문자 무시) |
| `sort_by` | string | ❌ | publish_date | 정렬 기준 (publish_date, title) |
| `order` | string | ❌ | desc | 정렬 방향 (asc, desc) |

**요청**:
```bash
# 기본 조회 (최신순 20개)
curl -X GET "http://localhost:8000/api/v1/tips?page=1&page_size=20"

# 초급 팁만 필터링
curl -X GET "http://localhost:8000/api/v1/tips?difficulty=Beginner"

# 카테고리 필터 + 검색
curl -X GET "http://localhost:8000/api/v1/tips?category=File%20Management&search=ls"

# 제목순 정렬 (오름차순)
curl -X GET "http://localhost:8000/api/v1/tips?sort_by=title&order=asc"
```

**응답 (200 OK)**:
```json
{
  "items": [
    {
      "id": "tip_01HZ8X9G...",
      "title": "ls 명령어로 파일 목록 보기",
      "difficulty": "Beginner",
      "category": ["File Management"],
      "viewCount": 42,
      "publishDate": "2025-11-05T00:00:00Z"
    },
    ...
  ],
  "total": 100,
  "page": 1,
  "pageSize": 20,
  "totalPages": 5
}
```

**캐싱**: 10분 (빠른 반영)

---

#### 2.3. 특정 팁 조회

**GET /api/v1/tips/{tip_id}**

특정 팁의 전체 내용을 반환합니다.

**Path Parameters**:
- `tip_id` (string, required): 팁 ID (예: `tip_01HZ8X9G...`)

**요청**:
```bash
curl -X GET "http://localhost:8000/api/v1/tips/tip_01HZ8X9G5KQZ..."
```

**응답 (200 OK)**:
```json
{
  "id": "tip_01HZ8X9G5KQZ...",
  "title": "ls 명령어로 파일 목록 보기",
  "content": "# ls 명령어 사용법\n\n...",
  "difficulty": "Beginner",
  "category": ["File Management"],
  "tags": ["ls", "directory"],
  "viewCount": 43,  // 자동 증가
  "likeCount": 7,
  "publishDate": "2025-11-05T00:00:00Z",
  "terminalSetup": { ... }
}
```

**응답 (404 Not Found)**:
```json
{
  "detail": {
    "code": "TIP_NOT_FOUND",
    "message": "Tip not found with id: tip_01HZ8X9G...",
    "timestamp": "2025-11-05T12:34:56.123456Z"
  }
}
```

**부작용**: `viewCount` 자동 증가 (비동기 처리)

**캐싱**: 1시간

---

#### 2.4. 팁 좋아요

**POST /api/v1/tips/{tip_id}/like**

특정 팁에 좋아요를 추가합니다.

**요청**:
```bash
curl -X POST "http://localhost:8000/api/v1/tips/tip_01HZ8X9G.../like"
```

**응답 (200 OK)**:
```json
{
  "id": "tip_01HZ8X9G...",
  "likeCount": 8,
  "message": "Like added successfully"
}
```

**부작용**: `likeCount` 증가, 캐시 무효화

---

#### 2.5. 카테고리 목록 조회

**GET /api/v1/tips/categories**

시스템에 존재하는 모든 카테고리 목록을 반환합니다.

**요청**:
```bash
curl -X GET "http://localhost:8000/api/v1/tips/categories"
```

**응답 (200 OK)**:
```json
{
  "categories": [
    "File Management",
    "System Monitoring",
    "Network Tools",
    "Text Processing",
    "Security",
    "Performance Tuning"
  ],
  "total": 6
}
```

**캐싱**: 30분

---

### 3. Authentication API

#### 3.1. Google OAuth 로그인

**GET /api/v1/auth/google**

Google OAuth 2.0 로그인 페이지로 리다이렉트합니다.

**요청**:
```bash
# 브라우저에서 접속
open "http://localhost:8000/api/v1/auth/google"
```

**응답**: 302 Redirect → Google 로그인 페이지

---

#### 3.2. Google OAuth 콜백

**GET /api/v1/auth/google/callback**

Google 로그인 후 콜백을 처리하고 JWT 토큰을 발급합니다.

**Query Parameters**:
- `code` (string, required): Google에서 발급한 인증 코드
- `state` (string, required): CSRF 방지 state 값

**요청**: (Google이 자동으로 호출)

**응답 (200 OK)**:
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "tokenType": "bearer",
  "expiresIn": 1800,
  "user": {
    "id": "user_01HZ8...",
    "email": "user@example.com",
    "name": "John Doe",
    "picture": "https://lh3.googleusercontent.com/...",
    "role": "user"
  }
}
```

**응답 (401 Unauthorized)**:
```json
{
  "detail": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid OAuth code or state",
    "timestamp": "2025-11-05T12:34:56.123456Z"
  }
}
```

---

#### 3.3. 현재 사용자 조회

**GET /api/v1/auth/me**

현재 로그인한 사용자 정보를 반환합니다.

**요청**:
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer <access_token>"
```

**응답 (200 OK)**:
```json
{
  "id": "user_01HZ8...",
  "email": "user@example.com",
  "name": "John Doe",
  "picture": "https://lh3.googleusercontent.com/...",
  "role": "user",
  "createdAt": "2025-10-01T10:00:00Z"
}
```

**응답 (401 Unauthorized)**:
```json
{
  "detail": "Not authenticated"
}
```

---

### 4. Terminal API

#### 4.1. 터미널 세션 생성

**POST /api/v1/terminal/sessions**

새로운 터미널 세션을 생성합니다.

**Request Body**:
```json
{
  "tipId": "tip_01HZ8X9G..."  // 선택: 팁 ID 지정 시 터미널 환경 자동 설정
}
```

**요청**:
```bash
# 빈 터미널 세션
curl -X POST "http://localhost:8000/api/v1/terminal/sessions" \
  -H "Content-Type: application/json"

# 팁 환경 설정된 세션
curl -X POST "http://localhost:8000/api/v1/terminal/sessions" \
  -H "Content-Type: application/json" \
  -d '{"tipId": "tip_01HZ8X9G..."}'
```

**응답 (200 OK)**:
```json
{
  "sessionId": "session_01HZ8...",
  "containerId": "alpine-sandbox-abc123",
  "status": "running",
  "createdAt": "2025-11-05T12:34:56.123456Z",
  "expiresAt": "2025-11-05T13:04:56.123456Z",  // 30분 후
  "workingDirectory": "/home/user",
  "websocketUrl": "ws://localhost:8000/api/v1/terminal/ws/session_01HZ8..."
}
```

**응답 (500 Internal Server Error)**:
```json
{
  "detail": {
    "code": "CONTAINER_CREATION_FAILED",
    "message": "Failed to create Docker container",
    "timestamp": "2025-11-05T12:34:56.123456Z"
  }
}
```

**세션 타임아웃**: 30분 (이후 자동 종료)

---

#### 4.2. 터미널 세션 조회

**GET /api/v1/terminal/sessions/{session_id}**

특정 터미널 세션 정보를 조회합니다.

**요청**:
```bash
curl -X GET "http://localhost:8000/api/v1/terminal/sessions/session_01HZ8..."
```

**응답 (200 OK)**:
```json
{
  "sessionId": "session_01HZ8...",
  "containerId": "alpine-sandbox-abc123",
  "status": "running",
  "createdAt": "2025-11-05T12:34:56.123456Z",
  "expiresAt": "2025-11-05T13:04:56.123456Z",
  "lastActivityAt": "2025-11-05T12:40:00.123456Z",
  "commandCount": 5
}
```

**응답 (404 Not Found)**:
```json
{
  "detail": {
    "code": "SESSION_NOT_FOUND",
    "message": "Session not found: session_01HZ8...",
    "timestamp": "2025-11-05T12:34:56.123456Z"
  }
}
```

---

#### 4.3. 터미널 명령어 실행

**POST /api/v1/terminal/sessions/{session_id}/execute**

터미널에서 명령어를 실행합니다.

**Request Body**:
```json
{
  "command": "ls -la"
}
```

**요청**:
```bash
curl -X POST "http://localhost:8000/api/v1/terminal/sessions/session_01HZ8.../execute" \
  -H "Content-Type: application/json" \
  -d '{"command": "ls -la"}'
```

**응답 (200 OK)**:
```json
{
  "output": "total 24\ndrwxr-xr-x    3 user  user  4096 Nov  5 12:34 .\ndrwxr-xr-x    1 root  root  4096 Nov  5 12:30 ..\n-rw-r--r--    1 user  user   220 Nov  5 12:30 .bash_logout\n...",
  "exitCode": 0,
  "executionTime": 0.055  // 초
}
```

**응답 (400 Bad Request)**:
```json
{
  "detail": {
    "code": "INVALID_COMMAND",
    "message": "Command cannot be empty",
    "timestamp": "2025-11-05T12:34:56.123456Z"
  }
}
```

**제약사항**:
- 라인 버퍼 모드 (vim, nano 미지원)
- 타임아웃: 30초
- 최대 출력 크기: 1MB

---

#### 4.4. WebSocket 연결

**WS /api/v1/terminal/ws/{session_id}**

실시간 터미널 WebSocket 연결

**연결**:
```javascript
// JavaScript 예시
const ws = new WebSocket('ws://localhost:8000/api/v1/terminal/ws/session_01HZ8...');

ws.onopen = () => {
  console.log('Connected');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Output:', data.output);
};

// 명령어 실행
ws.send(JSON.stringify({
  type: 'execute',
  command: 'ls -la'
}));
```

**메시지 형식**:

**클라이언트 → 서버**:
```json
{
  "type": "execute",
  "command": "ls -la"
}
```

**서버 → 클라이언트**:
```json
{
  "type": "output",
  "output": "...",
  "exitCode": 0
}
```

**연결 종료**:
```json
{
  "type": "close",
  "reason": "Session terminated"
}
```

---

#### 4.5. 터미널 세션 종료

**DELETE /api/v1/terminal/sessions/{session_id}**

터미널 세션을 종료하고 컨테이너를 삭제합니다.

**요청**:
```bash
curl -X DELETE "http://localhost:8000/api/v1/terminal/sessions/session_01HZ8..."
```

**응답 (200 OK)**:
```json
{
  "message": "Session terminated successfully",
  "sessionId": "session_01HZ8...",
  "deletedAt": "2025-11-05T12:50:00.123456Z"
}
```

**멱등성**: 이미 종료된 세션도 200 OK 반환

---

### 5. Admin API

#### 5.1. 팁 생성 (관리자 전용)

**POST /api/v1/admin/tips**

새로운 팁을 생성합니다.

**인증 필요**: ✅ (Admin 권한)

**Request Body**:
```json
{
  "title": "grep으로 파일 내용 검색하기",
  "content": "# grep 명령어 사용법\n\n...",
  "difficulty": "Intermediate",
  "category": ["Text Processing", "Search Tools"],
  "tags": ["grep", "search", "regex"],
  "publishDate": "2025-11-06T00:00:00Z",
  "terminalSetup": {
    "files": {
      "sample.txt": "Sample content for testing"
    },
    "workingDirectory": "/home/user"
  }
}
```

**요청**:
```bash
curl -X POST "http://localhost:8000/api/v1/admin/tips" \
  -H "Authorization: Bearer <admin_access_token>" \
  -H "Content-Type: application/json" \
  -d @tip_payload.json
```

**응답 (201 Created)**:
```json
{
  "id": "tip_01HZ9...",
  "title": "grep으로 파일 내용 검색하기",
  "status": "published",
  "createdAt": "2025-11-05T12:34:56.123456Z"
}
```

**응답 (403 Forbidden)**:
```json
{
  "detail": {
    "code": "INSUFFICIENT_PERMISSIONS",
    "message": "Admin role required",
    "timestamp": "2025-11-05T12:34:56.123456Z"
  }
}
```

---

#### 5.2. 시스템 통계 조회

**GET /api/v1/admin/stats**

시스템 전체 통계를 조회합니다.

**인증 필요**: ✅ (Admin 권한)

**요청**:
```bash
curl -X GET "http://localhost:8000/api/v1/admin/stats" \
  -H "Authorization: Bearer <admin_access_token>"
```

**응답 (200 OK)**:
```json
{
  "tips": {
    "total": 100,
    "published": 95,
    "draft": 5,
    "totalViews": 15420,
    "totalLikes": 1234
  },
  "users": {
    "total": 523,
    "active": 342,
    "admins": 3
  },
  "terminal": {
    "activeSessions": 12,
    "totalExecutedCommands": 3456,
    "averageSessionDuration": 450  // 초
  },
  "system": {
    "uptime": 86400,  // 초
    "version": "1.0.0",
    "environment": "production"
  }
}
```

---

## ⚠️ 에러 코드

### HTTP 상태 코드

| 상태 코드 | 설명 |
|----------|------|
| `200 OK` | 요청 성공 |
| `201 Created` | 리소스 생성 성공 |
| `400 Bad Request` | 잘못된 요청 (필수 필드 누락, 형식 오류) |
| `401 Unauthorized` | 인증 실패 (토큰 없음/만료) |
| `403 Forbidden` | 권한 없음 (Admin 권한 필요) |
| `404 Not Found` | 리소스 없음 |
| `422 Unprocessable Entity` | 유효성 검증 실패 |
| `429 Too Many Requests` | Rate Limit 초과 |
| `500 Internal Server Error` | 서버 내부 오류 |
| `503 Service Unavailable` | 서비스 일시 중단 (유지보수) |

### 에러 코드 목록

| 코드 | HTTP | 설명 |
|------|------|------|
| `TIP_NOT_FOUND` | 404 | 팁을 찾을 수 없음 |
| `SESSION_NOT_FOUND` | 404 | 터미널 세션을 찾을 수 없음 |
| `SESSION_EXPIRED` | 410 | 세션 만료 (30분 초과) |
| `INVALID_CREDENTIALS` | 401 | 잘못된 인증 정보 |
| `INSUFFICIENT_PERMISSIONS` | 403 | 권한 부족 (Admin 필요) |
| `INVALID_COMMAND` | 400 | 잘못된 명령어 |
| `CONTAINER_CREATION_FAILED` | 500 | Docker 컨테이너 생성 실패 |
| `VALIDATION_ERROR` | 422 | 입력 유효성 검증 실패 |
| `RATE_LIMIT_EXCEEDED` | 429 | Rate Limit 초과 |
| `DATABASE_ERROR` | 500 | 데이터베이스 오류 |
| `CACHE_ERROR` | 500 | Redis 캐시 오류 (Fail-Open) |

---

## 🚦 Rate Limiting

### 제한 정책

| 엔드포인트 그룹 | 제한 | 기간 |
|---------------|------|------|
| **GET /tips/*** | 100회 | 1분 |
| **POST /terminal/*** | 20회 | 1분 |
| **POST /admin/*** | 10회 | 1분 |
| **모든 요청** | 1000회 | 1시간 |

### Rate Limit 헤더

응답에 포함되는 헤더:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1699200000
```

### Rate Limit 초과 시

**응답 (429 Too Many Requests)**:
```json
{
  "detail": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded: 100 requests per 1 minute",
    "retryAfter": 45,  // 초
    "timestamp": "2025-11-05T12:34:56.123456Z"
  }
}
```

**헤더**:
```
Retry-After: 45
```

---

## 📊 API 사용 예시

### 시나리오 1: 오늘의 팁 + 터미널 실습

```bash
# 1. 오늘의 팁 조회
TIP=$(curl -s "http://localhost:8000/api/v1/tips/daily")
TIP_ID=$(echo $TIP | jq -r '.id')

# 2. 터미널 세션 생성 (팁 환경 자동 설정)
SESSION=$(curl -s -X POST "http://localhost:8000/api/v1/terminal/sessions" \
  -H "Content-Type: application/json" \
  -d "{\"tipId\": \"$TIP_ID\"}")
SESSION_ID=$(echo $SESSION | jq -r '.sessionId')

# 3. 명령어 실행
curl -s -X POST "http://localhost:8000/api/v1/terminal/sessions/$SESSION_ID/execute" \
  -H "Content-Type: application/json" \
  -d '{"command": "ls -la"}'

# 4. 세션 종료
curl -s -X DELETE "http://localhost:8000/api/v1/terminal/sessions/$SESSION_ID"
```

---

### 시나리오 2: 팁 검색 및 필터링

```bash
# 1. 초급 팁 검색 (ls 관련)
curl -s "http://localhost:8000/api/v1/tips?difficulty=Beginner&search=ls&page_size=5"

# 2. 카테고리별 최신 팁 10개
curl -s "http://localhost:8000/api/v1/tips?category=File%20Management&page_size=10&sort_by=publish_date&order=desc"

# 3. 특정 팁 상세 조회
curl -s "http://localhost:8000/api/v1/tips/tip_01HZ8X9G..."

# 4. 좋아요 추가
curl -s -X POST "http://localhost:8000/api/v1/tips/tip_01HZ8X9G.../like"
```

---

## 🔗 추가 리소스

- **Swagger UI**: http://localhost:8000/docs (인터랙티브 API 문서)
- **ReDoc**: http://localhost:8000/redoc (읽기 전용 API 문서)
- **OpenAPI JSON**: http://localhost:8000/openapi.json (스키마 다운로드)

---

## 📞 지원

- **버그 리포트**: GitHub Issues
- **기술 지원**: dev@yourdomain.com
- **보안 이슈**: security@yourdomain.com

---

**문서 버전**: Day 28 (2025-11-05)
**API 버전**: v1.0.0
**마지막 업데이트**: Week 4 완료

**⚠️ 주의사항**:
- 프로덕션 환경에서는 HTTPS를 반드시 사용하세요
- Rate Limit을 초과하지 않도록 주의하세요
- 민감한 정보를 로그에 남기지 마세요
- 토큰은 안전하게 보관하고 주기적으로 갱신하세요
