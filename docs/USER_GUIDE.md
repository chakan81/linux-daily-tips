# Linux Daily Tips - 사용자 가이드

이 문서는 Linux Daily Tips 프로젝트를 빠르게 시작하고 개발 환경을 구성하는 방법을 안내합니다.

---

## 📚 목차

1. [빠른 시작 (5분)](#-빠른-시작-5분)
2. [개발 환경 설정](#-개발-환경-설정)
3. [환경 변수 설명](#-환경-변수-설명)
4. [테스트 실행](#-테스트-실행)
5. [트러블슈팅](#-트러블슈팅)
6. [IDE 설정](#-ide-설정)

---

## 🚀 빠른 시작 (5분)

### 필수 조건

- **Docker & Docker Compose**: 20.10+ 버전 권장
- **Git**: 최신 버전
- **터미널 접근**: bash, zsh 등

### 5분 안에 실행하기

```bash
# 1. 저장소 클론
git clone <repository-url>
cd linux-daily-tips

# 2. 환경 변수 설정
cp .env.example .env

# 3. 전체 스택 시작 (Docker Compose)
docker compose up -d

# 4. 서비스 상태 확인
docker compose ps
```

### 서비스 접속

| 서비스 | URL | 설명 |
|--------|-----|------|
| **프론트엔드** | http://localhost:3000 | Next.js 앱 |
| **백엔드 API** | http://localhost:8000 | FastAPI |
| **API 문서** | http://localhost:8000/docs | Swagger UI |
| **pgAdmin** | http://localhost:5050 | PostgreSQL 관리 |
| **Redis Commander** | http://localhost:8081 | Redis 모니터링 |

### 빠른 종료

```bash
# 전체 서비스 종료
docker compose down

# 데이터 완전 삭제 후 종료 (주의!)
docker compose down -v
```

---

## 🛠 개발 환경 설정

### 방법 1: Docker 전체 스택 (권장)

**장점**: 환경 일관성, 빠른 시작, 프로덕션과 동일한 환경

```bash
# 전체 스택 시작
docker compose up -d

# 로그 실시간 확인
docker compose logs -f

# 특정 서비스만 재시작
docker compose restart frontend
docker compose restart backend
```

**개발 워크플로우**:
1. 코드 수정 (로컬 에디터)
2. Hot Reload 자동 적용 (볼륨 마운트)
3. 브라우저 새로고침 (프론트엔드)
4. API 테스트 (http://localhost:8000/docs)

---

### 방법 2: 하이브리드 개발 (로컬 + Docker)

**장점**: IDE 디버깅, 빠른 패키지 설치

#### 백엔드 (로컬 Python)

```bash
# 1. PostgreSQL + Redis만 Docker로 실행
docker compose up -d postgres redis

# 2. 백엔드 로컬 실행
cd backend

# Python 가상환경 생성 (uv 사용)
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 의존성 설치
uv pip install -e .

# 환경 변수 설정
export DATABASE_URL="postgresql://postgres:postgres_dev_password@localhost:5432/linux_daily_tips"
export REDIS_URL="redis://:redis_dev_password@localhost:6379/0"
export SECRET_KEY="your-secret-key-here"
export ENVIRONMENT="development"

# 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 프론트엔드 (로컬 Node.js)

```bash
# 1. 백엔드 서비스 실행 (위 참조)

# 2. 프론트엔드 로컬 실행
cd frontend

# 의존성 설치
npm install

# 환경 변수 설정 (.env.local)
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# 개발 서버 실행
npm run dev

# 브라우저 접속: http://localhost:3000
```

---

## 🔑 환경 변수 설명

### 필수 환경 변수

`.env` 파일에 다음 변수들이 반드시 설정되어야 합니다:

```bash
# === PostgreSQL 설정 ===
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres_dev_password
POSTGRES_DB=linux_daily_tips

# === Redis 설정 ===
REDIS_PASSWORD=redis_dev_password

# === 백엔드 설정 ===
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
SECRET_KEY=your-secret-key-change-this-in-production
ENVIRONMENT=development

# === JWT 설정 ===
JWT_SECRET_KEY=your-jwt-secret-key-change-this
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# === 프론트엔드 설정 ===
NEXT_PUBLIC_API_URL=http://localhost:8000  # 빈 문자열 = rewrites 사용
NEXT_PUBLIC_APP_ENV=development
```

### 선택 환경 변수

```bash
# === 백엔드 선택 사항 ===
LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR, CRITICAL
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
MAX_CONNECTION_COUNT=10           # 데이터베이스 커넥션 풀 크기
MIN_CONNECTION_COUNT=5

# === Redis 캐싱 선택 사항 ===
REDIS_CACHE_TTL=300               # 캐시 유효 시간 (초)
REDIS_MAX_CONNECTIONS=10

# === OAuth 설정 (선택) ===
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback

# === 모니터링 (선택) ===
SENTRY_DSN=                       # Sentry 에러 추적
```

---

## 🧪 테스트 실행

### 백엔드 테스트

```bash
# Docker 컨테이너에서 실행
docker compose exec backend pytest

# 커버리지 포함
docker compose exec backend pytest --cov=app --cov-report=html

# 특정 테스트 파일만
docker compose exec backend pytest tests/test_tips_service.py

# 로컬 환경에서 실행 (가상환경 활성화 필요)
cd backend
pytest
pytest --cov=app --cov-report=term-missing
```

### 프론트엔드 테스트

```bash
# Docker 컨테이너에서 실행
docker compose exec frontend npm run test

# E2E 테스트 (Playwright)
docker compose exec frontend npm run test:e2e

# E2E UI 모드 (디버깅)
docker compose exec frontend npm run test:e2e:ui

# 로컬 환경에서 실행
cd frontend
npm run test
npm run test:e2e
npm run test:e2e:ui
```

### 전체 통합 테스트

```bash
# CI 환경 시뮬레이션
docker compose -f docker-compose.ci.yml up --abort-on-container-exit

# 개별 CI 테스트
docker compose -f docker-compose.ci.yml run --rm backend-test
docker compose -f docker-compose.ci.yml run --rm frontend-test
```

---

## 🚨 트러블슈팅

### 1. Docker 서비스가 시작되지 않음

**증상**: `docker compose up` 실패, 컨테이너가 즉시 종료됨

**해결 방법**:

```bash
# Docker Desktop 실행 확인
docker info

# Docker Compose 버전 확인 (2.0+ 필요)
docker compose --version

# 이전 컨테이너 완전 제거
docker compose down -v
docker system prune -a --volumes  # 주의: 모든 Docker 데이터 삭제

# 다시 시작
docker compose up -d
```

---

### 2. 포트 충돌 (Port Already in Use)

**증상**: `Error: Bind for 0.0.0.0:5432 failed: port is already allocated`

**해결 방법**:

```bash
# 포트 사용 중인 프로세스 확인
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis
lsof -i :3000  # Frontend
lsof -i :8000  # Backend

# 프로세스 종료 (PID 확인 후)
kill -9 <PID>

# 또는 Docker Compose 포트 변경 (docker-compose.override.yml)
services:
  postgres:
    ports:
      - "5433:5432"  # 5432 → 5433으로 변경
```

---

### 3. 데이터베이스 연결 실패

**증상**: `FATAL: password authentication failed for user "postgres"`

**해결 방법**:

```bash
# 1. 서비스 상태 확인
docker compose ps

# 2. PostgreSQL 헬스 체크
docker compose exec postgres pg_isready -U postgres

# 3. 로그 확인
docker compose logs postgres

# 4. 환경 변수 확인
docker compose exec postgres env | grep POSTGRES

# 5. 데이터베이스 완전 재생성
docker compose down -v
docker compose up -d postgres
docker compose exec postgres psql -U postgres -c "CREATE DATABASE linux_daily_tips;"
```

---

### 4. 프론트엔드 Hot Reload가 작동하지 않음

**증상**: 코드 수정 후 브라우저에 반영되지 않음

**해결 방법**:

```bash
# 1. 컨테이너 재시작
docker compose restart frontend

# 2. node_modules 재설치
docker compose exec frontend rm -rf node_modules .next
docker compose exec frontend npm install

# 3. 볼륨 마운트 확인 (docker-compose.dev.yml)
services:
  frontend:
    volumes:
      - ./frontend:/app
      - /app/node_modules  # node_modules 제외 필수

# 4. 로컬 개발로 전환 (더 빠름)
cd frontend
npm run dev
```

---

### 5. CORS 에러 (Cross-Origin Request Blocked)

**증상**: 브라우저 콘솔에 CORS 에러 표시

**해결 방법**:

```bash
# 1. 백엔드 환경 변수 확인
docker compose exec backend env | grep CORS_ORIGINS

# 2. .env 파일 수정
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# 3. 백엔드 재시작
docker compose restart backend

# 4. Next.js rewrites 사용 (권장)
# frontend/next.config.js의 rewrites 설정 확인
# NEXT_PUBLIC_API_URL을 빈 문자열로 설정
NEXT_PUBLIC_API_URL=
```

---

### 6. Redis 연결 실패

**증상**: `Error: Redis connection failed`

**해결 방법**:

```bash
# 1. Redis 서비스 확인
docker compose ps redis

# 2. Redis CLI 접속 테스트
docker compose exec redis redis-cli -a redis_dev_password ping
# 응답: PONG

# 3. Redis 로그 확인
docker compose logs redis

# 4. Redis 재시작
docker compose restart redis
```

---

### 7. 터미널 WebSocket 연결 실패

**증상**: 터미널 페이지에서 "Connection failed" 에러

**해결 방법**:

```bash
# 1. 백엔드 WebSocket 엔드포인트 확인
curl http://localhost:8000/api/terminal/sessions

# 2. Docker 네트워크 확인
docker network ls
docker network inspect linux-daily-tips_default

# 3. 백엔드 로그 확인
docker compose logs backend | grep -i websocket

# 4. Docker 샌드박스 컨테이너 정리
docker ps -a | grep alpine-sandbox
docker rm -f $(docker ps -a -q --filter "name=sandbox")

# 5. 백엔드 재시작
docker compose restart backend
```

---

### 8. 테스트 실패 (Pytest/Playwright)

**증상**: 일부 테스트가 실패하거나 타임아웃

**해결 방법**:

```bash
# Backend 테스트 실패
# 1. 테스트 데이터베이스 재설정
docker compose exec backend pytest --create-db

# 2. 캐시 삭제
docker compose exec backend rm -rf .pytest_cache __pycache__

# 3. 특정 테스트만 실행 (디버깅)
docker compose exec backend pytest tests/test_tips_service.py -v -s

# Frontend E2E 테스트 실패
# 1. Playwright 브라우저 재설치
docker compose exec frontend npx playwright install --with-deps

# 2. 테스트 UI 모드로 디버깅
docker compose exec frontend npm run test:e2e:ui

# 3. 스크린샷/비디오 확인
ls -la frontend/test-results/
```

---

## 💻 IDE 설정

### VS Code 권장 확장

프로젝트 루트의 `.vscode/extensions.json`에 권장 확장이 정의되어 있습니다:

**백엔드 개발**:
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Black Formatter (ms-python.black-formatter)
- isort (ms-python.isort)

**프론트엔드 개발**:
- ESLint (dbaeumer.vscode-eslint)
- Prettier (esbenp.prettier-vscode)
- Tailwind CSS IntelliSense (bradlc.vscode-tailwindcss)
- TypeScript Error Translator (mattpocock.ts-error-translator)

**DevOps**:
- Docker (ms-azuretools.vscode-docker)
- YAML (redhat.vscode-yaml)

### VS Code 설정 (.vscode/settings.json)

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/backend/.venv/bin/python",
  "python.testing.pytestEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

### PyCharm/IntelliJ 설정

**Python 인터프리터**:
1. `File` → `Settings` → `Project: linux-daily-tips` → `Python Interpreter`
2. `Add Interpreter` → `Existing environment`
3. 경로: `backend/.venv/bin/python`

**Docker Compose 통합**:
1. `File` → `Settings` → `Build, Execution, Deployment` → `Docker`
2. `+` 버튼 클릭 → `Docker for Mac` (또는 사용 중인 Docker 엔진)
3. `docker-compose.yml` 우클릭 → `Run 'docker compose up'`

---

## 📊 유용한 명령어 모음

### Docker 관리

```bash
# 서비스 상태 확인
docker compose ps

# 실시간 로그 확인
docker compose logs -f

# 특정 서비스 로그
docker compose logs backend
docker compose logs frontend

# 컨테이너 내부 접속
docker compose exec backend bash
docker compose exec frontend sh

# 리소스 사용량 확인
docker stats

# 디스크 사용량 확인
docker system df

# 미사용 리소스 정리
docker system prune -a --volumes
```

### 데이터베이스 관리

```bash
# PostgreSQL 접속
docker compose exec postgres psql -U postgres -d linux_daily_tips

# SQL 파일 실행
docker compose exec postgres psql -U postgres -d linux_daily_tips -f /path/to/file.sql

# 데이터베이스 백업
docker compose exec postgres pg_dump -U postgres linux_daily_tips > backup.sql

# 데이터베이스 복원
docker compose exec -T postgres psql -U postgres -d linux_daily_tips < backup.sql

# 테이블 목록 확인
docker compose exec postgres psql -U postgres -d linux_daily_tips -c "\dt"
```

### Redis 관리

```bash
# Redis CLI 접속
docker compose exec redis redis-cli -a redis_dev_password

# 모든 키 확인
docker compose exec redis redis-cli -a redis_dev_password KEYS '*'

# 캐시 플러시 (개발용)
docker compose exec redis redis-cli -a redis_dev_password FLUSHALL

# Redis 메모리 사용량
docker compose exec redis redis-cli -a redis_dev_password INFO memory
```

---

## 📞 추가 도움

- **버그 리포트**: GitHub Issues
- **기능 요청**: GitHub Discussions
- **문서**: `docs/` 디렉토리
  - [요구사항 정의서](./requirements.md)
  - [기술 설계서](./service-planning.md)
  - [배포 가이드](./DEPLOYMENT.md)
  - [API 문서](../backend/docs/API_REFERENCE.md)

---

**문서 버전**: Day 28 (2025-11-05)
**마지막 업데이트**: Week 4 완료
