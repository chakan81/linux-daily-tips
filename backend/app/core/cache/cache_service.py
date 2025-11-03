"""
Redis 캐싱 서비스 (통합 인터페이스)

Redis를 사용한 비동기 캐싱 서비스를 제공합니다.
- JSON 직렬화/역직렬화 (datetime 지원)
- TTL 기반 만료
- 패턴 기반 일괄 삭제
- 에러 핸들링 및 로깅
"""

from typing import Any, Optional

import redis.asyncio as redis

from app.core.cache import redis_connection, redis_operations


class CacheService:
    """
    Redis 비동기 캐싱 서비스

    JSON 직렬화를 지원하는 Redis 캐시 래퍼 클래스입니다.
    연결 관리, TTL 설정, 패턴 기반 삭제 등을 제공합니다.

    Attributes:
        redis_client: Redis 비동기 클라이언트 인스턴스

    Example:
        ```python
        # 의존성 주입으로 사용
        cache = CacheService()
        await cache.connect()
        await cache.set("user:123", {"name": "John"}, ttl=3600)
        data = await cache.get("user:123")
        await cache.disconnect()
        ```
    """

    def __init__(self) -> None:
        """CacheService 초기화"""
        self.redis_client: Optional[redis.Redis] = None

    async def connect(self) -> None:
        """
        Redis 서버에 비동기 연결을 초기화합니다.

        settings.REDIS_URL을 사용하여 연결합니다.
        연결 실패 시 AppException을 발생시킵니다.

        Raises:
            AppException: Redis 연결 실패 시 (503 Service Unavailable)

        Example:
            >>> cache = CacheService()
            >>> await cache.connect()
        """
        client_ref = [self.redis_client]
        self.redis_client = await redis_connection.connect(client_ref)

    async def disconnect(self) -> None:
        """
        Redis 연결을 종료합니다.

        연결된 Redis 클라이언트를 안전하게 종료합니다.

        Example:
            >>> await cache.disconnect()
        """
        await redis_connection.disconnect(self.redis_client)

    async def get(self, key: str) -> Optional[dict[str, Any]]:
        """
        캐시에서 데이터를 조회합니다.

        JSON 문자열을 파싱하여 딕셔너리로 반환합니다.
        캐시 HIT/MISS를 로깅합니다.

        Args:
            key: 조회할 캐시 키

        Returns:
            Optional[dict[str, Any]]: 캐시된 데이터 (없으면 None)

        Raises:
            AppException: Redis 조회 실패 시

        Example:
            >>> data = await cache.get("tips:daily:2024-01-01")
            >>> if data:
            >>>     print(data["title"])
        """
        if not self.redis_client:
            from app.core.exceptions import AppException

            raise AppException(
                status_code=503,
                detail="캐시 서버가 연결되지 않았습니다",
            )

        return await redis_operations.get(self.redis_client, key)

    async def set(self, key: str, value: dict[str, Any], ttl: int = 3600) -> None:
        """
        캐시에 데이터를 저장합니다.

        딕셔너리를 JSON 문자열로 직렬화하여 저장합니다.
        datetime 객체는 ISO 8601 형식으로 자동 변환됩니다.

        Args:
            key: 캐시 키
            value: 저장할 데이터 (딕셔너리)
            ttl: 만료 시간 (초, 기본값: 3600초 = 1시간)

        Raises:
            AppException: Redis 저장 실패 시

        Example:
            >>> await cache.set(
            >>>     "tips:daily:2024-01-01",
            >>>     {"title": "Linux Tip", "created_at": datetime.now()},
            >>>     ttl=86400  # 24시간
            >>> )
        """
        if not self.redis_client:
            from app.core.exceptions import AppException

            raise AppException(
                status_code=503,
                detail="캐시 서버가 연결되지 않았습니다",
            )

        await redis_operations.set(self.redis_client, key, value, ttl)

    async def delete(self, key: str) -> bool:
        """
        캐시를 삭제합니다.

        Args:
            key: 삭제할 캐시 키

        Returns:
            bool: 삭제 성공 여부 (키가 존재했으면 True)

        Raises:
            AppException: Redis 삭제 실패 시

        Example:
            >>> deleted = await cache.delete("tips:daily:2024-01-01")
            >>> if deleted:
            >>>     print("캐시가 삭제되었습니다")
        """
        if not self.redis_client:
            from app.core.exceptions import AppException

            raise AppException(
                status_code=503,
                detail="캐시 서버가 연결되지 않았습니다",
            )

        return await redis_operations.delete(self.redis_client, key)

    async def exists(self, key: str) -> bool:
        """
        캐시 존재 여부를 확인합니다.

        Args:
            key: 확인할 캐시 키

        Returns:
            bool: 캐시가 존재하면 True

        Raises:
            AppException: Redis 조회 실패 시

        Example:
            >>> if await cache.exists("tips:daily:2024-01-01"):
            >>>     print("캐시가 존재합니다")
        """
        if not self.redis_client:
            from app.core.exceptions import AppException

            raise AppException(
                status_code=503,
                detail="캐시 서버가 연결되지 않았습니다",
            )

        return await redis_operations.exists(self.redis_client, key)

    async def clear_pattern(self, pattern: str) -> int:
        """
        패턴에 맞는 모든 캐시를 삭제합니다.

        Redis SCAN 명령을 사용하여 안전하게 패턴 매칭 키를 삭제합니다.
        대량 삭제 시에도 Redis 서버를 블로킹하지 않습니다.

        Args:
            pattern: 삭제할 키 패턴 (예: "tips:*", "user:*")

        Returns:
            int: 삭제된 키의 개수

        Raises:
            AppException: Redis 삭제 실패 시

        Example:
            >>> # 모든 팁 캐시 삭제
            >>> deleted_count = await cache.clear_pattern("tips:*")
            >>> print(f"{deleted_count}개의 캐시가 삭제되었습니다")
        """
        if not self.redis_client:
            from app.core.exceptions import AppException

            raise AppException(
                status_code=503,
                detail="캐시 서버가 연결되지 않았습니다",
            )

        return await redis_operations.clear_pattern(self.redis_client, pattern)
