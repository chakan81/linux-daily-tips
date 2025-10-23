"""
FastAPI 애플리케이션 진입점

Linux Daily Tips Backend API의 메인 애플리케이션입니다.
CORS, 라우터 등록, 애플리케이션 라이프사이클 이벤트를 관리합니다.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.exceptions import setup_exception_handlers
from app.core.rate_limit import limiter

# 로깅 시스템 초기화 (기본 logging 설정)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    애플리케이션 라이프사이클 이벤트 관리

    애플리케이션 시작 시 초기화 작업을 수행하고,
    종료 시 정리 작업을 수행합니다.

    Yields:
        None

    Note:
        - Day 10-11에서 데이터베이스 연결 초기화 추가 예정
        - Day 14에서 Redis 연결 초기화 추가 예정
    """
    # 애플리케이션 시작 시
    logger.info(f"🚀 Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"📝 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🔒 Debug mode: {settings.DEBUG}")

    # TODO: Day 10-11에서 데이터베이스 연결 초기화
    # logger.info("🗄️  Initializing database connection...")
    # await init_db()

    # TODO: Day 14에서 Redis 연결 초기화
    # logger.info("📦 Initializing Redis connection...")
    # await init_redis()

    logger.info("✅ Application startup complete")

    yield

    # 애플리케이션 종료 시
    logger.info(f"👋 Shutting down {settings.PROJECT_NAME}")

    # TODO: Day 10-11에서 데이터베이스 연결 종료
    # logger.info("🗄️  Closing database connection...")
    # await close_db()

    # TODO: Day 14에서 Redis 연결 종료
    # logger.info("📦 Closing Redis connection...")
    # await close_redis()

    logger.info("✅ Application shutdown complete")


# FastAPI 애플리케이션 생성
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="리눅스 일일 팁을 제공하고 웹 터미널 환경을 제공하는 교육용 웹서비스 API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Rate Limiter 등록
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 전역 예외 핸들러 등록
setup_exception_handlers(app)

# CORS 미들웨어 설정 (환경별 origins 자동 선택)
cors_origins = settings.cors_origins_list
logger.info(f"CORS origins 설정: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API v1 라우터 등록
app.include_router(api_router, prefix=settings.API_V1_STR)

logger.info("FastAPI 애플리케이션 설정 완료")


@app.get("/", tags=["root"])
async def root():
    """
    루트 엔드포인트

    API 정보 및 문서 링크를 제공합니다.

    Returns:
        dict: API 정보
            - message: 프로젝트 이름
            - version: API 버전
            - docs: Swagger UI 링크
            - redoc: ReDoc 링크
            - api_v1: API v1 베이스 경로
    """
    return {
        "message": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "api_v1": settings.API_V1_STR,
    }
