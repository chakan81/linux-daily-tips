"""
Tips API 검색 및 정렬 기능 테스트 (TDD)

GET /api/v1/tips 엔드포인트의 검색 및 정렬 기능을 검증합니다.
- 검색 기능 (q 파라미터): 제목, 내용에서 키워드 검색
- 정렬 기능 (sort_by, order 파라미터): 게시일, 제목 정렬

TDD 단계:
1. RED: 테스트 작성 (이 파일)
2. GREEN: 구현 (tip_query.py, tips.py)
3. REFACTOR: 코드 개선

현재 상태: RED (모든 테스트 FAIL 예상)
"""

from datetime import date, timedelta
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import CacheService
from app.core.dependencies import get_cache, get_tip_service
from app.main import app
from app.models.tip import DifficultyLevel, Tip
from app.services.tip import TipService


# ============================================================
# Fixtures
# ============================================================


@pytest_asyncio.fixture
async def cache_service() -> CacheService:
    """
    테스트용 Redis CacheService 인스턴스

    각 테스트마다 독립적인 캐시 서비스를 제공합니다.
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


@pytest_asyncio.fixture
async def test_client(
    async_db_session: AsyncSession,
    cache_service: CacheService,
) -> AsyncClient:
    """
    테스트용 AsyncClient (의존성 오버라이드 포함)

    실제 데이터베이스와 Redis를 사용하는 HTTP 클라이언트를 제공합니다.
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


@pytest_asyncio.fixture(autouse=True)
async def clean_tips_table(async_db_session: AsyncSession):
    """
    각 테스트 전후에 tips 테이블 정리

    API 엔드포인트가 db.commit()을 호출하여 데이터가 persist되므로,
    각 테스트 전에 tips 테이블을 정리합니다.
    """
    # 테스트 전 정리
    from sqlalchemy import delete
    await async_db_session.execute(delete(Tip))
    await async_db_session.commit()

    yield

    # 테스트 후 정리
    await async_db_session.execute(delete(Tip))
    await async_db_session.commit()


@pytest_asyncio.fixture
async def search_test_tips(async_db_session: AsyncSession) -> list[Tip]:
    """
    검색 및 정렬 테스트용 샘플 팁 7개 생성

    다양한 제목, 내용, 난이도, 게시일을 가진 팁을 생성합니다.

    Returns:
        list[Tip]: 7개의 샘플 팁 (게시일 역순 정렬)
    """
    today = date.today()

    tips = [
        # 1. 오늘 (초급) - ls
        Tip(
            title="ls 명령어로 파일 목록 보기",
            content="ls 명령어는 디렉토리 내의 파일과 폴더 목록을 표시합니다. 기본적으로 현재 디렉토리의 내용을 알파벳 순으로 보여줍니다.",
            difficulty=DifficultyLevel.BEGINNER,
            category=["file-system", "basics"],
            publish_date=today,
            is_active=True,
        ),
        # 2. 어제 (중급) - grep
        Tip(
            title="grep으로 파일 내용 검색하기",
            content="grep 명령어는 파일 내에서 특정 패턴을 검색할 때 사용합니다. 텍스트 처리에 매우 유용한 도구입니다.",
            difficulty=DifficultyLevel.INTERMEDIATE,
            category=["text-processing", "search"],
            publish_date=today - timedelta(days=1),
            is_active=True,
        ),
        # 3. 2일 전 (고급) - find
        Tip(
            title="find 명령어로 파일 찾기",
            content="find는 디렉토리 구조를 탐색하여 조건에 맞는 파일을 찾습니다. 강력한 검색 기능을 제공합니다.",
            difficulty=DifficultyLevel.ADVANCED,
            category=["file-system", "search"],
            publish_date=today - timedelta(days=2),
            is_active=True,
        ),
        # 4. 3일 전 (초급) - cd
        Tip(
            title="cd 명령어로 디렉토리 이동하기",
            content="cd는 현재 작업 디렉토리를 변경하는 가장 기본적인 명령어입니다. 리눅스 사용의 시작점입니다.",
            difficulty=DifficultyLevel.BEGINNER,
            category=["basics", "navigation"],
            publish_date=today - timedelta(days=3),
            is_active=True,
        ),
        # 5. 4일 전 (중급) - chmod
        Tip(
            title="chmod로 파일 권한 변경하기",
            content="chmod는 파일이나 디렉토리의 권한을 설정합니다. 보안 관리의 핵심 명령어입니다.",
            difficulty=DifficultyLevel.INTERMEDIATE,
            category=["file-system", "security"],
            publish_date=today - timedelta(days=4),
            is_active=True,
        ),
        # 6. 5일 전 (고급) - awk
        Tip(
            title="awk로 텍스트 처리 자동화하기",
            content="awk는 강력한 텍스트 처리 언어입니다. 복잡한 데이터 분석과 리포팅을 자동화할 수 있습니다.",
            difficulty=DifficultyLevel.ADVANCED,
            category=["text-processing", "scripting"],
            publish_date=today - timedelta(days=5),
            is_active=True,
        ),
        # 7. 6일 전 (초급) - pwd
        Tip(
            title="pwd로 현재 위치 확인하기",
            content="pwd는 현재 작업 중인 디렉토리의 전체 경로를 출력합니다. 위치 파악에 필수적인 명령어입니다.",
            difficulty=DifficultyLevel.BEGINNER,
            category=["basics"],
            publish_date=today - timedelta(days=6),
            is_active=True,
        ),
    ]

    for tip in tips:
        async_db_session.add(tip)

    await async_db_session.commit()

    # ID 생성을 위해 refresh
    for tip in tips:
        await async_db_session.refresh(tip)

    return tips


# ============================================================
# 1. 검색 테스트 (6개)
# ============================================================


@pytest.mark.asyncio
class TestTipsSearch:
    """팁 검색 기능 검증"""

    async def test_search_tips_by_title(
        self,
        test_client: AsyncClient,
        search_test_tips: list[Tip],
    ) -> None:
        """
        제목에서 키워드 검색

        Given: 제목에 "ls"를 포함한 팁이 존재
        When: GET /api/v1/tips?q=ls 호출
        Then: 제목에 "ls" 포함된 팁 반환
        """
        # Act
        response = await test_client.get("/api/v1/tips?q=ls")

        # Assert
        assert response.status_code == 200, "검색 요청이 성공해야 함"
        data = response.json()

        # 최소 1개 이상 반환 (ls 명령어 팁)
        assert data["total"] >= 1, "검색 결과가 최소 1개 이상이어야 함"

        # 모든 결과의 제목에 "ls" 포함 확인
        for item in data["items"]:
            title_lower = item["title"].lower()
            assert "ls" in title_lower, f"제목에 'ls'가 포함되어야 함: {item['title']}"

    async def test_search_tips_by_content(
        self,
        test_client: AsyncClient,
        search_test_tips: list[Tip],
    ) -> None:
        """
        내용에서 키워드 검색

        Given: 내용에 "디렉토리"를 포함한 팁이 존재
        When: GET /api/v1/tips?q=디렉토리 호출
        Then: content에 "디렉토리" 포함된 팁 반환
        """
        # Act
        response = await test_client.get("/api/v1/tips?q=디렉토리")

        # Assert
        assert response.status_code == 200, "검색 요청이 성공해야 함"
        data = response.json()

        # 최소 3개 이상 반환 (ls, cd, pwd 등)
        assert data["total"] >= 3, "검색 결과가 최소 3개 이상이어야 함"

        # 모든 결과의 제목 또는 내용에 "디렉토리" 포함 확인
        for item in data["items"]:
            title = item["title"]
            content = item["content"]
            has_keyword = "디렉토리" in title or "디렉토리" in content
            assert has_keyword, f"제목 또는 내용에 '디렉토리'가 포함되어야 함: {title}"

    async def test_search_tips_case_insensitive(
        self,
        test_client: AsyncClient,
        search_test_tips: list[Tip],
    ) -> None:
        """
        대소문자 구분 없이 검색

        Given: 제목에 소문자 "grep"을 포함한 팁이 존재
        When: GET /api/v1/tips?q=GREP (대문자) 호출
        Then: 대소문자 구분 없이 "grep" 포함된 팁 반환
        """
        # Act: 대문자로 검색
        response = await test_client.get("/api/v1/tips?q=GREP")

        # Assert
        assert response.status_code == 200, "검색 요청이 성공해야 함"
        data = response.json()

        # 최소 1개 반환 (grep 팁)
        assert data["total"] >= 1, "검색 결과가 최소 1개 이상이어야 함"

        # grep 팁이 포함되어 있는지 확인
        found_grep = False
        for item in data["items"]:
            if "grep" in item["title"].lower():
                found_grep = True
                break

        assert found_grep, "대소문자 구분 없이 'grep' 팁을 찾아야 함"

    async def test_search_tips_returns_empty_when_no_match(
        self,
        test_client: AsyncClient,
        search_test_tips: list[Tip],
    ) -> None:
        """
        일치하는 결과 없을 때 빈 배열 반환

        Given: 존재하지 않는 키워드
        When: GET /api/v1/tips?q=nonexistent_keyword_xyz123 호출
        Then: items=[], total=0 반환
        """
        # Act
        response = await test_client.get("/api/v1/tips?q=nonexistent_keyword_xyz123")

        # Assert
        assert response.status_code == 200, "검색 요청이 성공해야 함 (결과 없어도 200)"
        data = response.json()

        assert data["total"] == 0, "검색 결과가 0개여야 함"
        assert data["items"] == [], "items가 빈 배열이어야 함"

    async def test_search_tips_with_pagination(
        self,
        test_client: AsyncClient,
        search_test_tips: list[Tip],
    ) -> None:
        """
        검색 + 페이지네이션 조합

        Given: "파일"을 포함한 팁이 여러 개 존재
        When: GET /api/v1/tips?q=파일&skip=0&limit=2 호출
        Then: 최대 2개 반환, total은 전체 검색 결과 수
        """
        # Act
        response = await test_client.get("/api/v1/tips?q=파일&skip=0&limit=2")

        # Assert
        assert response.status_code == 200, "검색 요청이 성공해야 함"
        data = response.json()

        # total은 2개 이상, items는 최대 2개
        assert data["total"] >= 2, "전체 검색 결과가 2개 이상이어야 함"
        assert len(data["items"]) <= 2, "반환된 items는 최대 2개여야 함 (limit=2)"

        # 모든 결과에 "파일" 포함 확인
        for item in data["items"]:
            title = item["title"]
            content = item["content"]
            has_keyword = "파일" in title or "파일" in content
            assert has_keyword, f"제목 또는 내용에 '파일'이 포함되어야 함: {title}"

    async def test_search_tips_with_filters(
        self,
        test_client: AsyncClient,
        search_test_tips: list[Tip],
    ) -> None:
        """
        검색 + 난이도 필터 조합

        Given: "명령어"를 포함한 팁 중 초급 난이도 팁 존재
        When: GET /api/v1/tips?q=명령어&difficulty=beginner 호출
        Then: "명령어" 포함 + 초급 난이도만 반환
        """
        # Act
        response = await test_client.get("/api/v1/tips?q=명령어&difficulty=beginner")

        # Assert
        assert response.status_code == 200, "검색 요청이 성공해야 함"
        data = response.json()

        # 최소 1개 반환 (ls, cd, pwd 등 초급 팁)
        assert data["total"] >= 1, "검색 결과가 최소 1개 이상이어야 함"

        # 모든 결과가 beginner 난이도이고 "명령어" 포함 확인
        for item in data["items"]:
            assert item["difficulty"] == "beginner", f"난이도가 beginner여야 함: {item['difficulty']}"

            title = item["title"]
            content = item["content"]
            has_keyword = "명령어" in title or "명령어" in content
            assert has_keyword, f"제목 또는 내용에 '명령어'가 포함되어야 함: {title}"


# ============================================================
# 2. 정렬 테스트 (5개)
# ============================================================


@pytest.mark.asyncio
class TestTipsSort:
    """팁 정렬 기능 검증"""

    async def test_sort_by_publish_date_desc(
        self,
        test_client: AsyncClient,
        search_test_tips: list[Tip],
    ) -> None:
        """
        최신순 정렬 (기본값)

        Given: 다양한 게시일을 가진 팁들
        When: GET /api/v1/tips?sort_by=publish_date&order=desc 호출
        Then: publish_date 내림차순 (최신이 먼저)
        """
        # Act
        response = await test_client.get("/api/v1/tips?sort_by=publish_date&order=desc")

        # Assert
        assert response.status_code == 200, "정렬 요청이 성공해야 함"
        data = response.json()

        items = data["items"]
        assert len(items) >= 2, "정렬 검증을 위해 최소 2개 이상 필요"

        # 날짜가 내림차순인지 확인 (최신 → 과거)
        for i in range(len(items) - 1):
            current_date = items[i]["publishDate"]  # camelCase (Pydantic alias)
            next_date = items[i + 1]["publishDate"]
            assert current_date >= next_date, (
                f"날짜가 내림차순이어야 함: {current_date} >= {next_date}"
            )

    async def test_sort_by_publish_date_asc(
        self,
        test_client: AsyncClient,
        search_test_tips: list[Tip],
    ) -> None:
        """
        오래된순 정렬

        Given: 다양한 게시일을 가진 팁들
        When: GET /api/v1/tips?sort_by=publish_date&order=asc 호출
        Then: publish_date 오름차순 (과거가 먼저)
        """
        # Act
        response = await test_client.get("/api/v1/tips?sort_by=publish_date&order=asc")

        # Assert
        assert response.status_code == 200, "정렬 요청이 성공해야 함"
        data = response.json()

        items = data["items"]
        assert len(items) >= 2, "정렬 검증을 위해 최소 2개 이상 필요"

        # 날짜가 오름차순인지 확인 (과거 → 최신)
        for i in range(len(items) - 1):
            current_date = items[i]["publishDate"]  # camelCase (Pydantic alias)
            next_date = items[i + 1]["publishDate"]
            assert current_date <= next_date, (
                f"날짜가 오름차순이어야 함: {current_date} <= {next_date}"
            )

    async def test_sort_by_title_asc(
        self,
        test_client: AsyncClient,
        search_test_tips: list[Tip],
    ) -> None:
        """
        제목 A-Z 정렬

        Given: 다양한 제목을 가진 팁들
        When: GET /api/v1/tips?sort_by=title&order=asc 호출
        Then: title 오름차순 (가나다 순, 알파벳 순)
        """
        # Act
        response = await test_client.get("/api/v1/tips?sort_by=title&order=asc")

        # Assert
        assert response.status_code == 200, "정렬 요청이 성공해야 함"
        data = response.json()

        items = data["items"]
        assert len(items) >= 2, "정렬 검증을 위해 최소 2개 이상 필요"

        # 제목이 오름차순인지 확인 (가나다/알파벳 순)
        for i in range(len(items) - 1):
            current_title = items[i]["title"]
            next_title = items[i + 1]["title"]
            assert current_title <= next_title, (
                f"제목이 오름차순이어야 함: {current_title} <= {next_title}"
            )

    async def test_sort_by_title_desc(
        self,
        test_client: AsyncClient,
        search_test_tips: list[Tip],
    ) -> None:
        """
        제목 Z-A 정렬

        Given: 다양한 제목을 가진 팁들
        When: GET /api/v1/tips?sort_by=title&order=desc 호출
        Then: title 내림차순 (역순)
        """
        # Act
        response = await test_client.get("/api/v1/tips?sort_by=title&order=desc")

        # Assert
        assert response.status_code == 200, "정렬 요청이 성공해야 함"
        data = response.json()

        items = data["items"]
        assert len(items) >= 2, "정렬 검증을 위해 최소 2개 이상 필요"

        # 제목이 내림차순인지 확인 (역순)
        for i in range(len(items) - 1):
            current_title = items[i]["title"]
            next_title = items[i + 1]["title"]
            assert current_title >= next_title, (
                f"제목이 내림차순이어야 함: {current_title} >= {next_title}"
            )

    async def test_sort_invalid_field_returns_default(
        self,
        test_client: AsyncClient,
        search_test_tips: list[Tip],
    ) -> None:
        """
        잘못된 정렬 필드 (보안 테스트)

        Given: 유효하지 않은 정렬 필드
        When: GET /api/v1/tips?sort_by=invalid_field&order=asc 호출
        Then: 에러 없이 기본 정렬(publish_date desc) 적용
        """
        # Act
        response = await test_client.get("/api/v1/tips?sort_by=invalid_field&order=asc")

        # Assert: 에러가 아닌 200 반환 (graceful fallback)
        assert response.status_code == 200, "잘못된 정렬 필드에도 200 반환해야 함"
        data = response.json()

        items = data["items"]
        assert len(items) >= 2, "정렬 검증을 위해 최소 2개 이상 필요"

        # 기본 정렬(publish_date desc)이 적용되었는지 확인
        for i in range(len(items) - 1):
            current_date = items[i]["publishDate"]  # camelCase (Pydantic alias)
            next_date = items[i + 1]["publishDate"]
            # 기본 정렬은 내림차순
            assert current_date >= next_date, (
                f"기본 정렬(날짜 내림차순)이 적용되어야 함: {current_date} >= {next_date}"
            )
