"""
FastAPI 애플리케이션 진입점

Linux Daily Tips Backend API의 메인 애플리케이션입니다.
CORS, 라우터 등록, 애플리케이션 라이프사이클 이벤트를 관리합니다.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings


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
    print(f"🚀 Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"📝 Environment: {settings.ENVIRONMENT}")
    print(f"🔒 Debug mode: {settings.DEBUG}")
    print(f"🌐 CORS origins: {settings.CORS_ORIGINS}")

    # TODO: Day 10-11에서 데이터베이스 연결 초기화
    # print("🗄️  Initializing database connection...")
    # await init_db()

    # TODO: Day 14에서 Redis 연결 초기화
    # print("📦 Initializing Redis connection...")
    # await init_redis()

    print("✅ Application startup complete")

    yield

    # 애플리케이션 종료 시
    print(f"👋 Shutting down {settings.PROJECT_NAME}")

    # TODO: Day 10-11에서 데이터베이스 연결 종료
    # print("🗄️  Closing database connection...")
    # await close_db()

    # TODO: Day 14에서 Redis 연결 종료
    # print("📦 Closing Redis connection...")
    # await close_redis()

    print("✅ Application shutdown complete")


# FastAPI 애플리케이션 생성
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="리눅스 일일 팁을 제공하고 웹 터미널 환경을 제공하는 교육용 웹서비스 API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API v1 라우터 등록
app.include_router(api_router, prefix=settings.API_V1_STR)


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
