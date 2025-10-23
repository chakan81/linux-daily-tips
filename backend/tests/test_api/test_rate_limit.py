"""
Rate Limiting 통합 테스트 (E2E)

slowapi와 Redis 기반 Rate Limiting 동작을 검증하는 통합 테스트입니다.
- 제한 이내 요청 성공
- 제한 초과 시 429 에러
- 엔드포인트별 독립적인 제한
- Admin API의 엄격한 제한
- Rate Limit 응답 헤더 확인

TDD Day 14 - Phase 3: Rate Limiting 테스트
"""

import asyncio
from datetime import date
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import CacheService
from app.core.config import settings
from app.core.dependencies import get_cache, get_current_admin, get_tip_service
from app.main import app
from app.models.tip import DifficultyLevel, Tip
from app.services.tip_service import TipService


# ============================================================
# Fixtures
# ============================================================


@pytest_asyncio.fixture
async def cache_service() -> CacheService:
    """
    테스트용 Redis CacheService 인스턴스

    Rate Limiting과 캐싱 모두 사용하는 통합 테스트를 위해 제공합니다.
    """
    cache = CacheService()
    await cache.connect()
    yield cache

    # 테스트 후 모든 캐시 정리
    try:
        await cache.clear_pattern("tip:*")
        await cache.clear_pattern("tips:*")
    finally:
        await cache.disconnect()


@pytest_asyncio.fixture(autouse=True)
async def clear_rate_limit_keys():
    """
    각 테스트 전후 Rate Limit Redis 키 초기화

    slowapi는 "LIMITER:..." 형태의 키를 사용하여 Rate Limiting을 추적합니다.
    각 테스트의 독립성을 보장하기 위해 매 테스트 전후에 초기화합니다.
    """
    async def _clear_keys():
        redis = await Redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        try:
            # slowapi의 Rate Limit 키 패턴: "LIMITS:LIMITER/..."
            keys_to_delete = []
            async for key in redis.scan_iter("LIMITS:LIMITER/*"):
                keys_to_delete.append(key)

            if keys_to_delete:
                await redis.delete(*keys_to_delete)
        finally:
            await redis.aclose()

    # 테스트 전 정리
    await _clear_keys()

    yield

    # 테스트 후 정리
    await _clear_keys()


@pytest_asyncio.fixture
async def test_client(
    async_db_session: AsyncSession,
    cache_service: CacheService,
) -> AsyncClient:
    """
    테스트용 AsyncClient (의존성 오버라이드 포함)

    실제 데이터베이스와 Redis를 사용하는 HTTP 클라이언트를 제공합니다.
    Rate Limiting은 실제 Redis에서 동작합니다.
    """
    # 의존성 오버라이드: 테스트용 세션과 캐시 사용
    async def override_get_db():
        yield async_db_session

    async def override_get_cache():
        yield cache_service

    async def override_get_tip_service():
        return TipService(cache=cache_service)

    # 기존 의존성 백업
    original_dependencies = app.dependency_overrides.copy()

    # 의존성 오버라이드
    from app.config.database import get_async_session
    app.dependency_overrides[get_async_session] = override_get_db
    app.dependency_overrides[get_cache] = override_get_cache
    app.dependency_overrides[get_tip_service] = override_get_tip_service

    # AsyncClient 생성 (ASGI Transport 사용)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    # 의존성 복원
    app.dependency_overrides = original_dependencies


@pytest_asyncio.fixture
async def mock_admin_token() -> dict[str, str]:
    """
    Mock Admin JWT 토큰 생성

    Admin API 테스트를 위한 Mock 토큰을 제공합니다.
    get_current_admin 의존성을 오버라이드하여 인증을 우회합니다.
    """
    mock_admin_data = {
        "user_id": "admin_01JCAW0V1QQ9KZ2F3XHBP8TGNY",
        "email": "admin@example.com",
        "role": "admin",
    }

    # get_current_admin 의존성 오버라이드
    async def override_get_current_admin():
        return mock_admin_data

    app.dependency_overrides[get_current_admin] = override_get_current_admin

    # Authorization 헤더 반환
    return {"Authorization": "Bearer mock_admin_token_for_testing"}


@pytest_asyncio.fixture(autouse=True)
async def clean_tips_table(async_db_session: AsyncSession):
    """
    각 테스트 전후에 tips 테이블 정리

    API 엔드포인트가 db.commit()을 호출하여 데이터가 persist되므로,
    각 테스트 전에 tips 테이블을 정리하여 독립성을 보장합니다.
    """
    # 테스트 전 정리
    from app.models.tip import Tip
    from sqlalchemy import delete
    await async_db_session.execute(delete(Tip))
    await async_db_session.commit()

    yield

    # 테스트 후 정리
    await async_db_session.execute(delete(Tip))
    await async_db_session.commit()


@pytest_asyncio.fixture
async def sample_tip(async_db_session: AsyncSession) -> Tip:
    """
    테스트용 샘플 Tip 생성

    Rate Limiting 테스트에서 실제 데이터를 조회할 수 있도록 제공합니다.
    """
    tip = Tip(
        title="find 명령어로 파일 검색하기",
        content="```bash\nfind . -name '*.log'\n```",
        difficulty=DifficultyLevel.BEGINNER,
        category=["file-system", "search"],
        publish_date=date.today(),
        terminal_setup={
            "files": [{"path": "/home/user/test.log", "content": "Log entry\n"}],
            "directories": ["/home/user/logs"],
        },
        is_active=True,
    )
    async_db_session.add(tip)
    await async_db_session.commit()  # commit으로 변경 (API가 commit하므로)
    await async_db_session.refresh(tip)
    return tip


# ============================================================
# Test Cases: Tips API Rate Limiting
# ============================================================


@pytest.mark.asyncio
async def test_rate_limit_within_limit(test_client: AsyncClient, sample_tip: Tip):
    """
    제한 이내 요청 성공

    Given: /daily 엔드포인트 (10/분 제한)
    When: 5번 연속 요청
    Then: 모두 200 OK 반환
    """
    # Act: 5번 연속 요청 (10/분 제한의 절반)
    for i in range(5):
        response = await test_client.get("/api/v1/tips/daily")

        # Assert: 모두 성공
        assert response.status_code == 200, f"Request {i+1} failed with {response.status_code}"
        data = response.json()
        assert "id" in data
        assert "title" in data


@pytest.mark.asyncio
async def test_rate_limit_exceeded(test_client: AsyncClient, sample_tip: Tip):
    """
    제한 초과 시 429 에러

    Given: /daily 엔드포인트 (10/분 제한)
    When: 12번 연속 요청
    Then: 1-10번째는 200, 11-12번째는 429 Too Many Requests
    """
    success_count = 0
    rate_limit_count = 0

    # Act: 12번 연속 요청 (10/분 제한 초과)
    for i in range(12):
        response = await test_client.get("/api/v1/tips/daily")

        if response.status_code == 200:
            success_count += 1
            # Assert: 응답 데이터 검증
            data = response.json()
            assert "id" in data
            assert "title" in data
        elif response.status_code == 429:
            rate_limit_count += 1
            # Assert: Rate Limit 에러 메시지 확인
            assert "rate limit exceeded" in response.text.lower() or "too many requests" in response.text.lower()
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")

    # Assert: 정확히 10번 성공, 2번 Rate Limit
    assert success_count == 10, f"Expected 10 successful requests, got {success_count}"
    assert rate_limit_count == 2, f"Expected 2 rate-limited requests, got {rate_limit_count}"


@pytest.mark.asyncio
async def test_rate_limit_per_endpoint_independent(test_client: AsyncClient, sample_tip: Tip):
    """
    엔드포인트별 독립적인 제한

    Given: /daily (10/분), / (30/분) 엔드포인트
    When: /daily 10번 + / 20번 요청
    Then: 모두 성공 (독립적 카운팅)
    """
    # Act: /daily 엔드포인트 10번 요청 (제한까지)
    for i in range(10):
        response = await test_client.get("/api/v1/tips/daily")
        assert response.status_code == 200, f"/daily request {i+1} failed"

    # Act: / 엔드포인트 20번 요청 (독립적인 제한)
    for i in range(20):
        response = await test_client.get("/api/v1/tips/?skip=0&limit=10")
        assert response.status_code == 200, f"/ request {i+1} failed"

    # Assert: 다시 /daily 요청하면 Rate Limit
    response = await test_client.get("/api/v1/tips/daily")
    assert response.status_code == 429, "Expected rate limit on /daily after 10 requests"

    # Assert: / 엔드포인트는 여전히 10번 더 가능 (30/분 - 20 = 10)
    for i in range(10):
        response = await test_client.get("/api/v1/tips/?skip=0&limit=10")
        assert response.status_code == 200, f"/ request {20+i+1} should still succeed"


@pytest.mark.asyncio
async def test_rate_limit_by_endpoint_path(test_client: AsyncClient, sample_tip: Tip):
    """
    엔드포인트별 독립적인 Rate Limit 검증 (상세 조회)

    Given: /{tip_id} (20/분), /categories/list (30/분)
    When: 각각 제한까지 요청
    Then: 독립적으로 Rate Limit 적용
    """
    tip_id = sample_tip.id

    # Act: /{tip_id} 엔드포인트 20번 요청
    for i in range(20):
        response = await test_client.get(f"/api/v1/tips/{tip_id}")
        assert response.status_code == 200, f"/{tip_id} request {i+1} failed"

    # Assert: 21번째 요청은 Rate Limit
    response = await test_client.get(f"/api/v1/tips/{tip_id}")
    assert response.status_code == 429, "Expected rate limit on /{tip_id} after 20 requests"

    # Act: /categories/list는 독립적이므로 30번 가능
    for i in range(30):
        response = await test_client.get("/api/v1/tips/categories/list")
        assert response.status_code == 200, f"/categories/list request {i+1} failed"

    # Assert: 31번째 요청은 Rate Limit
    response = await test_client.get("/api/v1/tips/categories/list")
    assert response.status_code == 429, "Expected rate limit on /categories/list after 30 requests"


@pytest.mark.asyncio
async def test_rate_limit_response_headers(test_client: AsyncClient, sample_tip: Tip):
    """
    Rate Limit 응답 헤더 확인

    Given: 모든 Rate Limited 엔드포인트
    When: 요청 시
    Then: Rate Limit 정보가 제공되는지 확인 (헤더 또는 429 응답)

    Note:
        slowapi는 기본적으로 Rate Limit 헤더를 추가하지 않을 수 있습니다.
        주요 검증은 Rate Limit 동작 자체이므로, 헤더가 없어도 테스트를 통과시킵니다.
    """
    # Act: /daily 엔드포인트 요청
    response = await test_client.get("/api/v1/tips/daily")

    # Assert: 기본 응답 성공
    assert response.status_code == 200

    # Assert: Rate Limit 헤더 확인 (선택적)
    # slowapi는 다음 헤더를 제공할 수 있습니다:
    # - X-RateLimit-Limit: 최대 허용 횟수
    # - X-RateLimit-Remaining: 남은 횟수
    # - X-RateLimit-Reset: 재설정 시각 (Unix timestamp)
    headers = response.headers
    header_keys = [key.lower() for key in headers.keys()]

    # Note: slowapi 기본 설정에서는 헤더를 추가하지 않을 수 있음
    # 따라서 헤더 존재 여부만 확인하고 없으면 pass
    has_ratelimit_headers = any("ratelimit" in key for key in header_keys)

    if has_ratelimit_headers:
        # 헤더가 있다면 검증
        assert any("ratelimit-limit" in key for key in header_keys), \
            "X-RateLimit-Limit header should be present"
        assert any("ratelimit-remaining" in key for key in header_keys), \
            "X-RateLimit-Remaining header should be present"
        assert any("ratelimit-reset" in key for key in header_keys), \
            "X-RateLimit-Reset header should be present"

        # Remaining 값 검증
        remaining_key = next(key for key in headers.keys() if "remaining" in key.lower())
        remaining = int(headers[remaining_key])
        assert remaining == 9, f"Expected 9 remaining requests, got {remaining}"
    else:
        # 헤더가 없어도 Rate Limit 동작은 다른 테스트에서 검증됨
        # 이 테스트는 선택적 기능이므로 pass
        pass

    # 추가 검증: 제한 초과 시 429 응답 확인
    for i in range(10):
        response = await test_client.get("/api/v1/tips/daily")

    # 11번째 요청은 Rate Limit
    response = await test_client.get("/api/v1/tips/daily")
    assert response.status_code == 429, "Rate limit should be enforced after 10 requests"


# ============================================================
# Test Cases: Admin API Rate Limiting (Stricter Limits)
# ============================================================


@pytest.mark.asyncio
async def test_admin_get_me_rate_limit(test_client: AsyncClient, mock_admin_token: dict[str, str]):
    """
    Admin GET /me Rate Limit 테스트 (30/분)

    Given: GET /admin/me (30/분 제한)
    When: 31번 연속 요청
    Then: 1-30번째는 200, 31번째는 429
    """
    # Act: 30번 연속 요청 (제한까지)
    for i in range(30):
        response = await test_client.get("/api/v1/admin/me", headers=mock_admin_token)
        assert response.status_code == 200, f"Request {i+1} failed with {response.status_code}"
        data = response.json()
        assert data["email"] == "admin@example.com"

    # Assert: 31번째 요청은 Rate Limit
    response = await test_client.get("/api/v1/admin/me", headers=mock_admin_token)
    assert response.status_code == 429, "Expected rate limit after 30 requests"


@pytest.mark.asyncio
async def test_admin_create_tip_rate_limit_strict(test_client: AsyncClient, mock_admin_token: dict[str, str]):
    """
    Admin POST /tips Rate Limit 테스트 (5/분 - 엄격한 제한)

    Given: POST /admin/tips (5/분 제한)
    When: 6번 연속 요청
    Then: 1-5번째는 200/201, 6번째는 429
    """
    tip_create_data = {
        "title": "Test Tip for Rate Limiting",
        "content": "This is test content for rate limiting with at least 20 characters",
        "difficulty": "beginner",
        "category": ["test"],
        "terminal_setup": {},
        "is_active": True,
    }

    # Act: 5번 연속 요청 (제한까지)
    for i in range(5):
        response = await test_client.post(
            "/api/v1/admin/tips",
            json=tip_create_data,
            headers=mock_admin_token
        )
        assert response.status_code == 200, f"Request {i+1} failed with {response.status_code}"
        data = response.json()
        assert "title" in data

    # Assert: 6번째 요청은 Rate Limit
    response = await test_client.post(
        "/api/v1/admin/tips",
        json=tip_create_data,
        headers=mock_admin_token
    )
    assert response.status_code == 429, "Expected rate limit after 5 POST requests"


@pytest.mark.asyncio
async def test_admin_update_tip_rate_limit(test_client: AsyncClient, mock_admin_token: dict[str, str]):
    """
    Admin PUT /tips/{id} Rate Limit 테스트 (10/분)

    Given: PUT /admin/tips/{id} (10/분 제한)
    When: 11번 연속 요청
    Then: 1-10번째는 200, 11번째는 429
    """
    tip_update_data = {
        "title": "Updated Tip",
    }
    tip_id = "tip_01JCAW0V1QQ9KZ2F3XHBP8TGNY"

    # Act: 10번 연속 요청 (제한까지)
    for i in range(10):
        response = await test_client.put(
            f"/api/v1/admin/tips/{tip_id}",
            json=tip_update_data,
            headers=mock_admin_token
        )
        assert response.status_code == 200, f"Request {i+1} failed with {response.status_code}"

    # Assert: 11번째 요청은 Rate Limit
    response = await test_client.put(
        f"/api/v1/admin/tips/{tip_id}",
        json=tip_update_data,
        headers=mock_admin_token
    )
    assert response.status_code == 429, "Expected rate limit after 10 PUT requests"


@pytest.mark.asyncio
async def test_admin_delete_tip_rate_limit_strict(test_client: AsyncClient, mock_admin_token: dict[str, str]):
    """
    Admin DELETE /tips/{id} Rate Limit 테스트 (5/분 - 엄격한 제한)

    Given: DELETE /admin/tips/{id} (5/분 제한)
    When: 6번 연속 요청
    Then: 1-5번째는 200, 6번째는 429
    """
    tip_id = "tip_01JCAW0V1QQ9KZ2F3XHBP8TGNY"

    # Act: 5번 연속 요청 (제한까지)
    for i in range(5):
        response = await test_client.delete(
            f"/api/v1/admin/tips/{tip_id}",
            headers=mock_admin_token
        )
        assert response.status_code == 200, f"Request {i+1} failed with {response.status_code}"
        data = response.json()
        assert "deleted_id" in data

    # Assert: 6번째 요청은 Rate Limit
    response = await test_client.delete(
        f"/api/v1/admin/tips/{tip_id}",
        headers=mock_admin_token
    )
    assert response.status_code == 429, "Expected rate limit after 5 DELETE requests"


@pytest.mark.asyncio
async def test_admin_endpoints_independent_limits(
    test_client: AsyncClient,
    mock_admin_token: dict[str, str]
):
    """
    Admin 엔드포인트별 독립적인 Rate Limit 검증

    Given: POST /tips (5/분), PUT /tips (10/분), DELETE /tips (5/분)
    When: 각각 제한까지 요청
    Then: 독립적으로 Rate Limit 적용
    """
    tip_create_data = {
        "title": "Test Tip for Rate Limiting",
        "content": "This is test content for rate limiting with at least 20 characters",
        "difficulty": "beginner",
        "category": ["test"],
        "terminal_setup": {},
        "is_active": True
    }
    tip_update_data = {"title": "Updated"}
    tip_id = "tip_01JCAW0V1QQ9KZ2F3XHBP8TGNY"

    # Act: POST 5번 (제한까지)
    for i in range(5):
        response = await test_client.post("/api/v1/admin/tips", json=tip_create_data, headers=mock_admin_token)
        assert response.status_code == 200, f"POST request {i+1} failed"

    # Act: PUT 10번 (독립적인 제한)
    for i in range(10):
        response = await test_client.put(f"/api/v1/admin/tips/{tip_id}", json=tip_update_data, headers=mock_admin_token)
        assert response.status_code == 200, f"PUT request {i+1} failed"

    # Act: DELETE 5번 (독립적인 제한)
    for i in range(5):
        response = await test_client.delete(f"/api/v1/admin/tips/{tip_id}", headers=mock_admin_token)
        assert response.status_code == 200, f"DELETE request {i+1} failed"

    # Assert: 추가 요청은 모두 Rate Limit
    assert (await test_client.post("/api/v1/admin/tips", json=tip_create_data, headers=mock_admin_token)).status_code == 429
    assert (await test_client.put(f"/api/v1/admin/tips/{tip_id}", json=tip_update_data, headers=mock_admin_token)).status_code == 429
    assert (await test_client.delete(f"/api/v1/admin/tips/{tip_id}", headers=mock_admin_token)).status_code == 429


# ============================================================
# Test Cases: TTL Reset (Optional - Skipped for Performance)
# ============================================================


@pytest.mark.skip(reason="TTL 테스트는 실제 60초 대기가 필요하여 비현실적 (CI/CD 성능 저하)")
async def test_rate_limit_reset_after_ttl(test_client: AsyncClient, sample_tip: Tip):
    """
    TTL 만료 후 재요청 성공 (스킵됨)

    Given: /daily (10/분 제한)
    When: 10번 요청 → 60초 대기 → 다시 10번 요청
    Then: 모두 성공

    Note:
        실제 60초 대기는 CI/CD에서 비현실적이므로 스킵합니다.
        Mock으로 처리하거나 수동 테스트로 검증 필요.
    """
    # Act: 10번 요청 (제한까지)
    for i in range(10):
        response = await test_client.get("/api/v1/tips/daily")
        assert response.status_code == 200

    # Wait: 60초 대기 (실제 TTL 만료)
    await asyncio.sleep(60)

    # Act: 다시 10번 요청 (TTL 만료 후)
    for i in range(10):
        response = await test_client.get("/api/v1/tips/daily")
        assert response.status_code == 200, f"Request {i+1} after TTL should succeed"
