# Environment Variables Configuration Guide

Linux Daily Tips 백엔드의 환경 변수 설정 가이드입니다.

## 📋 목차

- [개요](#개요)
- [필수 환경 변수](#필수-환경-변수)
- [선택적 환경 변수](#선택적-환경-변수)
- [환경별 설정](#환경별-설정)
- [보안 권장사항](#보안-권장사항)

---

## 개요

모든 환경 변수는 `.env` 파일 또는 시스템 환경 변수로 설정할 수 있습니다.

**우선순위**: 시스템 환경 변수 > `.env` 파일 > 기본값

### .env 파일 생성

```bash
cd backend
cp .env.example .env  # 예제 파일 복사
nano .env             # 환경 변수 편집
```

---

## 필수 환경 변수

### 🔐 보안 설정

#### SECRET_KEY
JWT 토큰 서명용 시크릿 키 (최소 32자 이상)

```bash
# 개발 환경: 자동 생성됨 (경고 로그 출력)
# 프로덕션: 반드시 설정 필요

# 생성 방법
python -c "import secrets; print(secrets.token_urlsafe(32))"

# .env 설정
SECRET_KEY=your_generated_secret_key_here_min_32_chars
```

**프로덕션 요구사항**:
- ✅ 최소 32자 이상
- ✅ 환경 변수 필수 설정
- ❌ 미설정 시 서버 시작 실패

#### REDIS_ENCRYPTION_KEY
Redis 세션 데이터 암호화 키 (Fernet 키, 44자 Base64)

```bash
# 개발 환경: 자동 생성됨 (경고 로그 출력)
# 프로덕션: 반드시 설정 필요

# 생성 방법
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# .env 설정
REDIS_ENCRYPTION_KEY=your_fernet_key_here_44_chars_base64
```

**프로덕션 요구사항**:
- ✅ Fernet 키 형식 (44자 Base64)
- ✅ 환경 변수 필수 설정
- ❌ 잘못된 형식 시 서버 시작 실패

### 🗄️ 데이터베이스 설정

#### DATABASE_URL
PostgreSQL 비동기 연결 URL

```bash
# 개발 환경
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/linux_daily_tips

# 프로덕션
DATABASE_URL=postgresql+asyncpg://user:password@db-host:5432/dbname
```

#### REDIS_URL
Redis 연결 URL

```bash
# 개발 환경
REDIS_URL=redis://localhost:6379/0

# 프로덕션
REDIS_URL=redis://redis-host:6379/0
```

### 🔑 Google OAuth 2.0 설정

#### GOOGLE_CLIENT_ID
Google OAuth 2.0 Client ID

```bash
GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
```

#### GOOGLE_CLIENT_SECRET
Google OAuth 2.0 Client Secret

```bash
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

#### GOOGLE_REDIRECT_URI
Google OAuth 2.0 Redirect URI

```bash
# 개발 환경
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/callback

# 프로덕션
GOOGLE_REDIRECT_URI=https://yourdomain.com/api/v1/auth/callback
```

**설정 방법**:
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 프로젝트 생성 → API 및 서비스 → 사용자 인증 정보
3. OAuth 2.0 클라이언트 ID 생성 (웹 애플리케이션)
4. 승인된 리디렉션 URI 추가

---

## 선택적 환경 변수

### 🌐 애플리케이션 설정

#### PROJECT_NAME
프로젝트 이름 (기본값: "Linux Daily Tips API")

```bash
PROJECT_NAME=Linux Daily Tips API
```

#### VERSION
API 버전 (기본값: "0.1.0")

```bash
VERSION=0.1.0
```

#### API_V1_STR
API v1 URL 접두사 (기본값: "/api/v1")

```bash
API_V1_STR=/api/v1
```

#### ENVIRONMENT
실행 환경 (기본값: "development")

```bash
# 가능한 값: development, staging, production
ENVIRONMENT=development
```

#### DEBUG
디버그 모드 활성화 여부 (기본값: True)

```bash
# 프로덕션에서는 False 설정 권장
DEBUG=False
```

#### LOG_LEVEL
로그 레벨 (기본값: "INFO")

```bash
# 가능한 값: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO
```

### ⏱️ HTTP 클라이언트 설정

#### HTTP_TIMEOUT
HTTP 요청 타임아웃 (초, 기본값: 10)

```bash
# Google OAuth API 호출 타임아웃
HTTP_TIMEOUT=10
```

#### HTTP_CONNECT_TIMEOUT
HTTP 연결 타임아웃 (초, 기본값: 5)

```bash
# Google OAuth API 연결 타임아웃
HTTP_CONNECT_TIMEOUT=5
```

**적용 대상**:
- `app/services/auth/oauth_client.py` - Google OAuth HTTP 통신
- 모든 외부 API 호출

### 🕒 세션 설정

#### SESSION_TTL
세션 만료 시간 (초, 기본값: 3600 = 1시간)

```bash
# 1시간 (3600초)
SESSION_TTL=3600

# 24시간
SESSION_TTL=86400
```

#### SESSION_EXPIRY_MINUTES
터미널 세션 자동 만료 시간 (분, 기본값: 30)

```bash
# 30분 (기본값)
SESSION_EXPIRY_MINUTES=30

# 1시간
SESSION_EXPIRY_MINUTES=60

# 개발 환경: 짧은 타임아웃
SESSION_EXPIRY_MINUTES=10
```

**적용 위치**: `app/services/terminal/session_manager.py:25`

**설명**:
- 터미널 세션이 비활성화된 후 자동으로 만료되는 시간
- Docker 컨테이너 리소스 관리를 위해 설정
- 만료된 세션은 백그라운드 크론잡이 자동으로 정리

#### OAUTH_STATE_TTL
OAuth State 만료 시간 (초, 기본값: 600 = 10분)

```bash
# 10분 (CSRF 방어용)
OAUTH_STATE_TTL=600
```

### 🔒 JWT 토큰 설정

#### ALGORITHM
JWT 토큰 암호화 알고리즘 (기본값: "HS256")

```bash
ALGORITHM=HS256
```

#### ACCESS_TOKEN_EXPIRE_MINUTES
액세스 토큰 만료 시간 (분, 기본값: 30)

```bash
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### REFRESH_TOKEN_EXPIRE_DAYS
리프레시 토큰 만료 시간 (일, 기본값: 7)

```bash
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 🌍 CORS 설정

#### CORS_ORIGINS
CORS 허용 origin 목록 (개발 환경)

```bash
# JSON 배열 형식
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]

# 쉼표 구분 형식 (자동 파싱)
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

#### CORS_ORIGINS_PRODUCTION
프로덕션 CORS 허용 origin 목록

```bash
# 프로덕션에서는 반드시 설정 필요
CORS_ORIGINS_PRODUCTION=["https://yourdomain.com","https://www.yourdomain.com"]
```

**프로덕션 요구사항**:
- ✅ 환경 변수 필수 설정
- ❌ 미설정 시 서버 시작 실패

### 🍪 Cookie 보안 설정

#### COOKIE_SECURE
Cookie Secure 플래그 (HTTPS only, 기본값: False)

```bash
# 프로덕션: HTTPS 사용 시 True 설정
COOKIE_SECURE=True
```

#### COOKIE_HTTPONLY
Cookie HttpOnly 플래그 (XSS 방어, 기본값: True)

```bash
# 항상 True 권장 (XSS 공격 방어)
COOKIE_HTTPONLY=True
```

#### COOKIE_SAMESITE
Cookie SameSite 정책 (CSRF 방어, 기본값: "lax")

```bash
# 가능한 값: lax, strict, none
COOKIE_SAMESITE=lax
```

### 🌐 프론트엔드 URL 설정

#### FRONTEND_URL
프론트엔드 애플리케이션 URL (OAuth 리다이렉트용)

```bash
# 개발 환경
FRONTEND_URL=http://localhost:3000

# 프로덕션
FRONTEND_URL=https://yourdomain.com
```

#### ALLOWED_FRONTEND_URLS
허용된 프론트엔드 URL 화이트리스트 (Open Redirect 방지)

```bash
# JSON 배열 형식
ALLOWED_FRONTEND_URLS=["http://localhost:3000","http://localhost:3001"]
```

### 🗄️ 데이터베이스 연결 풀 설정

#### MAX_CONNECTIONS_COUNT
데이터베이스 최대 연결 수 (기본값: 10)

```bash
MAX_CONNECTIONS_COUNT=10
```

#### MIN_CONNECTIONS_COUNT
데이터베이스 최소 연결 수 (기본값: 10)

```bash
MIN_CONNECTIONS_COUNT=10
```

---

## 환경별 설정

### 개발 환경 (.env.development)

```bash
# 기본 설정
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=DEBUG

# 데이터베이스 (로컬)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/linux_daily_tips
REDIS_URL=redis://localhost:6379/0

# 보안 (자동 생성됨, 경고 로그 출력)
# SECRET_KEY=  # 미설정 시 자동 생성
# REDIS_ENCRYPTION_KEY=  # 미설정 시 자동 생성

# CORS (로컬 개발)
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
FRONTEND_URL=http://localhost:3000

# Cookie (HTTP 허용)
COOKIE_SECURE=False
COOKIE_HTTPONLY=True
COOKIE_SAMESITE=lax

# 타임아웃 (개발용 짧게 설정)
HTTP_TIMEOUT=10
HTTP_CONNECT_TIMEOUT=5
SESSION_TTL=3600
OAUTH_STATE_TTL=600
```

### 프로덕션 환경 (.env.production)

```bash
# 기본 설정
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO

# 데이터베이스 (프로덕션)
DATABASE_URL=postgresql+asyncpg://user:password@db-host:5432/dbname
REDIS_URL=redis://redis-host:6379/0

# 보안 (필수 설정!)
SECRET_KEY=your_production_secret_key_min_32_chars
REDIS_ENCRYPTION_KEY=your_production_fernet_key_44_chars

# Google OAuth (프로덕션)
GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=https://yourdomain.com/api/v1/auth/callback

# CORS (프로덕션 도메인)
CORS_ORIGINS_PRODUCTION=["https://yourdomain.com","https://www.yourdomain.com"]
FRONTEND_URL=https://yourdomain.com
ALLOWED_FRONTEND_URLS=["https://yourdomain.com","https://www.yourdomain.com"]

# Cookie (HTTPS only)
COOKIE_SECURE=True
COOKIE_HTTPONLY=True
COOKIE_SAMESITE=lax

# 타임아웃 (프로덕션용 길게 설정)
HTTP_TIMEOUT=30
HTTP_CONNECT_TIMEOUT=10
SESSION_TTL=7200  # 2시간
OAUTH_STATE_TTL=600

# 데이터베이스 연결 풀 (프로덕션 트래픽에 맞게 조정)
MAX_CONNECTIONS_COUNT=50
MIN_CONNECTIONS_COUNT=10
```

---

## 보안 권장사항

### ✅ 필수 사항

1. **SECRET_KEY와 REDIS_ENCRYPTION_KEY 보호**
   - ❌ Git에 커밋하지 마세요
   - ✅ `.gitignore`에 `.env` 추가
   - ✅ 환경별로 다른 키 사용
   - ✅ 주기적으로 키 로테이션

2. **프로덕션 환경 변수 검증**
   - ✅ `ENVIRONMENT=production` 시 모든 필수 변수 설정
   - ✅ 서버 시작 전 자동 검증 (config.py validator)
   - ✅ 미설정 시 서버 시작 실패

3. **CORS 설정**
   - ❌ `CORS_ORIGINS=["*"]` 절대 사용 금지
   - ✅ 프로덕션에서는 `CORS_ORIGINS_PRODUCTION` 명시
   - ✅ 허용된 도메인만 화이트리스트

4. **Cookie 보안**
   - ✅ 프로덕션: `COOKIE_SECURE=True` (HTTPS only)
   - ✅ 항상 `COOKIE_HTTPONLY=True` (XSS 방어)
   - ✅ `COOKIE_SAMESITE=lax` 또는 `strict` (CSRF 방어)

### 🔐 키 생성 스크립트

```python
# scripts/generate_keys.py
import secrets
from cryptography.fernet import Fernet

print("=== Environment Variables Generation ===\n")

# SECRET_KEY 생성
secret_key = secrets.token_urlsafe(32)
print(f"SECRET_KEY={secret_key}")

# REDIS_ENCRYPTION_KEY 생성
redis_key = Fernet.generate_key().decode()
print(f"REDIS_ENCRYPTION_KEY={redis_key}")

print("\n⚠️ 이 키들을 .env 파일에 복사하세요!")
print("⚠️ Git에 커밋하지 마세요!")
```

실행:
```bash
cd backend
python scripts/generate_keys.py
```

### 📋 환경 변수 체크리스트

#### 개발 환경
- [ ] `.env` 파일 생성
- [ ] `DATABASE_URL` 로컬 DB 설정
- [ ] `REDIS_URL` 로컬 Redis 설정
- [ ] Google OAuth (선택적)

#### 프로덕션 환경
- [ ] `ENVIRONMENT=production` 설정
- [ ] `SECRET_KEY` 생성 및 설정 (최소 32자)
- [ ] `REDIS_ENCRYPTION_KEY` 생성 및 설정 (Fernet 키)
- [ ] `DATABASE_URL` 프로덕션 DB 설정
- [ ] `REDIS_URL` 프로덕션 Redis 설정
- [ ] `CORS_ORIGINS_PRODUCTION` 설정
- [ ] `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI` 설정
- [ ] `COOKIE_SECURE=True` 설정
- [ ] `DEBUG=False` 설정
- [ ] `.env` 파일 `.gitignore`에 추가

---

## 📚 관련 문서

- `backend/app/core/config.py` - 설정 정의 및 validator
- `backend/docs/models-usage-guide.md` - Error Handling 가이드
- `backend/CLAUDE.md` - 백엔드 개발 가이드

---

**Last Updated**: 2025-11-03
**Version**: 1.0.0
