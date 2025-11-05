"""
FastAPI 애플리케이션 진입점

Linux Daily Tips Backend API의 메인 애플리케이션입니다.
CORS, 라우터 등록, 애플리케이션 라이프사이클 이벤트를 관리합니다.
"""

import asyncio
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

# 백그라운드 작업 제어
cleanup_task = None
should_cleanup = True


async def cleanup_expired_sessions_task():
    """
    만료된 터미널 세션을 주기적으로 정리하는 백그라운드 작업

    매 1분마다 실행되어 만료된 세션과 고아 컨테이너를 자동 삭제합니다.
    """
    try:
        from app.config.database import get_database
        from app.services.docker_service import DockerService
        from app.services.terminal import TerminalService

        logger.info("🧹 컨테이너 정리 백그라운드 작업 시작 (1분 주기)")

        docker_service = DockerService()
        terminal_service = TerminalService(docker_service=docker_service)
        db_config = get_database()

        while should_cleanup:
            try:
                # 만료된 세션 정리
                async with db_config.async_session_factory() as db:
                    cleaned_count = await terminal_service.cleanup_expired_sessions(db)
                    if cleaned_count > 0:
                        logger.info(f"🧹 만료된 세션 {cleaned_count}개 정리 완료")
                    await db.commit()

                # 고아 컨테이너 정리 (Redis에 없는 컨테이너)
                orphan_count = await docker_service.cleanup_all_containers(
                    label="app=linux-daily-tips"
                )
                if orphan_count > 0:
                    logger.info(f"🧹 고아 컨테이너 {orphan_count}개 정리 완료")

            except Exception as e:
                logger.error(f"❌ 세션 정리 중 오류 발생: {str(e)}", exc_info=True)

            # 1분 대기
            await asyncio.sleep(60)

    except Exception as e:
        logger.error(f"❌ 컨테이너 정리 백그라운드 작업 초기화 실패: {str(e)}", exc_info=True)
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    애플리케이션 라이프사이클 이벤트 관리

    애플리케이션 시작 시 초기화 작업을 수행하고,
    종료 시 정리 작업을 수행합니다.

    Yields:
        None

    Note:
        - Day 21: 컨테이너 정리 백그라운드 작업 추가
    """
    global cleanup_task, should_cleanup

    # 애플리케이션 시작 시
    logger.info(f"🚀 Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"📝 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🔒 Debug mode: {settings.DEBUG}")

    # 백그라운드 정리 작업 시작
    should_cleanup = True
    cleanup_task = asyncio.create_task(cleanup_expired_sessions_task())

    # Task 예외를 명시적으로 로그에 기록
    def task_exception_handler(task):
        try:
            task.result()
        except Exception as e:
            logger.error(f"❌ 백그라운드 작업 예외 발생: {str(e)}", exc_info=True)

    cleanup_task.add_done_callback(task_exception_handler)
    logger.info("✅ 컨테이너 정리 백그라운드 작업 등록 완료")

    logger.info("✅ Application startup complete")

    yield

    # 애플리케이션 종료 시
    logger.info(f"👋 Shutting down {settings.PROJECT_NAME}")

    # 백그라운드 작업 중지
    should_cleanup = False
    if cleanup_task:
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            logger.info("🧹 컨테이너 정리 백그라운드 작업 중지 완료")

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
