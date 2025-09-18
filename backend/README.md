# Backend - Linux Daily Tips

이 디렉토리는 Linux Daily Tips 웹서비스의 백엔드 API 서버를 포함합니다.

## 기술 스택
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy 2.0
- **Authentication**: JWT
- **Terminal**: Docker (샌드박스)
- **LLM Integration**: OpenAI API / Anthropic Claude
- **Caching**: Redis

## 주요 기능
- RESTful API 서버
- 팁 콘텐츠 관리 (CRUD)
- LLM 기반 콘텐츠 자동 생성
- 드래프트 승인 워크플로우
- 웹 터미널 샌드박스 관리
- 사용자 인증 (관리자)

## API 엔드포인트 (예정)
```
GET    /api/tips/today          # 오늘의 팁
GET    /api/tips/history        # 팁 히스토리
POST   /api/tips/generate       # LLM 팁 생성 (관리자)
GET    /api/terminal/setup      # 터미널 환경 설정
POST   /api/terminal/execute    # 터미널 명령 실행
```

## 개발 계획
- **Phase 1**: 기본 API, 팁 CRUD, 간단한 터미널 연동
- **Phase 2**: LLM 연동, 드래프트 시스템, 고급 터미널
- **Phase 3**: 성능 최적화, 모니터링, 배포 자동화

## 설치 및 실행
```bash
# 가상환경 생성 (향후)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치 (향후)
pip install -r requirements.txt

# 데이터베이스 마이그레이션 (향후)
alembic upgrade head

# 개발 서버 실행 (향후)
uvicorn main:app --reload
```

## 폴더 구조 (예정)
```
backend/
├── app/
│   ├── api/             # API 라우터
│   ├── core/            # 설정, 보안
│   ├── models/          # 데이터베이스 모델
│   ├── schemas/         # Pydantic 스키마
│   ├── services/        # 비즈니스 로직
│   └── utils/           # 유틸리티 함수
├── alembic/             # 데이터베이스 마이그레이션
├── docker/              # 터미널 샌드박스
├── requirements.txt     # Python 의존성
└── main.py             # 애플리케이션 진입점
```

## 보안 고려사항
- 터미널 명령 실행 시 Docker 샌드박스 격리
- API 인증 및 권한 관리
- SQL Injection 방어
- Rate Limiting 적용