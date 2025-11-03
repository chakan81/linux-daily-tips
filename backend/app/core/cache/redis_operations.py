"""
Redis CRUD 작업 모듈

Redis 캐시의 생성, 조회, 수정, 삭제 작업을 담당합니다.
"""

import json
import logging
from typing import Any, Optional

import redis.asyncio as redis
from redis.exceptions import RedisError

from app.core.cache.redis_serialization import CustomJSONEncoder
from app.core.exceptions import AppException

# 로거 인스턴스
logger = logging.getLogger(__name__)


async def get(redis_client: redis.Redis, key: str) -> Optional[dict[str, Any]]:
    """
    캐시에서 데이터를 조회합니다.

    JSON 문자열을 파싱하여 딕셔너리로 반환합니다.
    캐시 HIT/MISS를 로깅합니다.

    Args:
        redis_client: Redis 클라이언트
        key: 조회할 캐시 키

    Returns:
        Optional[dict[str, Any]]: 캐시된 데이터 (없으면 None)

    Raises:
        AppException: Redis 조회 실패 시

    Example:
        >>> data = await get(redis_client, "tips:daily:2024-01-01")
        >>> if data:
        >>>     print(data["title"])
    """
    try:
        value = await redis_client.get(key)

        if value is None:
            logger.debug(
                "캐시 MISS",
                extra={"key": key},
            )
            return None

        # JSON 역직렬화
        data: dict[str, Any] = json.loads(value)
        logger.debug(
            "캐시 HIT",
            extra={"key": key},
        )
        return data

    except json.JSONDecodeError as e:
        logger.error(
            f"JSON 파싱 실패: {str(e)}",
            extra={"key": key},
            exc_info=True,
        )
        # 잘못된 캐시 데이터 삭제
        await delete(redis_client, key)
        return None

    except RedisError as e:
        logger.error(
            f"Redis 조회 실패: {str(e)}",
            extra={"key": key},
            exc_info=True,
        )
        raise AppException(
            status_code=503,
            detail="캐시 조회에 실패했습니다",
        )


async def set(
    redis_client: redis.Redis, key: str, value: dict[str, Any], ttl: int = 3600
) -> None:
    """
    캐시에 데이터를 저장합니다.

    딕셔너리를 JSON 문자열로 직렬화하여 저장합니다.
    datetime 객체는 ISO 8601 형식으로 자동 변환됩니다.

    Args:
        redis_client: Redis 클라이언트
        key: 캐시 키
        value: 저장할 데이터 (딕셔너리)
        ttl: 만료 시간 (초, 기본값: 3600초 = 1시간)

    Raises:
        AppException: Redis 저장 실패 시

    Example:
        >>> await set(
        >>>     redis_client,
        >>>     "tips:daily:2024-01-01",
        >>>     {"title": "Linux Tip", "created_at": datetime.now()},
        >>>     ttl=86400  # 24시간
        >>> )
    """
    try:
        # JSON 직렬화 (datetime 지원)
        json_value = json.dumps(value, cls=CustomJSONEncoder)

        # Redis에 저장 (TTL 설정)
        await redis_client.setex(key, ttl, json_value)

        logger.debug(
            "캐시 저장 성공",
            extra={
                "key": key,
                "ttl": ttl,
            },
        )

    except (TypeError, ValueError) as e:
        logger.error(
            f"JSON 직렬화 실패: {str(e)}",
            extra={"key": key},
            exc_info=True,
        )
        raise AppException(
            status_code=500,
            detail="캐시 데이터 직렬화에 실패했습니다",
        )

    except RedisError as e:
        logger.error(
            f"Redis 저장 실패: {str(e)}",
            extra={"key": key},
            exc_info=True,
        )
        raise AppException(
            status_code=503,
            detail="캐시 저장에 실패했습니다",
        )


async def delete(redis_client: redis.Redis, key: str) -> bool:
    """
    캐시를 삭제합니다.

    Args:
        redis_client: Redis 클라이언트
        key: 삭제할 캐시 키

    Returns:
        bool: 삭제 성공 여부 (키가 존재했으면 True)

    Raises:
        AppException: Redis 삭제 실패 시

    Example:
        >>> deleted = await delete(redis_client, "tips:daily:2024-01-01")
        >>> if deleted:
        >>>     print("캐시가 삭제되었습니다")
    """
    try:
        result = await redis_client.delete(key)

        logger.debug(
            "캐시 삭제",
            extra={
                "key": key,
                "deleted": bool(result),
            },
        )

        return bool(result)

    except RedisError as e:
        logger.error(
            f"Redis 삭제 실패: {str(e)}",
            extra={"key": key},
            exc_info=True,
        )
        raise AppException(
            status_code=503,
            detail="캐시 삭제에 실패했습니다",
        )


async def exists(redis_client: redis.Redis, key: str) -> bool:
    """
    캐시 존재 여부를 확인합니다.

    Args:
        redis_client: Redis 클라이언트
        key: 확인할 캐시 키

    Returns:
        bool: 캐시가 존재하면 True

    Raises:
        AppException: Redis 조회 실패 시

    Example:
        >>> if await exists(redis_client, "tips:daily:2024-01-01"):
        >>>     print("캐시가 존재합니다")
    """
    try:
        result = await redis_client.exists(key)
        return bool(result)

    except RedisError as e:
        logger.error(
            f"Redis 존재 확인 실패: {str(e)}",
            extra={"key": key},
            exc_info=True,
        )
        raise AppException(
            status_code=503,
            detail="캐시 존재 확인에 실패했습니다",
        )


async def clear_pattern(redis_client: redis.Redis, pattern: str) -> int:
    """
    패턴에 맞는 모든 캐시를 삭제합니다.

    Redis SCAN 명령을 사용하여 안전하게 패턴 매칭 키를 삭제합니다.
    대량 삭제 시에도 Redis 서버를 블로킹하지 않습니다.

    Args:
        redis_client: Redis 클라이언트
        pattern: 삭제할 키 패턴 (예: "tips:*", "user:*")

    Returns:
        int: 삭제된 키의 개수

    Raises:
        AppException: Redis 삭제 실패 시

    Example:
        >>> # 모든 팁 캐시 삭제
        >>> deleted_count = await clear_pattern(redis_client, "tips:*")
        >>> print(f"{deleted_count}개의 캐시가 삭제되었습니다")
    """
    try:
        deleted_count = 0
        cursor = 0

        # SCAN 명령으로 패턴에 맞는 키를 찾아 삭제 (논블로킹)
        while True:
            cursor, keys = await redis_client.scan(
                cursor=cursor,
                match=pattern,
                count=100,  # 한 번에 100개씩 스캔
            )

            if keys:
                # 파이프라인으로 일괄 삭제
                async with redis_client.pipeline() as pipe:
                    for key in keys:
                        pipe.delete(key)
                    results = await pipe.execute()
                    deleted_count += sum(results)

            # 커서가 0이면 스캔 완료
            if cursor == 0:
                break

        logger.info(
            "패턴 기반 캐시 삭제 완료",
            extra={
                "pattern": pattern,
                "deleted_count": deleted_count,
            },
        )

        return deleted_count

    except RedisError as e:
        logger.error(
            f"Redis 패턴 삭제 실패: {str(e)}",
            extra={"pattern": pattern},
            exc_info=True,
        )
        raise AppException(
            status_code=503,
            detail="캐시 패턴 삭제에 실패했습니다",
        )
