"""
헬스 체크 엔드포인트

서버 상태 및 버전 정보를 제공하는 헬스 체크 API입니다.
모니터링 및 로드밸런서 헬스 체크에 사용됩니다.
Day 14에서 Redis 연결 상태 확인 기능을 추가했습니다.
"""

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_async_session as get_db
from app.core.cache import CacheService
from app.core.config import settings
from app.core.dependencies import get_cache

router = APIRouter()


@router.get("/health", summary="헬스 체크", tags=["health"])
async def health_check() -> dict[str, Any]:
    """
    서버 헬스 체크

    서버가 정상적으로 실행 중인지 확인합니다.
    로드밸런서 및 모니터링 시스템에서 사용됩니다.

    Returns:
        dict: 서버 상태 정보
            - status: 서버 상태 (healthy)
            - version: API 버전
            - environment: 실행 환경 (development/staging/production)

    Example:
        ```
        GET /api/v1/health

        Response:
        {
            "status": "healthy",
            "version": "0.1.0",
            "environment": "development"
        }
        ```

    Note:
        - 인증 불필요
        - 항상 200 OK 반환 (서버가 실행 중인 경우)
        - 상세 헬스 체크는 /api/v1/health/detailed 사용
    """
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


@router.get("/health/detailed", summary="상세 헬스 체크", tags=["health"])
async def detailed_health_check(
    db: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
) -> dict[str, Any]:
    """
    상세 헬스 체크 (DB 및 Redis 연결 상태 포함)

    서버뿐만 아니라 데이터베이스 및 Redis 연결 상태까지 확인합니다.
    모니터링 도구에서 사용할 수 있습니다.

    Args:
        db: 데이터베이스 세션 (자동 주입)
        cache: Redis 캐시 서비스 (자동 주입)

    Returns:
        dict: 상세 서버 상태 정보
            - status: 전체 상태 (healthy/unhealthy)
            - version: API 버전
            - environment: 실행 환경
            - services: 각 서비스별 상태
                - database: PostgreSQL 연결 상태
                - redis: Redis 연결 상태

    Example:
        ```
        GET /api/v1/health/detailed

        Response:
        {
            "status": "healthy",
            "version": "0.1.0",
            "environment": "development",
            "services": {
                "database": {
                    "status": "connected",
                    "message": "PostgreSQL 연결 정상"
                },
                "redis": {
                    "status": "connected",
                    "message": "Redis 연결 정상"
                }
            }
        }
        ```

    Note:
        - 인증 불필요
        - 모든 서비스가 정상일 때만 status: "healthy"
        - Day 10-11: PostgreSQL 연결 확인 구현
        - Day 14: Redis 연결 확인 구현
    """
    services_status = {}

    # PostgreSQL 연결 확인
    db_status = "connected"
    db_message = "PostgreSQL 연결 정상"
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar_one()
    except Exception as e:
        db_status = "disconnected"
        db_message = f"PostgreSQL 연결 실패: {str(e)}"

    services_status["database"] = {
        "status": db_status,
        "message": db_message,
    }

    # Redis 연결 확인 (Day 14 구현)
    redis_status = "connected"
    redis_message = "Redis 연결 정상"
    try:
        # 간단한 캐시 쓰기/읽기 테스트
        test_key = "health:check:test"
        test_value = {"status": "ok", "timestamp": "now"}

        await cache.set(test_key, test_value, ttl=10)
        cached_value = await cache.get(test_key)
        await cache.delete(test_key)

        if not cached_value or cached_value.get("status") != "ok":
            redis_status = "disconnected"
            redis_message = "Redis 캐시 동작 실패"
    except Exception as e:
        redis_status = "disconnected"
        redis_message = f"Redis 연결 실패: {str(e)}"

    services_status["redis"] = {
        "status": redis_status,
        "message": redis_message,
    }

    # 전체 상태 판단
    all_healthy = all(
        service["status"] == "connected" for service in services_status.values()
    )

    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "services": services_status,
    }
