"""
Redis 연결 관리 모듈

Redis 서버와의 연결 생성 및 종료를 담당합니다.
"""

import logging
from typing import Optional

import redis.asyncio as redis
from redis.exceptions import RedisError

from app.core.config import settings
from app.core.exceptions import AppException

# 로거 인스턴스
logger = logging.getLogger(__name__)


async def connect(redis_client_ref: list) -> redis.Redis:
    """
    Redis 서버에 비동기 연결을 초기화합니다.

    settings.REDIS_URL을 사용하여 연결합니다.
    연결 실패 시 AppException을 발생시킵니다.

    Args:
        redis_client_ref: Redis 클라이언트 참조 (리스트로 전달하여 변경 가능)

    Returns:
        redis.Redis: Redis 비동기 클라이언트

    Raises:
        AppException: Redis 연결 실패 시 (503 Service Unavailable)

    Example:
        >>> client_ref = [None]
        >>> client = await connect(client_ref)
    """
    try:
        # Redis 비동기 클라이언트 생성
        redis_client: redis.Redis = redis.from_url(  # type: ignore[no-untyped-call]
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            max_connections=50,
        )

        # 연결 테스트
        await redis_client.ping()

        # 참조 업데이트
        redis_client_ref[0] = redis_client

        logger.info(
            "Redis 연결 성공",
            extra={
                "redis_url": settings.REDIS_URL.split("@")[-1],  # 비밀번호 제외
            },
        )

        return redis_client

    except RedisError as e:
        logger.error(
            f"Redis 연결 실패: {str(e)}",
            exc_info=True,
        )
        raise AppException(
            status_code=503,
            detail="캐시 서버 연결에 실패했습니다",
        )
    except Exception as e:
        logger.error(
            f"예상치 못한 Redis 연결 오류: {str(e)}",
            exc_info=True,
        )
        raise AppException(
            status_code=503,
            detail="캐시 서버 연결에 실패했습니다",
        )


async def disconnect(redis_client: Optional[redis.Redis]) -> None:
    """
    Redis 연결을 종료합니다.

    연결된 Redis 클라이언트를 안전하게 종료합니다.

    Args:
        redis_client: Redis 클라이언트 인스턴스

    Example:
        >>> await disconnect(redis_client)
    """
    if redis_client:
        try:
            await redis_client.aclose()  # aclose() 사용 (redis 5.0.1+)
            logger.info("Redis 연결 종료")
        except Exception as e:
            logger.warning(f"Redis 연결 종료 중 오류: {str(e)}")
