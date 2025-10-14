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
├── app/
│   ├── main.py          # FastAPI 진입점
│   ├── core/            # 설정 (config, security, dependencies)
│   ├── api/v1/          # API 엔드포인트
│   │   ├── api.py       # 라우터 통합
│   │   └── endpoints/   # 개별 엔드포인트
│   ├── models/          # SQLAlchemy 모델
│   ├── schemas/         # Pydantic 스키마
│   └── services/        # 비즈니스 로직
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
- **구조화 로깅**: logger.info/warning/error로 체계적 로깅
- **에러 트래킹**: 모든 에러는 `exc_info=True`로 스택 트레이스 기록

### 사용 패턴
- 비즈니스 로직 에러 → `AppException` 발생
- 데이터베이스 에러 → 자동 rollback + 로깅 + AppException 변환
- 성능 로깅 → 1초 이상 쿼리 자동 경고

**상세 가이드**: `backend/docs/models-usage-guide.md` Error Handling 섹션

---

## 📚 주요 문서

- `docs/models-usage-guide.md` - SQLAlchemy 사용 가이드 (리팩토링 반영)
- `docs/code-refactoring-report.md` - 코드 품질 평가 보고서
- `docs/day10-11-completion-report.md` - Day 10-11 완료 보고서

---

**핵심 원칙**:
- **TDD**: 구현 전에 테스트를 작성하라! 🧪
- **코드 품질**: 8.3 → 9.0/10 (리팩토링 완료) 🔧