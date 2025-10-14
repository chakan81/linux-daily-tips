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
├── pyproject.toml       # uv 패키지 관리 (PEP 621 표준)
├── Dockerfile.dev       # 개발용 Docker (uv 기반)
├── Dockerfile           # 프로덕션 Docker (uv 기반)
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI 앱 진입점
│   ├── core/            # 핵심 설정
│   │   ├── config.py    # 환경변수 설정
│   │   ├── security.py  # 보안 유틸리티
│   │   └── dependencies.py  # FastAPI 의존성
│   ├── api/             # API 엔드포인트
│   │   └── v1/          # API 버전 1
│   │       ├── api.py   # 라우터 통합
│   │       └── endpoints/  # 엔드포인트들
│   ├── models/          # SQLAlchemy 모델
│   ├── schemas/         # Pydantic 스키마
│   └── services/        # 비즈니스 로직
└── tests/               # 테스트
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

# 로컬 가상환경 생성 (선택적)
cd backend
uv venv
source .venv/bin/activate
uv pip install -e ".[dev,test]"
```

- Python 인터프리터: `.venv/bin/python`
- 추천 확장: Python, Pylance, Black Formatter

## 📝 중요 노트
- **Docker가 메인 개발 환경** (가상환경 불필요)
- **uv로 초고속 패키지 설치** (10-100배 빠름)
- pyproject.toml 표준 형식 사용
- 로컬 Python 환경은 선택적 (IDE 지원용)