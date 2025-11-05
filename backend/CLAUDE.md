# Backend Development Guide

Linux Daily Tips 백엔드 개발을 위한 Claude Code 가이드입니다.

## 🚀 패키지 관리 (uv)

**중요**: Docker 환경에서 **uv**를 사용하여 초고속 패키지 설치

### uv란?
- Rust로 작성된 차세대 Python 패키지 매니저
- pip/Poetry보다 **10-100배 빠른** 패키지 설치
- pyproject.toml 표준 지원
- Docker 환경에 최적화

## 🐳 Docker 기반 개발 (권장)

**가상환경 불필요**: Docker 컨테이너 자체가 격리된 환경

### 기본 명령어
```bash
# 전체 스택 실행 (백엔드 + DB + Redis)
docker-compose up

# 백엔드만 실행
docker-compose up backend

# 백그라운드 실행
docker-compose up -d backend

# 로그 확인
docker-compose logs -f backend

# 컨테이너 종료
docker-compose down
```

### 패키지 관리
```bash
# 새 패키지 추가 (pyproject.toml 수정 후)
docker-compose build backend

# 또는 실행 중인 컨테이너에서
docker-compose exec backend uv pip install --system [패키지명]

# 개발 의존성 추가 (pyproject.toml [project.optional-dependencies])
docker-compose exec backend uv pip install --system -e ".[dev,test]"
```

### 개발 워크플로우
1. 로컬에서 코드 작성 (에디터/IDE)
2. Docker에서 자동 reload (볼륨 마운트)
3. 의존성 추가 시 pyproject.toml 수정 → 빌드

## 📁 프로젝트 구조

```
backend/
├── pyproject.toml       # uv 패키지 관리
├── Dockerfile.dev       # 개발용 Docker
├── scripts/             # 유틸리티 스크립트 ✨ 신규
│   └── add_test_tips.py # 테스트 데이터 생성 (5개 샘플)
├── app/
│   ├── main.py          # FastAPI 진입점
│   ├── core/            # 코어 모듈
│   │   ├── config/      # 설정 (database, settings)
│   │   ├── cache/       # Redis 캐시 (4개 모듈) ✨ 리팩토링
│   │   ├── security/    # JWT, 암호화
│   │   └── dependencies.py
│   ├── api/v1/          # API 엔드포인트
│   │   ├── api.py       # 라우터 통합
│   │   └── endpoints/   # 개별 엔드포인트
│   ├── models/          # SQLAlchemy 모델
│   ├── schemas/         # Pydantic 스키마
│   └── services/        # 비즈니스 로직
│       ├── tip/         # Tip 서비스 (4개 모듈) ✨ 리팩토링
│       └── terminal/    # 터미널 서비스 (4개 모듈) ✨ 리팩토링
└── tests/
    ├── conftest.py      # pytest 설정
    ├── test_models/     # 모델 테스트
    ├── test_schemas/    # 스키마 테스트
    ├── test_api/        # API 통합 테스트
    └── test_services/   # Service 레이어 테스트
```

## 🔧 VS Code 설정 (선택적)

### Docker Remote Container (추천)
- Docker Extension 설치
- 컨테이너 내부에서 직접 개발
- 완벽한 환경 일치

### 로컬 Python 인터프리터 (선택적)
로컬에서 IDE 지원이 필요한 경우:
```bash
# uv 설치 (macOS)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 로컬 가상환경 생성
cd backend
uv venv
source .venv/bin/activate
uv pip install -e ".[dev,test]"
```

## 📝 중요 노트
- **Docker가 메인 개발 환경** (가상환경 불필요)
- **uv로 초고속 패키지 설치** (10-100배 빠름)
- pyproject.toml 표준 형식 사용
- 로컬 Python 환경은 선택적 (IDE 지원용)

---

## 🎲 테스트 데이터 관리 (Day 23-24 추가)

### 테스트 팁 데이터 생성

**스크립트**: `backend/scripts/add_test_tips.py` (262줄)

**기능**:
- 프론트엔드 개발 및 통합 테스트를 위한 샘플 팁 데이터 생성
- 기존 데이터 클린업 → 5개 샘플 삽입
- 완전한 `Tip` 모델 구조 (terminal_setup, category, difficulty 포함)

**생성되는 데이터**:
1. **오늘 팁** (초급): "ls 명령어로 파일 목록 보기"
2. **어제 팁** (중급): "파이프(|)로 명령어 연결하기"
3. **2일 전 팁** (고급): "find와 xargs로 파일 일괄 처리하기"
4. **3일 전 팁** (초급): "cd 명령어로 디렉토리 이동하기"
5. **4일 전 팁** (중급): "grep으로 파일 내용 검색하기"

### 실행 방법

```bash
# Docker 환경에서 실행 (추천)
docker-compose exec backend python scripts/add_test_tips.py

# 출력 예시
🚀 테스트 팁 데이터 추가 시작...
⚠️  기존 팁 5개 발견. 삭제 후 진행합니다.
✅ 기존 데이터 삭제 완료
✅ 테스트 팁 5개 추가 완료!
   - 오늘: ls 명령어로 파일 목록 보기 (초급)
   - 어제: 파이프(|)로 명령어 연결하기 (중급)
   - 2일 전: find와 xargs로 파일 일괄 처리하기 (고급)
   - 3일 전: cd 명령어로 디렉토리 이동하기 (초급)
   - 4일 전: grep으로 파일 내용 검색하기 (중급)
```

### 사용 시나리오

1. **프론트엔드 개발**: MSW 제거 후 실제 백엔드 데이터로 UI 확인
2. **API 통합 테스트**: 홈페이지, Tips 페이지 동작 검증
3. **데모/프리뷰**: 스테이징 환경 데이터 준비

### 주의사항

- **개발 환경 전용**: 프로덕션에서는 사용하지 마세요
- **멱등성**: 여러 번 실행해도 안전 (기존 데이터 삭제 후 재생성)
- **PostgreSQL 연결 필요**: Docker Compose 환경에서 실행 권장

---

## 🏗️ 서비스 모듈 아키텍처 (2025-11-03 리팩토링)

### 리팩토링 개요
**목표**: 300줄 이상 장문 파일을 Single Responsibility Principle에 따라 모듈화
**결과**: 3개 파일 (1,575줄) → 12개 모듈로 분리

### 모듈 분리 전략

#### 1. Tip 서비스 (`app/services/tip/`)
```
tip_service.py (582줄) → 4개 모듈
├── tip_crud.py          # CRUD 작업 (create, update, delete, increment)
├── tip_query.py         # 조회 작업 + 캐싱 전략 (daily, by_id, list)
├── tip_cache.py         # 캐시 무효화 (invalidate_tip_cache)
└── tip_service.py       # 조율 레이어 (다른 모듈에 위임)
```

**캐싱 전략**:
- `tip:daily:{date}` - 24시간 TTL (일일 팁)
- `tip:detail:{id}` - 1시간 TTL (관리자 수정 가능)
- `tips:list:*` - 10분 TTL (빠른 반영)

#### 2. 터미널 서비스 (`app/services/terminal/`)
```
terminal_service.py (570줄) → 4개 모듈
├── session_manager.py      # 세션 CRUD (create, get, terminate)
├── session_lifecycle.py    # 생명주기 관리 (expiry, cleanup, stats)
├── command_executor.py     # 명령어 실행 로직
└── terminal_service.py     # 조율 레이어
```

**핵심 상수**:
- `SESSION_EXPIRY_MINUTES = 30` - 세션 타임아웃
- 멱등성 보장 (terminate는 여러 번 호출 가능)

#### 3. Redis 캐시 (`app/core/cache/`)
```
cache.py (423줄) → 4개 모듈
├── redis_serialization.py  # JSON 인코더 (datetime 처리)
├── redis_connection.py     # 연결 관리 (connect, disconnect)
├── redis_operations.py     # CRUD 작업 (get, set, delete, clear_pattern)
└── cache_service.py        # CacheService 인터페이스
```

**주요 개선사항**:
- CustomJSONEncoder로 datetime 자동 직렬화
- SCAN을 사용한 패턴 기반 삭제 (블로킹 방지)
- 손상된 캐시 데이터 자동 삭제
- 에러 처리 표준화 (logger 사용)

### Backward Compatibility
각 패키지의 `__init__.py`에서 메인 클래스를 재export하여 기존 import 경로 유지:
```python
# app/services/tip/__init__.py
from app.services.tip.tip_service import TipService
__all__ = ["TipService"]

# 기존 코드 그대로 동작
from app.services.tip import TipService
```

### 테스트 검증
- **266개 테스트 100% 통과** (리팩토링 전후 동일)
- 기능 변경 없이 구조만 개선
- 백업 파일 보관 (`.backup` 확장자)

**상세 문서**: `backend/docs/service-refactoring-report.md`

---

## 🧪 TDD (Test-Driven Development) 전략

### Day 12-13부터 적용

Day 10-11에서 **129개 테스트 100% 통과**로 검증된 TDD 방식을 앞으로 모든 개발에 적용합니다.

### TDD 사이클: RED → GREEN → REFACTOR

1. **RED**: 실패하는 테스트 먼저 작성
2. **GREEN**: 테스트를 통과하는 최소 코드 구현
3. **REFACTOR**: 테스트 통과 상태 유지하며 코드 개선

### 테스트 구조

```
tests/
├── conftest.py                    # ✅ pytest 설정 (완료)
├── test_models/                   # ✅ 90개 테스트 (완료)
├── test_schemas/                  # ✅ 39개 테스트 (완료)
├── test_api/                      # ⏳ API 통합 테스트
│   ├── test_tips_api.py           # Tips CRUD
│   └── test_auth_api.py           # 인증 (Day 14)
└── test_services/                 # ⏳ 비즈니스 로직 테스트
    └── test_tip_service.py
```

### pytest 명령어

```bash
# 전체 테스트
docker-compose exec backend pytest tests/ -v

# 특정 파일/테스트
docker-compose exec backend pytest tests/test_api/test_tips_api.py -v
docker-compose exec backend pytest tests/test_api/test_tips_api.py::test_get_daily_tip -v

# 커버리지 확인
docker-compose exec backend pytest tests/ --cov=app --cov-report=html

# 실패한 테스트만 재실행
docker-compose exec backend pytest tests/ --lf
```

### 테스트 작성 가이드라인

- **AAA 패턴**: Arrange (준비) → Act (실행) → Assert (검증)
- **하나의 테스트, 하나의 검증**: 각 테스트는 한 가지만 검증
- **독립성**: 테스트 간 의존성 없이 독립적으로 실행 가능
- **명확한 이름**: `test_get_daily_tip_returns_404_when_no_tip` 처럼 동작이 명확하게
- **실패 메시지**: assert에 설명 추가 `assert result is not None, "Daily tip should exist"`

### TDD의 이점 (Day 10-11 실증)

1. **버그 조기 발견**: 9개 이슈를 배포 전 발견
2. **리팩토링 안전성**: 129개 테스트가 안전망 역할
3. **문서화**: 테스트 = 실행 가능한 사용 예시
4. **설계 개선**: 테스트 가능한 코드 = 잘 설계된 코드

---

## ⚠️ Error Handling & Logging (리팩토링 추가)

### 핵심 구성 요소
- **AppException**: 비즈니스 로직 에러 처리 (HTTP 상태 코드 포함)
- **전역 예외 핸들러**: SQLAlchemyError, ValidationError 자동 처리
- **구조화 로깅**: logger.info/warning/error로 체계적 로깅 (모든 print() 제거)
- **에러 트래킹**: 모든 에러는 `exc_info=True`로 스택 트레이스 기록

### 사용 패턴
- 비즈니스 로직 에러 → `AppException` 발생
- 데이터베이스 에러 → 자동 rollback + 로깅 + AppException 변환
- Redis 에러 → logger.error() 자동 기록 + Fail-Open 정책
- 암호화/복호화 에러 → InvalidToken 명시적 처리 (401/500 구분)
- 성능 로깅 → 1초 이상 쿼리 자동 경고

### 환경 변수 설정
- **HTTP 타임아웃**: `HTTP_TIMEOUT`, `HTTP_CONNECT_TIMEOUT` (.env 설정 가능)
- **세션 TTL**: `SESSION_TTL`, `OAUTH_STATE_TTL` (.env 설정 가능)
- 환경별로 다른 타임아웃 설정 가능 (개발/프로덕션)

**상세 가이드**:
- `backend/docs/models-usage-guide.md` - Error Handling 섹션
- `backend/docs/environment-variables.md` - 환경 변수 설정 가이드

---

## 📚 주요 문서

### 개발 가이드
- `docs/models-usage-guide.md` - SQLAlchemy 사용 가이드 (Error Handling 포함)
- `docs/environment-variables.md` - 환경 변수 설정 가이드 ✨ 신규

### 아키텍처 문서
- `docs/redis-module-architecture.md` - Redis 모듈 아키텍처
- `docs/redis-refactoring-summary.md` - Redis 리팩토링 요약

### 완료 보고서
- `docs/day10-11-completion-report.md` - Day 10-11 (모델/스키마)
- `docs/day12-13-completion-report.md` - Day 12-13 (TDD, Service 계층)
- `docs/day14-completion-report.md` - Day 14 (Redis, JWT 인증)
- `docs/day21-security-optimization.md` - Day 21 (터미널 보안 최적화)
- `docs/issue-fixes-completion-report.md` - 코드 품질 이슈 수정 ✨ 신규
- `docs/service-refactoring-report.md` - 서비스 모듈 리팩토링 (3파일 → 12모듈) ✨ 신규

### 코드 품질 보고서
- `docs/code-refactoring-report.md` - 초기 리팩토링 (8.3 → 9.0/10)

---

**핵심 원칙**:
- **TDD**: 구현 전에 테스트를 작성하라! 🧪
- **코드 품질**: 9.5/10 (Day 10-11: 9.0/10 → Day 12-13: 9.2/10 → 이슈 수정: 9.5/10) 🔧
- **성능 최적화**: 데이터베이스 인덱스 전략 (복합 인덱스, GIN 인덱스) ⚡
- **환경 변수 관리**: .env 파일로 환경별 설정 분리 (개발/프로덕션) ⚙️

---

## 🤖 백엔드 에이전트 활용 (TDD 필수)

**자주 사용할 에이전트**:
- `backend-code-writer`: FastAPI 엔드포인트, SQLAlchemy 모델, 서비스 로직, 인증, WebSocket
- `unit-test-generator`: 모든 계층의 테스트 작성 (TDD의 RED 단계) ⭐⭐⭐⭐⭐
- `code-quality-evaluator`: 코드 품질 평가, 보안 점검
- `code-refactoring-specialist`: 코드 개선 (TDD의 REFACTOR 단계)
- `service-planner`: 시스템 아키텍처 설계
- `general-purpose`: 함수/클래스 사용처 검색, 패턴 분석

**TDD 워크플로우 (Day 12-13부터 필수)**:
1. unit-test-generator: 실패하는 테스트 작성 (RED)
2. backend-code-writer: 테스트 통과하는 최소 코드 구현 (GREEN)
3. pytest 실행 → 통과 확인
4. code-refactoring-specialist: 코드 개선 (REFACTOR)
5. pytest 재실행 → 여전히 통과 확인

**핵심**: 테스트를 먼저 작성하고 구현하세요! (Day 10-11: 129개 테스트 100% 통과 실증)