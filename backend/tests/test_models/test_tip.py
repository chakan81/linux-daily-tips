"""
Tip 모델 테스트

테스트 항목:
- ULID + Prefix ID 자동 생성 (tip_...)
- TimestampMixin 동작 (created_at, updated_at)
- CRUD 기본 동작
- DifficultyLevel Enum 검증
- JSON 필드 (category, terminal_setup)
- Relationship (TerminalSession, AnalyticsEvent)
"""

from datetime import date, datetime, timezone
from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analytics import AnalyticsEvent
from app.models.terminal import TerminalSession
from app.models.tip import DifficultyLevel, Tip


@pytest.mark.unit
class TestTipModel:
    """Tip 모델 기본 동작 테스트"""

    async def test_create_tip_with_minimal_data(
        self, async_db_session: AsyncSession
    ) -> None:
        """최소 필드만으로 Tip 생성 가능"""
        tip = Tip(
            title="간단한 팁",
            content="간단한 내용입니다. 최소 20자 이상이어야 합니다.",
        )
        async_db_session.add(tip)
        await async_db_session.flush()
        await async_db_session.refresh(tip)

        # 자동 생성 필드 검증
        assert tip.id.startswith("tip_")
        assert len(tip.id) == 30  # tip_ (4) + ULID (26)
        assert tip.difficulty == DifficultyLevel.BEGINNER  # 기본값
        assert tip.category == []  # 기본값
        assert tip.terminal_setup == {}  # 기본값
        assert tip.is_active is True  # 기본값
        assert tip.view_count == 0  # 기본값
        assert tip.publish_date == date.today()  # 기본값

    async def test_create_tip_with_full_data(
        self, async_db_session: AsyncSession, sample_tip_data: dict[str, Any]
    ) -> None:
        """모든 필드를 포함한 Tip 생성"""
        tip = Tip(**sample_tip_data)
        async_db_session.add(tip)
        await async_db_session.flush()
        await async_db_session.refresh(tip)

        assert tip.title == sample_tip_data["title"]
        assert tip.content == sample_tip_data["content"]
        assert tip.difficulty == sample_tip_data["difficulty"]
        assert tip.category == sample_tip_data["category"]
        assert tip.terminal_setup == sample_tip_data["terminal_setup"]

    async def test_tip_id_is_unique_and_time_sortable(
        self, async_db_session: AsyncSession
    ) -> None:
        """Tip ID는 고유하며 시간순 정렬 가능"""
        tip1 = Tip(title="첫 번째 팁", content="첫 번째 팁입니다. 최소 20자 이상.")
        tip2 = Tip(title="두 번째 팁", content="두 번째 팁입니다. 최소 20자 이상.")

        async_db_session.add(tip1)
        await async_db_session.flush()
        async_db_session.add(tip2)
        await async_db_session.flush()

        # ID는 고유함
        assert tip1.id != tip2.id

        # ULID는 시간순 정렬 가능 (먼저 생성된 ID가 사전순으로 앞섬)
        assert tip1.id < tip2.id

    async def test_tip_timestamps_auto_generated(
        self, async_db_session: AsyncSession
    ) -> None:
        """created_at, updated_at 타임스탬프 자동 생성"""
        tip = Tip(title="타임스탬프 테스트", content="타임스탬프 테스트입니다. 최소 20자 이상.")
        async_db_session.add(tip)
        await async_db_session.flush()
        await async_db_session.refresh(tip)

        # 타임스탬프가 자동 생성됨
        assert tip.created_at is not None
        assert tip.updated_at is not None
        assert isinstance(tip.created_at, datetime)
        assert isinstance(tip.updated_at, datetime)

        # UTC 시간대 확인
        assert tip.created_at.tzinfo is not None
        assert tip.updated_at.tzinfo is not None

    async def test_tip_updated_at_changes_on_update(
        self, async_db_session: AsyncSession, tip_instance: Tip
    ) -> None:
        """updated_at은 업데이트 시 자동 갱신"""
        original_updated_at = tip_instance.updated_at

        # 약간의 시간 지연
        import asyncio

        await asyncio.sleep(0.1)

        # 필드 수정
        tip_instance.title = "수정된 제목"
        await async_db_session.flush()
        await async_db_session.refresh(tip_instance)

        # updated_at이 갱신됨
        assert tip_instance.updated_at > original_updated_at

    async def test_tip_difficulty_enum_validation(
        self, async_db_session: AsyncSession
    ) -> None:
        """DifficultyLevel Enum 타입 검증"""
        # 유효한 난이도
        tip_beginner = Tip(
            title="초급 팁",
            content="초급 팁입니다. 최소 20자 이상.",
            difficulty=DifficultyLevel.BEGINNER,
        )
        tip_intermediate = Tip(
            title="중급 팁",
            content="중급 팁입니다. 최소 20자 이상.",
            difficulty=DifficultyLevel.INTERMEDIATE,
        )
        tip_advanced = Tip(
            title="고급 팁",
            content="고급 팁입니다. 최소 20자 이상.",
            difficulty=DifficultyLevel.ADVANCED,
        )

        async_db_session.add_all([tip_beginner, tip_intermediate, tip_advanced])
        await async_db_session.flush()

        # 모두 정상 저장됨
        assert tip_beginner.difficulty == DifficultyLevel.BEGINNER
        assert tip_intermediate.difficulty == DifficultyLevel.INTERMEDIATE
        assert tip_advanced.difficulty == DifficultyLevel.ADVANCED

    async def test_tip_category_json_field(self, async_db_session: AsyncSession) -> None:
        """category JSONB 필드 저장 및 조회"""
        categories = ["file-system", "permissions", "search"]
        tip = Tip(
            title="카테고리 테스트",
            content="카테고리 테스트입니다. 최소 20자 이상.",
            category=categories,
        )
        async_db_session.add(tip)
        await async_db_session.flush()
        await async_db_session.refresh(tip)

        # JSONB 배열로 정상 저장 및 조회
        assert tip.category == categories
        assert isinstance(tip.category, list)

    async def test_tip_terminal_setup_json_field(
        self, async_db_session: AsyncSession
    ) -> None:
        """terminal_setup JSONB 필드 저장 및 조회"""
        terminal_setup = {
            "files": [
                {"path": "/home/user/test.txt", "content": "Hello World"},
                {"path": "/home/user/script.sh", "content": "#!/bin/bash\necho test"},
            ],
            "directories": ["/home/user/logs", "/home/user/data"],
        }
        tip = Tip(
            title="터미널 설정 테스트",
            content="터미널 설정 테스트입니다. 최소 20자 이상.",
            terminal_setup=terminal_setup,
        )
        async_db_session.add(tip)
        await async_db_session.flush()
        await async_db_session.refresh(tip)

        # JSONB 객체로 정상 저장 및 조회
        assert tip.terminal_setup == terminal_setup
        assert isinstance(tip.terminal_setup, dict)
        assert len(tip.terminal_setup["files"]) == 2
        assert len(tip.terminal_setup["directories"]) == 2

    async def test_tip_view_count_increment(
        self, async_db_session: AsyncSession, tip_instance: Tip
    ) -> None:
        """조회수 증가 테스트"""
        initial_count = tip_instance.view_count

        tip_instance.view_count += 1
        await async_db_session.flush()
        await async_db_session.refresh(tip_instance)

        assert tip_instance.view_count == initial_count + 1

    async def test_tip_is_active_toggle(
        self, async_db_session: AsyncSession, tip_instance: Tip
    ) -> None:
        """활성화 상태 토글 테스트"""
        assert tip_instance.is_active is True

        tip_instance.is_active = False
        await async_db_session.flush()
        await async_db_session.refresh(tip_instance)

        assert tip_instance.is_active is False

    async def test_tip_read_by_id(
        self, async_db_session: AsyncSession, tip_instance: Tip
    ) -> None:
        """ID로 Tip 조회"""
        result = await async_db_session.execute(
            select(Tip).where(Tip.id == tip_instance.id)
        )
        found_tip = result.scalar_one_or_none()

        assert found_tip is not None
        assert found_tip.id == tip_instance.id
        assert found_tip.title == tip_instance.title

    async def test_tip_update_fields(
        self, async_db_session: AsyncSession, tip_instance: Tip
    ) -> None:
        """Tip 필드 업데이트"""
        new_title = "업데이트된 제목"
        new_difficulty = DifficultyLevel.ADVANCED
        new_categories = ["advanced", "scripting"]

        tip_instance.title = new_title
        tip_instance.difficulty = new_difficulty
        tip_instance.category = new_categories

        await async_db_session.flush()
        await async_db_session.refresh(tip_instance)

        assert tip_instance.title == new_title
        assert tip_instance.difficulty == new_difficulty
        assert tip_instance.category == new_categories

    async def test_tip_delete(
        self, async_db_session: AsyncSession, tip_instance: Tip
    ) -> None:
        """Tip 삭제"""
        tip_id = tip_instance.id

        await async_db_session.delete(tip_instance)
        await async_db_session.flush()

        # 삭제 후 조회 시 None 반환
        result = await async_db_session.execute(select(Tip).where(Tip.id == tip_id))
        found_tip = result.scalar_one_or_none()
        assert found_tip is None

    async def test_tip_repr(self, tip_instance: Tip) -> None:
        """__repr__ 메서드 테스트"""
        repr_str = repr(tip_instance)
        assert "Tip" in repr_str
        assert tip_instance.id in repr_str
        assert tip_instance.difficulty.value in repr_str


@pytest.mark.unit
class TestTipRelationships:
    """Tip 모델 관계(Relationship) 테스트"""

    async def test_tip_terminal_sessions_relationship(
        self,
        async_db_session: AsyncSession,
        tip_instance: Tip,
        terminal_session_instance: TerminalSession,
    ) -> None:
        """Tip ↔ TerminalSession 관계 테스트"""
        # Relationship을 통해 터미널 세션 조회 가능
        await async_db_session.refresh(tip_instance, ["terminal_sessions"])
        assert len(tip_instance.terminal_sessions) == 1
        assert tip_instance.terminal_sessions[0].id == terminal_session_instance.id

        # 역방향 관계도 동작
        await async_db_session.refresh(terminal_session_instance, ["tip"])
        assert terminal_session_instance.tip.id == tip_instance.id

    async def test_tip_analytics_events_relationship(
        self,
        async_db_session: AsyncSession,
        tip_instance: Tip,
        analytics_event_instance: AnalyticsEvent,
    ) -> None:
        """Tip ↔ AnalyticsEvent 관계 테스트"""
        await async_db_session.refresh(tip_instance, ["analytics_events"])
        assert len(tip_instance.analytics_events) == 1
        assert tip_instance.analytics_events[0].id == analytics_event_instance.id

        # 역방향 관계도 동작
        await async_db_session.refresh(analytics_event_instance, ["tip"])
        assert analytics_event_instance.tip.id == tip_instance.id

    async def test_tip_cascade_delete_terminal_sessions(
        self,
        async_db_session: AsyncSession,
        tip_instance: Tip,
        terminal_session_instance: TerminalSession,
    ) -> None:
        """Tip 삭제 시 연결된 TerminalSession도 cascade 삭제"""
        tip_id = tip_instance.id
        session_id = terminal_session_instance.id

        # Tip 삭제
        await async_db_session.delete(tip_instance)
        await async_db_session.flush()

        # 연결된 TerminalSession도 삭제됨
        result = await async_db_session.execute(
            select(TerminalSession).where(TerminalSession.id == session_id)
        )
        found_session = result.scalar_one_or_none()
        assert found_session is None

    async def test_tip_delete_sets_analytics_tip_id_null(
        self,
        async_db_session: AsyncSession,
        tip_instance: Tip,
        analytics_event_instance: AnalyticsEvent,
    ) -> None:
        """Tip 삭제 시 AnalyticsEvent는 보존되고 tip_id만 NULL로 설정됨 (통계 데이터 보존)"""
        event_id = analytics_event_instance.id

        # Tip 삭제
        await async_db_session.delete(tip_instance)
        await async_db_session.flush()
        # 세션 캐시 무효화 (데이터베이스의 SET NULL 반영)
        async_db_session.expire_all()

        # AnalyticsEvent는 여전히 존재하지만 tip_id는 NULL
        result = await async_db_session.execute(
            select(AnalyticsEvent).where(AnalyticsEvent.id == event_id)
        )
        found_event = result.scalar_one_or_none()
        assert found_event is not None
        assert found_event.tip_id is None  # SET NULL
