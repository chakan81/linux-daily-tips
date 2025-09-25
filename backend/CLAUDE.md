# Backend Development Guide

Linux Daily Tips 백엔드 개발을 위한 Claude Code 가이드입니다.

## 🐍 Python 가상환경 관리 (pipenv)

**중요**: 로컬 개발은 **pipenv** 사용, Docker는 Poetry 사용

### 기본 명령어
- `pipenv install` - 가상환경 생성 및 의존성 설치
- `pipenv install --dev` - 개발 의존성 포함 설치 (테스트, 린팅 도구 등)
- `pipenv shell` - 가상환경 활성화
- `pipenv run [명령어]` - 가상환경에서 명령 실행

### 의존성 관리
- 운영: `pipenv install fastapi uvicorn sqlalchemy`
- 개발: `pipenv install pytest black flake8 --dev`

## 🐳 이중 환경 전략

1. **Docker** (컨테이너) - Poetry + pyproject.toml
   - 운영 환경과 동일, CI/CD 사용

2. **로컬** (macOS) - pipenv + Pipfile
   - IDE 지원, 빠른 개발

### 권장 워크플로우
1. 로컬에서 코드 작성 (`pipenv shell`)
2. Docker에서 실행/테스트
3. 의존성 변경 시 두 환경 모두 업데이트

## 📁 프로젝트 구조
```
backend/
├── Pipfile              # pipenv (로컬)
├── pyproject.toml       # Poetry (Docker)
├── app/
│   ├── main.py          # FastAPI 앱
│   ├── api/             # 라우터
│   ├── models/          # DB 모델
│   ├── schemas/         # Pydantic
│   └── config/          # 설정
└── tests/               # 테스트
```

## 🔧 VS Code 설정
- `pipenv --venv`로 가상환경 경로 확인
- Python 인터프리터를 해당 경로로 설정
- 추천 확장: Python, Pylance, Black Formatter

## 📝 중요 노트
- **모든 로컬 개발은 pipenv 사용**
- Docker는 Poetry 유지 (운영 환경 일관성)
- Git에 `Pipfile`, `Pipfile.lock` 포함