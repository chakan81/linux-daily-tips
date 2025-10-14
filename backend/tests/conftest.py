"""
pytest 테스트 설정 및 공통 fixture

테스트 데이터베이스 설정, 세션 관리, 샘플 데이터 생성 등
모든 테스트에서 공통으로 사용하는 fixture를 정의합니다.
"""

import asyncio
from collections.abc import AsyncGenerator, Generator
from datetime import date, datetime, timezone
from ipaddress import IPv4Address
from typing import Any

import pytest
import pytest_asyncio
from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.db.base import Base
from app.models.analytics import AnalyticsEvent
from app.models.draft import DraftStatus, DraftTip, DraftWeek
from app.models.terminal import TerminalSession, TerminalStatus
from app.models.tip import DifficultyLevel, Tip
from app.models.user import AdminUser

# 테스트용 데이터베이스 URL (동일 DB 사용하지만 트랜잭션 rollback으로 격리)
TEST_DATABASE_URL = settings.DATABASE_URL


# ============================================================
# Pytest 설정
# ============================================================


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """
    세션 스코프의 이벤트 루프 생성

    pytest-asyncio가 async fixture들을 올바르게 실행할 수 있도록
    세션 레벨 이벤트 루프를 제공합니다.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================
# 데이터베이스 Fixtures
# ============================================================


@pytest_asyncio.fixture(scope="session")
async def async_db_engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    테스트용 비동기 데이터베이스 엔진 생성 (세션 스코프)

    모든 테스트에서 공유되는 엔진을 생성하고, 테스트 시작 전에
    모든 테이블을 생성하고, 테스트 종료 후 정리합니다.
    """
    # NullPool 사용하여 각 테스트의 독립성 보장
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,  # 테스트 로그를 깔끔하게 유지
        poolclass=NullPool,  # 연결 풀 비활성화 (테스트 격리)
        connect_args={
            "server_settings": {
                "search_path": "linux_tips,public",
            }
        },
    )

    # 테스트 전 기존 스키마 삭제 및 재생성 (스키마 변경 및 VIEW 포함 모두 반영)
    async with engine.begin() as conn:
        # linux_tips 스키마를 CASCADE로 삭제 (VIEW 포함 모든 객체 삭제)
        await conn.execute(
            text("DROP SCHEMA IF EXISTS linux_tips CASCADE")
        )
        # linux_tips 스키마 재생성
        await conn.execute(
            text("CREATE SCHEMA linux_tips")
        )
        # 테이블 생성
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # 테스트 종료 후 정리는 필요시 활성화
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def async_db_session(
    async_db_engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """
    테스트용 비동기 데이터베이스 세션 (함수 스코프)

    각 테스트마다 새로운 트랜잭션을 시작하고, 테스트 종료 후
    자동으로 rollback하여 테스트 간 데이터 격리를 보장합니다.
    """
    # 세션 팩토리 생성
    async_session_factory = async_sessionmaker(
        bind=async_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    # 트랜잭션 시작 (AsyncSession은 자동으로 트랜잭션 시작)
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            # 테스트 종료 후 무조건 rollback
            await session.rollback()


# ============================================================
# 샘플 데이터 Fixtures
# ============================================================


@pytest.fixture
def sample_tip_data() -> dict[str, Any]:
    """
    샘플 Tip 데이터 딕셔너리

    Tip 모델 테스트에서 사용할 기본 데이터를 제공합니다.
    """
    return {
        "title": "파일 검색 마스터하기",
        "content": """
# find 명령어로 파일 검색하기

## 기본 사용법
```bash
find . -name "*.log"
```

최근 7일 이내에 수정된 로그 파일을 찾습니다:
```bash
find . -name "*.log" -mtime -7
```
        """.strip(),
        "difficulty": DifficultyLevel.BEGINNER,
        "category": ["file-system", "search"],
        "publish_date": date.today(),
        "terminal_setup": {
            "files": [
                {"path": "/home/user/test.log", "content": "Log entry 1\n"},
                {"path": "/home/user/error.log", "content": "Error log\n"},
            ],
            "directories": ["/home/user/logs"],
        },
        "is_active": True,
    }


@pytest.fixture
def sample_admin_user_data() -> dict[str, Any]:
    """
    샘플 AdminUser 데이터 딕셔너리

    AdminUser 모델 테스트에서 사용할 기본 데이터를 제공합니다.
    """
    return {
        "username": "testadmin",
        "email": "test@example.com",
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY3jKQOQM8a",  # "password123"
        "is_active": True,
        "is_superuser": False,
    }


@pytest.fixture
def sample_draft_week_data() -> dict[str, Any]:
    """
    샘플 DraftWeek 데이터 딕셔너리
    """
    return {
        "week_start_date": date(2024, 1, 1),  # 월요일
        "status": DraftStatus.DRAFT,
        "generated_by": "gpt-4",
    }


@pytest.fixture
def sample_draft_tip_data() -> dict[str, Any]:
    """
    샘플 DraftTip 데이터 딕셔너리
    """
    return {
        "day_of_week": 1,  # 월요일
        "title": "파일 권한 확인하기",
        "content": "```bash\nls -l file.txt\n```",
        "difficulty": "beginner",
        "category": ["file-system", "permissions"],
        "terminal_setup": {
            "files": [{"path": "/home/user/file.txt", "content": "test"}]
        },
        "llm_confidence_score": 0.95,
    }


@pytest.fixture
def sample_terminal_session_data() -> dict[str, Any]:
    """
    샘플 TerminalSession 데이터 딕셔너리
    """
    return {
        "container_id": "abc123def456",
        "status": TerminalStatus.ACTIVE,
        "ip_address": IPv4Address("192.168.1.1"),
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "session_data": {"terminal_size": {"rows": 24, "cols": 80}},
    }


@pytest.fixture
def sample_analytics_event_data() -> dict[str, Any]:
    """
    샘플 AnalyticsEvent 데이터 딕셔너리
    """
    return {
        "event_type": "tip_view",
        "ip_address": IPv4Address("192.168.1.100"),
        "user_agent": "Mozilla/5.0",
        "event_data": {"referrer": "https://google.com", "device": "desktop"},
    }


# ============================================================
# 모델 인스턴스 Fixtures
# ============================================================


@pytest_asyncio.fixture
async def tip_instance(
    async_db_session: AsyncSession, sample_tip_data: dict[str, Any]
) -> Tip:
    """
    데이터베이스에 저장된 Tip 인스턴스 반환

    테스트에서 즉시 사용 가능한 Tip 객체를 제공합니다.
    flush()를 사용하여 ID를 생성하지만 트랜잭션은 커밋하지 않습니다.
    """
    tip = Tip(**sample_tip_data)
    async_db_session.add(tip)
    await async_db_session.flush()  # commit() 대신 flush() 사용
    await async_db_session.refresh(tip)
    return tip


@pytest_asyncio.fixture
async def admin_user_instance(
    async_db_session: AsyncSession, sample_admin_user_data: dict[str, Any]
) -> AdminUser:
    """
    데이터베이스에 저장된 AdminUser 인스턴스 반환
    """
    user = AdminUser(**sample_admin_user_data)
    async_db_session.add(user)
    await async_db_session.flush()  # commit() 대신 flush() 사용
    await async_db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def draft_week_instance(
    async_db_session: AsyncSession, sample_draft_week_data: dict[str, Any]
) -> DraftWeek:
    """
    데이터베이스에 저장된 DraftWeek 인스턴스 반환
    """
    draft_week = DraftWeek(**sample_draft_week_data)
    async_db_session.add(draft_week)
    await async_db_session.flush()  # commit() 대신 flush() 사용
    await async_db_session.refresh(draft_week)
    return draft_week


@pytest_asyncio.fixture
async def terminal_session_instance(
    async_db_session: AsyncSession,
    tip_instance: Tip,
    sample_terminal_session_data: dict[str, Any],
) -> TerminalSession:
    """
    데이터베이스에 저장된 TerminalSession 인스턴스 반환 (Tip과 연결됨)
    """
    session_data = sample_terminal_session_data.copy()
    session_data["tip_id"] = tip_instance.id
    terminal_session = TerminalSession(**session_data)
    async_db_session.add(terminal_session)
    await async_db_session.flush()  # commit() 대신 flush() 사용
    await async_db_session.refresh(terminal_session)
    return terminal_session


@pytest_asyncio.fixture
async def analytics_event_instance(
    async_db_session: AsyncSession,
    tip_instance: Tip,
    sample_analytics_event_data: dict[str, Any],
) -> AnalyticsEvent:
    """
    데이터베이스에 저장된 AnalyticsEvent 인스턴스 반환 (Tip과 연결됨)
    """
    event_data = sample_analytics_event_data.copy()
    event_data["tip_id"] = tip_instance.id
    event = AnalyticsEvent(**event_data)
    async_db_session.add(event)
    await async_db_session.flush()  # commit() 대신 flush() 사용
    await async_db_session.refresh(event)
    return event
