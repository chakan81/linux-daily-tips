"""
CacheService 유닛 테스트 (TDD RED 단계)

테스트 범위:
- 연결 관리 (connect, disconnect, connection errors)
- 기본 CRUD (set, get, delete, exists)
- JSON 직렬화 (datetime, nested dict, invalid objects)
- 패턴 기반 삭제 (clear_pattern)
- 에러 핸들링 (Redis 연결 끊김, 타임아웃)
- 엣지 케이스 (empty dict, large values)

총 20개 테스트
"""

import asyncio
import json
from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import RedisError, TimeoutError as RedisTimeoutError

from app.core.cache import CacheService, CustomJSONEncoder
from app.core.exceptions import AppException


# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def cache_service() -> CacheService:
    """
    CacheService 인스턴스 반환 (연결 전)

    각 테스트마다 새로운 인스턴스를 제공합니다.
    """
    return CacheService()


@pytest.fixture
async def connected_cache_service() -> CacheService:
    """
    Redis에 연결된 CacheService 인스턴스 반환

    테스트 종료 후 생성된 모든 키를 정리하고 연결을 종료합니다.
    실제 Redis 서버(redis://localhost:6379/1)가 필요합니다.
    """
    cache = CacheService()
    await cache.connect()

    # 테스트용 키 추적 (정리용)
    created_keys: list[str] = []

    # 원본 set 메서드를 래핑하여 키 추적
    original_set = cache.set

    async def tracked_set(key: str, value: dict[str, Any], ttl: int = 3600) -> None:
        created_keys.append(key)
        await original_set(key, value, ttl)

    cache.set = tracked_set  # type: ignore[method-assign]

    yield cache

    # 정리: 생성된 모든 키 삭제
    if cache.redis_client:
        for key in created_keys:
            try:
                await cache.redis_client.delete(key)
            except Exception:
                pass  # 이미 삭제된 키는 무시

    # 연결 종료
    await cache.disconnect()


# ============================================================
# 1. 연결 관리 테스트 (3개)
# ============================================================


@pytest.mark.asyncio
@pytest.mark.unit
class TestCacheConnection:
    """CacheService 연결 관리 테스트"""

    async def test_connect_success(self, cache_service: CacheService) -> None:
        """
        Redis 연결 성공

        정상적인 Redis 서버에 연결하면 redis_client가 설정되고
        ping이 성공합니다.
        """
        # Act
        await cache_service.connect()

        # Assert
        assert cache_service.redis_client is not None
        # ping이 성공하면 True 반환
        pong = await cache_service.redis_client.ping()
        assert pong is True

        # Cleanup
        await cache_service.disconnect()

    async def test_connect_failure_invalid_url(self) -> None:
        """
        잘못된 URL로 연결 실패 시 AppException 발생

        존재하지 않는 Redis 서버에 연결하면 AppException이
        발생합니다 (503 Service Unavailable).
        """
        # Arrange
        cache = CacheService()

        # Mock settings to use invalid URL
        with patch("app.core.cache.settings") as mock_settings:
            mock_settings.REDIS_URL = "redis://invalid-host:9999/1"

            # Act & Assert
            with pytest.raises(AppException) as exc_info:
                await cache.connect()

            assert exc_info.value.status_code == 503
            assert "캐시 서버 연결에 실패했습니다" in exc_info.value.detail

    async def test_disconnect(self, connected_cache_service: CacheService) -> None:
        """
        Redis 연결 종료

        disconnect() 호출 시 Redis 클라이언트가 안전하게 종료됩니다.
        """
        # Arrange
        cache = connected_cache_service
        assert cache.redis_client is not None

        # Act
        await cache.disconnect()

        # Assert
        # redis_client는 close되었지만 여전히 객체는 존재
        # (재연결을 위해 None으로 설정하지 않음)
        assert cache.redis_client is not None


# ============================================================
# 2. 기본 CRUD 테스트 (5개)
# ============================================================


@pytest.mark.asyncio
@pytest.mark.unit
class TestCacheCRUD:
    """CacheService 기본 CRUD 동작 테스트"""

    async def test_set_and_get_success(
        self, connected_cache_service: CacheService
    ) -> None:
        """
        데이터 저장 후 조회 성공

        set()으로 저장한 데이터를 get()으로 조회할 수 있습니다.
        """
        # Arrange
        cache = connected_cache_service
        key = "test:user:123"
        value = {"name": "John Doe", "age": 30}

        # Act
        await cache.set(key, value, ttl=60)
        result = await cache.get(key)

        # Assert
        assert result is not None
        assert result == value
        assert result["name"] == "John Doe"
        assert result["age"] == 30

    async def test_get_nonexistent_key_returns_none(
        self, connected_cache_service: CacheService
    ) -> None:
        """
        존재하지 않는 키 조회 시 None 반환

        Redis에 존재하지 않는 키를 조회하면 None을 반환합니다.
        """
        # Arrange
        cache = connected_cache_service
        key = "test:nonexistent:key"

        # Act
        result = await cache.get(key)

        # Assert
        assert result is None

    async def test_set_with_ttl_expires(
        self, connected_cache_service: CacheService
    ) -> None:
        """
        TTL 설정 후 만료 확인

        TTL을 짧게 설정하면 시간이 지난 후 키가 자동으로 삭제됩니다.
        """
        # Arrange
        cache = connected_cache_service
        key = "test:ttl:key"
        value = {"message": "This will expire"}
        ttl = 1  # 1초

        # Act
        await cache.set(key, value, ttl=ttl)

        # 즉시 조회 (존재해야 함)
        result_before = await cache.get(key)
        assert result_before is not None

        # TTL 대기
        await asyncio.sleep(ttl + 0.5)

        # 만료 후 조회 (None이어야 함)
        result_after = await cache.get(key)

        # Assert
        assert result_after is None

    async def test_delete_success(
        self, connected_cache_service: CacheService
    ) -> None:
        """
        캐시 삭제 성공

        delete()를 호출하면 캐시가 삭제되고 True를 반환합니다.
        """
        # Arrange
        cache = connected_cache_service
        key = "test:delete:key"
        value = {"data": "to be deleted"}

        await cache.set(key, value)

        # Act
        deleted = await cache.delete(key)

        # Assert
        assert deleted is True

        # 삭제 후 조회 시 None 반환
        result = await cache.get(key)
        assert result is None

    async def test_exists_returns_true_when_key_exists(
        self, connected_cache_service: CacheService
    ) -> None:
        """
        키 존재 여부 확인

        exists()는 키가 존재하면 True, 없으면 False를 반환합니다.
        """
        # Arrange
        cache = connected_cache_service
        key = "test:exists:key"
        value = {"data": "exists"}

        # Act
        await cache.set(key, value)
        exists_before = await cache.exists(key)

        await cache.delete(key)
        exists_after = await cache.exists(key)

        # Assert
        assert exists_before is True
        assert exists_after is False


# ============================================================
# 3. JSON 직렬화 테스트 (3개)
# ============================================================


@pytest.mark.asyncio
@pytest.mark.unit
class TestCacheJSONSerialization:
    """CacheService JSON 직렬화/역직렬화 테스트"""

    async def test_set_get_with_datetime(
        self, connected_cache_service: CacheService
    ) -> None:
        """
        datetime 객체 직렬화/역직렬화

        datetime 객체를 포함한 딕셔너리를 저장하면
        CustomJSONEncoder가 ISO 8601 문자열로 변환합니다.
        """
        # Arrange
        cache = connected_cache_service
        key = "test:datetime:key"
        now = datetime.now(timezone.utc)
        value = {
            "created_at": now,
            "title": "Test with datetime",
        }

        # Act
        await cache.set(key, value)
        result = await cache.get(key)

        # Assert
        assert result is not None
        assert result["title"] == "Test with datetime"
        # datetime은 ISO 8601 문자열로 저장됨
        assert isinstance(result["created_at"], str)
        assert result["created_at"] == now.isoformat()

    async def test_set_get_complex_nested_dict(
        self, connected_cache_service: CacheService
    ) -> None:
        """
        중첩된 딕셔너리 저장/조회

        복잡한 중첩 구조의 딕셔너리도 정상적으로 저장/조회됩니다.
        """
        # Arrange
        cache = connected_cache_service
        key = "test:nested:dict"
        value = {
            "user": {
                "id": "user_123",
                "profile": {
                    "name": "Alice",
                    "settings": {
                        "theme": "dark",
                        "notifications": True,
                    },
                },
            },
            "metadata": {
                "tags": ["python", "redis", "cache"],
                "count": 42,
            },
        }

        # Act
        await cache.set(key, value)
        result = await cache.get(key)

        # Assert
        assert result is not None
        assert result == value
        assert result["user"]["profile"]["settings"]["theme"] == "dark"
        assert result["metadata"]["tags"] == ["python", "redis", "cache"]

    async def test_set_invalid_json_raises_exception(
        self, connected_cache_service: CacheService
    ) -> None:
        """
        직렬화 불가능한 객체 저장 시 AppException 발생

        JSON으로 직렬화할 수 없는 객체(set, custom class 등)를
        저장하려고 하면 AppException이 발생합니다.
        """
        # Arrange
        cache = connected_cache_service
        key = "test:invalid:object"

        # set 객체는 JSON 직렬화 불가능
        value = {"data": {1, 2, 3}}  # type: ignore[dict-item]

        # Act & Assert
        with pytest.raises(AppException) as exc_info:
            await cache.set(key, value)

        assert exc_info.value.status_code == 500
        assert "캐시 데이터 직렬화에 실패했습니다" in exc_info.value.detail


# ============================================================
# 4. 패턴 삭제 테스트 (2개)
# ============================================================


@pytest.mark.asyncio
@pytest.mark.unit
class TestCachePatternDelete:
    """CacheService 패턴 기반 삭제 테스트"""

    async def test_clear_pattern_deletes_matching_keys(
        self, connected_cache_service: CacheService
    ) -> None:
        """
        패턴에 맞는 키 일괄 삭제

        clear_pattern()은 와일드카드 패턴에 매칭되는 모든 키를
        삭제하고 삭제된 개수를 반환합니다.
        """
        # Arrange
        cache = connected_cache_service

        # 여러 키 생성
        await cache.set("tips:daily:2024-01-01", {"title": "Tip 1"})
        await cache.set("tips:daily:2024-01-02", {"title": "Tip 2"})
        await cache.set("tips:daily:2024-01-03", {"title": "Tip 3"})
        await cache.set("user:123", {"name": "Alice"})  # 다른 패턴

        # Act
        deleted_count = await cache.clear_pattern("tips:daily:*")

        # Assert
        assert deleted_count == 3

        # tips:daily:* 키는 모두 삭제됨
        assert await cache.exists("tips:daily:2024-01-01") is False
        assert await cache.exists("tips:daily:2024-01-02") is False
        assert await cache.exists("tips:daily:2024-01-03") is False

        # 다른 패턴의 키는 유지됨
        assert await cache.exists("user:123") is True

    async def test_clear_pattern_with_no_matches(
        self, connected_cache_service: CacheService
    ) -> None:
        """
        매칭 키가 없을 때 정상 동작

        패턴에 맞는 키가 없으면 0을 반환하고 에러 없이 종료됩니다.
        """
        # Arrange
        cache = connected_cache_service

        # Act
        deleted_count = await cache.clear_pattern("nonexistent:*")

        # Assert
        assert deleted_count == 0


# ============================================================
# 5. 에러 핸들링 테스트 (3개)
# ============================================================


@pytest.mark.asyncio
@pytest.mark.unit
class TestCacheErrorHandling:
    """CacheService 에러 처리 테스트"""

    async def test_get_when_redis_disconnected(
        self, cache_service: CacheService
    ) -> None:
        """
        Redis 연결 끊긴 상태에서 조회 시 AppException 발생

        redis_client가 None인 상태에서 get()을 호출하면
        AppException이 발생합니다.
        """
        # Arrange
        cache = cache_service
        # redis_client가 None인 상태 (연결 안 함)

        # Act & Assert
        with pytest.raises(AppException) as exc_info:
            await cache.get("test:key")

        assert exc_info.value.status_code == 503
        assert "캐시 서버가 연결되지 않았습니다" in exc_info.value.detail

    async def test_set_when_redis_disconnected(
        self, cache_service: CacheService
    ) -> None:
        """
        Redis 연결 끊긴 상태에서 저장 시 AppException 발생

        redis_client가 None인 상태에서 set()을 호출하면
        AppException이 발생합니다.
        """
        # Arrange
        cache = cache_service
        # redis_client가 None인 상태 (연결 안 함)

        # Act & Assert
        with pytest.raises(AppException) as exc_info:
            await cache.set("test:key", {"data": "value"})

        assert exc_info.value.status_code == 503
        assert "캐시 서버가 연결되지 않았습니다" in exc_info.value.detail

    async def test_connection_timeout(self) -> None:
        """
        Redis 연결 타임아웃 처리

        Redis 서버가 응답하지 않으면 타임아웃 에러가 발생하고
        AppException으로 변환됩니다.
        """
        # Arrange
        cache = CacheService()

        # Mock Redis client to raise timeout error
        with patch("app.core.cache.redis.from_url") as mock_from_url:
            mock_client = AsyncMock()
            mock_client.ping.side_effect = RedisTimeoutError("Connection timeout")
            mock_from_url.return_value = mock_client

            # Act & Assert
            with pytest.raises(AppException) as exc_info:
                await cache.connect()

            assert exc_info.value.status_code == 503
            assert "캐시 서버 연결에 실패했습니다" in exc_info.value.detail


# ============================================================
# 6. 엣지 케이스 테스트 (2개)
# ============================================================


@pytest.mark.asyncio
@pytest.mark.unit
class TestCacheEdgeCases:
    """CacheService 엣지 케이스 테스트"""

    async def test_set_empty_dict(
        self, connected_cache_service: CacheService
    ) -> None:
        """
        빈 딕셔너리 저장/조회

        빈 딕셔너리도 정상적으로 저장하고 조회할 수 있습니다.
        """
        # Arrange
        cache = connected_cache_service
        key = "test:empty:dict"
        value: dict[str, Any] = {}

        # Act
        await cache.set(key, value)
        result = await cache.get(key)

        # Assert
        assert result is not None
        assert result == {}
        assert isinstance(result, dict)

    async def test_set_large_value(
        self, connected_cache_service: CacheService
    ) -> None:
        """
        큰 데이터 저장 (1MB 이상)

        큰 데이터도 정상적으로 저장하고 조회할 수 있습니다.
        Redis 기본 최대 값 크기는 512MB입니다.
        """
        # Arrange
        cache = connected_cache_service
        key = "test:large:value"

        # 약 1MB 크기의 데이터 생성
        large_string = "x" * (1024 * 1024)  # 1MB
        value = {
            "data": large_string,
            "size": len(large_string),
        }

        # Act
        await cache.set(key, value, ttl=10)  # 짧은 TTL로 메모리 절약
        result = await cache.get(key)

        # Assert
        assert result is not None
        assert result["size"] == 1024 * 1024
        assert len(result["data"]) == 1024 * 1024


# ============================================================
# 7. CustomJSONEncoder 테스트 (보너스 2개)
# ============================================================


@pytest.mark.unit
class TestCustomJSONEncoder:
    """CustomJSONEncoder 단위 테스트"""

    def test_encode_datetime(self) -> None:
        """
        datetime 객체를 ISO 8601 문자열로 인코딩

        CustomJSONEncoder는 datetime 객체를 isoformat()으로 변환합니다.
        """
        # Arrange
        now = datetime(2024, 1, 15, 12, 30, 45, tzinfo=timezone.utc)
        data = {"timestamp": now}

        # Act
        json_str = json.dumps(data, cls=CustomJSONEncoder)
        result = json.loads(json_str)

        # Assert
        assert result["timestamp"] == now.isoformat()
        assert result["timestamp"] == "2024-01-15T12:30:45+00:00"

    def test_encode_regular_types(self) -> None:
        """
        일반 타입(str, int, list, dict)은 기본 인코더 사용

        CustomJSONEncoder는 datetime 외의 타입은 기본 동작을 유지합니다.
        """
        # Arrange
        data = {
            "string": "hello",
            "number": 42,
            "list": [1, 2, 3],
            "nested": {"key": "value"},
        }

        # Act
        json_str = json.dumps(data, cls=CustomJSONEncoder)
        result = json.loads(json_str)

        # Assert
        assert result == data
