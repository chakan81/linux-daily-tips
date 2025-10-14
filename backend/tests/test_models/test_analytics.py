"""
AnalyticsEvent 모델 테스트

테스트 항목:
- ULID + Prefix ID 자동 생성 (evt_...)
- event_type 문자열 타입
- IP 주소 저장 (INET 타입)
- JSON 필드 (event_data)
- Tip과의 관계
- 익명 이벤트 (tip_id=None)
"""

from datetime import datetime
from ipaddress import IPv4Address, IPv6Address
from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analytics import AnalyticsEvent, EventType
from app.models.tip import Tip


@pytest.mark.unit
class TestAnalyticsEventModel:
    """AnalyticsEvent 모델 기본 동작 테스트"""

    async def test_create_analytics_event_with_minimal_data(
        self, async_db_session: AsyncSession
    ) -> None:
        """최소 필드만으로 AnalyticsEvent 생성 가능"""
        event = AnalyticsEvent(event_type="test_event")
        async_db_session.add(event)
        await async_db_session.flush()
        await async_db_session.refresh(event)

        # 자동 생성 필드 검증
        assert event.id.startswith("evt_")
        assert len(event.id) == 30  # evt_ (4) + ULID (26)
        assert event.event_type == "test_event"
        assert event.event_data == {}  # 기본값
        assert event.tip_id is None  # nullable
        assert event.session_id is None  # nullable
        assert event.created_at is not None

    async def test_create_analytics_event_with_full_data(
        self,
        async_db_session: AsyncSession,
        tip_instance: Tip,
        sample_analytics_event_data: dict[str, Any],
    ) -> None:
        """모든 필드를 포함한 AnalyticsEvent 생성"""
        event_data = sample_analytics_event_data.copy()
        event_data["tip_id"] = tip_instance.id
        event_data["session_id"] = "session_01JCAW0V1QQ9KZ2F3XHBP8TGNY"

        event = AnalyticsEvent(**event_data)
        async_db_session.add(event)
        await async_db_session.flush()
        await async_db_session.refresh(event)

        assert event.event_type == sample_analytics_event_data["event_type"]
        assert event.tip_id == tip_instance.id
        assert event.ip_address == sample_analytics_event_data["ip_address"]
        assert event.event_data == sample_analytics_event_data["event_data"]

    async def test_analytics_event_id_is_unique(
        self, async_db_session: AsyncSession
    ) -> None:
        """AnalyticsEvent ID는 고유함"""
        event1 = AnalyticsEvent(event_type="event1")
        event2 = AnalyticsEvent(event_type="event2")

        async_db_session.add(event1)
        await async_db_session.flush()
        async_db_session.add(event2)
        await async_db_session.flush()

        assert event1.id != event2.id
        assert event1.id < event2.id  # ULID 시간순 정렬

    async def test_analytics_event_created_at_auto_generated(
        self, async_db_session: AsyncSession
    ) -> None:
        """created_at 타임스탬프 자동 생성"""
        event = AnalyticsEvent(event_type="test")
        async_db_session.add(event)
        await async_db_session.flush()
        await async_db_session.refresh(event)

        assert event.created_at is not None
        assert isinstance(event.created_at, datetime)
        assert event.created_at.tzinfo is not None

    async def test_analytics_event_types_constants(
        self, async_db_session: AsyncSession
    ) -> None:
        """EventType 상수를 사용한 이벤트 생성"""
        events = [
            AnalyticsEvent(event_type=EventType.TIP_VIEW),
            AnalyticsEvent(event_type=EventType.TIP_COPY),
            AnalyticsEvent(event_type=EventType.TERMINAL_START),
            AnalyticsEvent(event_type=EventType.TERMINAL_COMMAND),
            AnalyticsEvent(event_type=EventType.SEARCH),
        ]

        async_db_session.add_all(events)
        await async_db_session.flush()

        assert events[0].event_type == "tip_view"
        assert events[1].event_type == "tip_copy"
        assert events[2].event_type == "terminal_start"
        assert events[3].event_type == "terminal_command"
        assert events[4].event_type == "search"

    async def test_analytics_event_ipv4_address(
        self, async_db_session: AsyncSession
    ) -> None:
        """IPv4 주소 저장 및 조회"""
        ipv4 = IPv4Address("203.0.113.42")
        event = AnalyticsEvent(event_type="test", ip_address=ipv4)
        async_db_session.add(event)
        await async_db_session.flush()
        await async_db_session.refresh(event)

        assert event.ip_address == ipv4
        assert isinstance(event.ip_address, IPv4Address)

    async def test_analytics_event_ipv6_address(
        self, async_db_session: AsyncSession
    ) -> None:
        """IPv6 주소 저장 및 조회"""
        ipv6 = IPv6Address("2001:db8::1")
        event = AnalyticsEvent(event_type="test", ip_address=ipv6)
        async_db_session.add(event)
        await async_db_session.flush()
        await async_db_session.refresh(event)

        assert event.ip_address == ipv6
        assert isinstance(event.ip_address, IPv6Address)

    async def test_analytics_event_json_field(
        self, async_db_session: AsyncSession
    ) -> None:
        """event_data JSONB 필드 저장 및 조회"""
        event_data = {
            "command": "ls -la",
            "execution_time_ms": 125,
            "exit_code": 0,
            "referrer": "https://google.com",
            "device_type": "mobile",
        }
        event = AnalyticsEvent(event_type="terminal_command", event_data=event_data)
        async_db_session.add(event)
        await async_db_session.flush()
        await async_db_session.refresh(event)

        assert event.event_data == event_data
        assert isinstance(event.event_data, dict)

    async def test_analytics_event_with_session_id(
        self, async_db_session: AsyncSession
    ) -> None:
        """session_id 필드 테스트"""
        session_id = "session_01JCAW0V1QQ9KZ2F3XHBP8TGNY"
        event = AnalyticsEvent(event_type="terminal_start", session_id=session_id)
        async_db_session.add(event)
        await async_db_session.flush()
        await async_db_session.refresh(event)

        assert event.session_id == session_id

    async def test_analytics_event_anonymous(
        self, async_db_session: AsyncSession
    ) -> None:
        """익명 이벤트 (tip_id=None) 생성 가능"""
        event = AnalyticsEvent(
            event_type="page_view", tip_id=None, session_id=None, ip_address=None
        )
        async_db_session.add(event)
        await async_db_session.flush()
        await async_db_session.refresh(event)

        assert event.tip_id is None
        assert event.session_id is None
        assert event.ip_address is None

    async def test_analytics_event_delete(
        self, async_db_session: AsyncSession, analytics_event_instance: AnalyticsEvent
    ) -> None:
        """AnalyticsEvent 삭제"""
        event_id = analytics_event_instance.id

        await async_db_session.delete(analytics_event_instance)
        await async_db_session.flush()

        result = await async_db_session.execute(
            select(AnalyticsEvent).where(AnalyticsEvent.id == event_id)
        )
        found_event = result.scalar_one_or_none()
        assert found_event is None

    async def test_analytics_event_repr(
        self, analytics_event_instance: AnalyticsEvent
    ) -> None:
        """__repr__ 메서드 테스트"""
        repr_str = repr(analytics_event_instance)
        assert "AnalyticsEvent" in repr_str
        assert analytics_event_instance.id in repr_str
        assert analytics_event_instance.event_type in repr_str


@pytest.mark.unit
class TestAnalyticsEventRelationships:
    """AnalyticsEvent 모델 관계(Relationship) 테스트"""

    async def test_analytics_event_tip_relationship(
        self,
        async_db_session: AsyncSession,
        tip_instance: Tip,
        analytics_event_instance: AnalyticsEvent,
    ) -> None:
        """AnalyticsEvent ↔ Tip 관계 테스트"""
        # Relationship을 통해 Tip 조회
        await async_db_session.refresh(analytics_event_instance, ["tip"])
        assert analytics_event_instance.tip is not None
        assert analytics_event_instance.tip.id == tip_instance.id

        # 역방향 관계는 Tip 테스트에서 검증됨

    async def test_analytics_event_tip_deleted_sets_null(
        self,
        async_db_session: AsyncSession,
        tip_instance: Tip,
        sample_analytics_event_data: dict[str, Any],
    ) -> None:
        """Tip 삭제 시 AnalyticsEvent는 보존되고 tip_id만 NULL로 설정됨 (통계 데이터 보존)"""
        # 이벤트 생성
        event_data = sample_analytics_event_data.copy()
        event_data["tip_id"] = tip_instance.id
        event = AnalyticsEvent(**event_data)
        async_db_session.add(event)
        await async_db_session.flush()
        event_id = event.id

        # Tip 삭제
        await async_db_session.delete(tip_instance)
        await async_db_session.flush()
        # 세션 캐시 무효화 (데이터베이스의 SET NULL 반영)
        async_db_session.expire_all()

        # 이벤트는 여전히 존재하지만 tip_id는 NULL (통계 데이터 보존)
        result = await async_db_session.execute(
            select(AnalyticsEvent).where(AnalyticsEvent.id == event_id)
        )
        found_event = result.scalar_one_or_none()
        assert found_event is not None
        assert found_event.tip_id is None  # SET NULL


@pytest.mark.unit
class TestEventTypeConstants:
    """EventType 상수 클래스 테스트"""

    def test_event_type_constants_exist(self) -> None:
        """EventType 상수들이 정의되어 있는지 확인"""
        assert EventType.TIP_VIEW == "tip_view"
        assert EventType.TIP_COPY == "tip_copy"
        assert EventType.TIP_SHARE == "tip_share"
        assert EventType.TERMINAL_START == "terminal_start"
        assert EventType.TERMINAL_COMMAND == "terminal_command"
        assert EventType.TERMINAL_END == "terminal_end"
        assert EventType.SEARCH == "search"
        assert EventType.CATEGORY_FILTER == "category_filter"
        assert EventType.DIFFICULTY_FILTER == "difficulty_filter"
        assert EventType.ERROR == "error"
        assert EventType.PAGE_VIEW == "page_view"

    def test_event_type_constants_are_strings(self) -> None:
        """EventType 상수들이 문자열 타입인지 확인"""
        assert isinstance(EventType.TIP_VIEW, str)
        assert isinstance(EventType.TERMINAL_START, str)
        assert isinstance(EventType.SEARCH, str)
