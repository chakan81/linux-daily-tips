"""
Health Check API 테스트

서버 상태 및 의존성(DB, Redis) 헬스 체크 API를 테스트합니다.
"""

from typing import Any

import pytest
import pytest_asyncio
from httpx import AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession


# ============================================================
# Fixtures
# ============================================================


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    """
    테스트용 AsyncClient (FastAPI 앱 연결)

    Health Check API 테스트를 위한 HTTP 클라이언트를 제공합니다.

    Yields:
        AsyncClient: FastAPI 앱에 연결된 테스트 클라이언트
    """
    from httpx import ASGITransport

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def redis_client_test() -> Redis:
    """
    테스트용 Redis 클라이언트

    Health Check 테스트에서 Redis 상태를 확인하기 위해 사용합니다.

    Yields:
        Redis: 테스트용 Redis 클라이언트 인스턴스
    """
    from app.core.config import settings

    client = Redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )

    try:
        yield client
    finally:
        await client.aclose()


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    """
    테스트용 데이터베이스 세션

    Health Check 테스트에서 DB 상태를 확인하기 위해 사용합니다.

    Yields:
        AsyncSession: 테스트용 DB 세션
    """
    from app.config.database import get_async_session

    async for session in get_async_session():
        yield session


# ============================================================
# Tests
# ============================================================


@pytest.mark.asyncio
@pytest.mark.integration
class TestHealthCheck:
    """기본 헬스 체크 테스트"""

    async def test_basic_health_check(self, client: AsyncClient) -> None:
        """
        기본 헬스 체크

        Given: 서버가 실행 중
        When: GET /api/v1/health
        Then: 200 OK, status: healthy
        """
        # Act
        response = await client.get("/api/v1/health")

        # Assert
        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert data["status"] == "healthy"
        assert "version" in data
        assert "environment" in data

    async def test_health_check_returns_version(self, client: AsyncClient) -> None:
        """
        버전 정보 확인

        Given: 서버가 실행 중
        When: GET /api/v1/health
        Then: version 필드가 있어야 함
        """
        # Act
        response = await client.get("/api/v1/health")

        # Assert
        assert response.status_code == 200
        data = response.json()

        assert "version" in data
        assert isinstance(data["version"], str)
        assert len(data["version"]) > 0

    async def test_health_check_returns_environment(
        self, client: AsyncClient
    ) -> None:
        """
        환경 정보 확인

        Given: 서버가 실행 중
        When: GET /api/v1/health
        Then: environment 필드가 있어야 함
        """
        # Act
        response = await client.get("/api/v1/health")

        # Assert
        assert response.status_code == 200
        data = response.json()

        assert "environment" in data
        assert isinstance(data["environment"], str)
        # development, staging, production 중 하나
        assert data["environment"] in ["development", "staging", "production"]

    async def test_health_check_no_authentication_required(
        self, client: AsyncClient
    ) -> None:
        """
        인증 불필요 확인

        Given: 인증 토큰 없음
        When: GET /api/v1/health
        Then: 200 OK (인증 없이 접근 가능)
        """
        # Act
        response = await client.get("/api/v1/health")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
@pytest.mark.integration
class TestDetailedHealthCheck:
    """상세 헬스 체크 테스트 (DB + Redis)"""

    @pytest.mark.xfail(
        reason="Test isolation issue: passes when run individually, fails in full suite due to asyncio event loop conflict",
        strict=False,
    )
    async def test_detailed_health_check_all_services_healthy(
        self, client: AsyncClient
    ) -> None:
        """
        모든 서비스 정상 시나리오

        Given: PostgreSQL 및 Redis가 정상 동작 중
        When: GET /api/v1/health/detailed
        Then: 200 OK, status: healthy, 모든 서비스 connected
        """
        # Act
        response = await client.get("/api/v1/health/detailed")

        # Assert
        assert response.status_code == 200
        data = response.json()

        # 전체 상태
        assert data["status"] == "healthy"
        assert "version" in data
        assert "environment" in data

        # 서비스별 상태
        assert "services" in data
        services = data["services"]

        # PostgreSQL
        assert "database" in services
        assert services["database"]["status"] == "connected"
        assert "message" in services["database"]

        # Redis
        assert "redis" in services
        assert services["redis"]["status"] == "connected"
        assert "message" in services["redis"]


    async def test_detailed_health_check_redis_connected(
        self, client: AsyncClient, redis_client_test: Redis
    ) -> None:
        """
        Redis 연결 확인

        Given: Redis가 정상 동작 중
        When: GET /api/v1/health/detailed
        Then: redis.status == "connected"
        """
        # Act
        response = await client.get("/api/v1/health/detailed")

        # Assert
        assert response.status_code == 200
        data = response.json()

        redis = data["services"]["redis"]
        assert redis["status"] == "connected"
        assert "Redis" in redis["message"]

    async def test_detailed_health_check_redis_cache_operations(
        self, client: AsyncClient, redis_client_test: Redis
    ) -> None:
        """
        Redis 캐시 동작 검증

        Given: Redis가 정상 동작 중
        When: GET /api/v1/health/detailed (내부적으로 캐시 쓰기/읽기/삭제)
        Then: 정상 동작, health check test key는 자동 삭제됨
        """
        # Arrange: health check test key가 없는지 확인
        test_key = "health:check:test"
        await redis_client_test.delete(test_key)

        # Act: Health check 실행 (내부적으로 test key 생성/삭제)
        response = await client.get("/api/v1/health/detailed")

        # Assert: Health check 성공
        assert response.status_code == 200
        data = response.json()
        assert data["services"]["redis"]["status"] == "connected"

        # Verify: Test key가 자동으로 삭제되었는지 확인
        exists = await redis_client_test.exists(test_key)
        assert exists == 0, "Health check test key는 자동으로 삭제되어야 함"

    async def test_detailed_health_check_no_authentication_required(
        self, client: AsyncClient
    ) -> None:
        """
        상세 헬스 체크도 인증 불필요

        Given: 인증 토큰 없음
        When: GET /api/v1/health/detailed
        Then: 200 OK (인증 없이 접근 가능)
        """
        # Act
        response = await client.get("/api/v1/health/detailed")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "services" in data


@pytest.mark.asyncio
@pytest.mark.integration
class TestHealthCheckFailureScenarios:
    """헬스 체크 실패 시나리오 테스트"""

    async def test_detailed_health_check_response_structure(
        self, client: AsyncClient
    ) -> None:
        """
        응답 구조 검증

        Given: 서버가 실행 중
        When: GET /api/v1/health/detailed
        Then: 정확한 응답 구조 반환
        """
        # Act
        response = await client.get("/api/v1/health/detailed")

        # Assert
        assert response.status_code == 200
        data = response.json()

        # 최상위 필드
        required_fields = ["status", "version", "environment", "services"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

        # services 구조
        assert isinstance(data["services"], dict)
        assert "database" in data["services"]
        assert "redis" in data["services"]

        # 각 서비스 구조
        for service_name, service_data in data["services"].items():
            assert "status" in service_data, f"{service_name} missing 'status'"
            assert "message" in service_data, f"{service_name} missing 'message'"
            assert isinstance(service_data["status"], str)
            assert isinstance(service_data["message"], str)

    async def test_health_check_consistent_response(
        self, client: AsyncClient
    ) -> None:
        """
        헬스 체크 응답 일관성 테스트

        Given: 서버가 실행 중
        When: 헬스 체크를 여러 번 호출
        Then: 항상 동일한 구조로 응답
        """
        # Act: 3번 호출
        responses = []
        for _ in range(3):
            response = await client.get("/api/v1/health")
            responses.append(response.json())

        # Assert: 모든 응답이 동일한 필드를 가짐
        for data in responses:
            assert "status" in data
            assert "version" in data
            assert "environment" in data
            assert data["status"] == "healthy"

        # 버전과 환경은 동일해야 함
        versions = [r["version"] for r in responses]
        assert len(set(versions)) == 1, "버전이 일관되어야 함"

        environments = [r["environment"] for r in responses]
        assert len(set(environments)) == 1, "환경이 일관되어야 함"
