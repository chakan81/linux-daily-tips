"""
TerminalSession 모델 테스트

테스트 항목:
- ULID + Prefix ID 자동 생성 (session_...)
- TerminalStatus Enum 검증
- IP 주소 저장 (INET 타입)
- JSON 필드 (session_data)
- 만료 시간 관리 (expires_at, is_expired, remaining_time)
- Tip과의 관계
"""

from datetime import datetime, timedelta, timezone
from ipaddress import IPv4Address, IPv6Address
from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.terminal import TerminalSession, TerminalStatus
from app.models.tip import Tip


@pytest.mark.unit
class TestTerminalSessionModel:
    """TerminalSession 모델 기본 동작 테스트"""

    async def test_create_terminal_session_with_minimal_data(
        self, async_db_session: AsyncSession
    ) -> None:
        """최소 필드만으로 TerminalSession 생성 가능"""
        session = TerminalSession()
        async_db_session.add(session)
        await async_db_session.flush()
        await async_db_session.refresh(session)

        # 자동 생성 필드 검증
        assert session.id.startswith("session_")
        assert len(session.id) == 34  # session_ (8) + ULID (26)
        assert session.status == TerminalStatus.ACTIVE  # 기본값
        assert session.session_data == {}  # 기본값
        assert session.tip_id is None  # nullable
        assert session.container_id is None  # nullable
        assert session.expires_at is not None  # 자동 생성 (30분 후)

    async def test_create_terminal_session_with_full_data(
        self,
        async_db_session: AsyncSession,
        tip_instance: Tip,
        sample_terminal_session_data: dict[str, Any],
    ) -> None:
        """모든 필드를 포함한 TerminalSession 생성"""
        session_data = sample_terminal_session_data.copy()
        session_data["tip_id"] = tip_instance.id

        session = TerminalSession(**session_data)
        async_db_session.add(session)
        await async_db_session.flush()
        await async_db_session.refresh(session)

        assert session.tip_id == tip_instance.id
        assert session.container_id == sample_terminal_session_data["container_id"]
        assert session.status == sample_terminal_session_data["status"]
        assert session.ip_address == sample_terminal_session_data["ip_address"]
        assert session.session_data == sample_terminal_session_data["session_data"]

    async def test_terminal_session_id_is_unique(
        self, async_db_session: AsyncSession
    ) -> None:
        """TerminalSession ID는 고유함"""
        session1 = TerminalSession()
        session2 = TerminalSession()

        async_db_session.add(session1)
        await async_db_session.flush()
        async_db_session.add(session2)
        await async_db_session.flush()

        assert session1.id != session2.id
        assert session1.id < session2.id  # ULID 시간순 정렬

    async def test_terminal_session_timestamps_auto_generated(
        self, async_db_session: AsyncSession
    ) -> None:
        """created_at 타임스탬프 자동 생성 (updated_at 없음 - 터미널 세션은 수정 안 됨)"""
        session = TerminalSession()
        async_db_session.add(session)
        await async_db_session.flush()
        await async_db_session.refresh(session)

        assert session.created_at is not None
        assert isinstance(session.created_at, datetime)
        # TerminalSession은 updated_at이 없음 (수정되지 않는 모델)

    async def test_terminal_session_status_enum_validation(
        self, async_db_session: AsyncSession
    ) -> None:
        """TerminalStatus Enum 타입 검증"""
        session_active = TerminalSession(status=TerminalStatus.ACTIVE)
        session_terminated = TerminalSession(status=TerminalStatus.TERMINATED)
        session_expired = TerminalSession(status=TerminalStatus.EXPIRED)

        async_db_session.add_all([session_active, session_terminated, session_expired])
        await async_db_session.flush()

        assert session_active.status == TerminalStatus.ACTIVE
        assert session_terminated.status == TerminalStatus.TERMINATED
        assert session_expired.status == TerminalStatus.EXPIRED

    async def test_terminal_session_ipv4_address(
        self, async_db_session: AsyncSession
    ) -> None:
        """IPv4 주소 저장 및 조회 (INET 타입)"""
        ipv4 = IPv4Address("192.168.1.100")
        session = TerminalSession(ip_address=ipv4)
        async_db_session.add(session)
        await async_db_session.flush()
        await async_db_session.refresh(session)

        assert session.ip_address == ipv4
        assert isinstance(session.ip_address, IPv4Address)

    async def test_terminal_session_ipv6_address(
        self, async_db_session: AsyncSession
    ) -> None:
        """IPv6 주소 저장 및 조회 (INET 타입)"""
        ipv6 = IPv6Address("2001:0db8:85a3:0000:0000:8a2e:0370:7334")
        session = TerminalSession(ip_address=ipv6)
        async_db_session.add(session)
        await async_db_session.flush()
        await async_db_session.refresh(session)

        assert session.ip_address == ipv6
        assert isinstance(session.ip_address, IPv6Address)

    async def test_terminal_session_json_field(
        self, async_db_session: AsyncSession
    ) -> None:
        """session_data JSONB 필드 저장 및 조회"""
        session_data = {
            "terminal_size": {"rows": 40, "cols": 120},
            "theme": "dark",
            "font_size": 14,
        }
        session = TerminalSession(session_data=session_data)
        async_db_session.add(session)
        await async_db_session.flush()
        await async_db_session.refresh(session)

        assert session.session_data == session_data
        assert isinstance(session.session_data, dict)

    async def test_terminal_session_expires_at_default(
        self, async_db_session: AsyncSession
    ) -> None:
        """expires_at 기본값은 30분 후"""
        before_create = datetime.now(timezone.utc)
        session = TerminalSession()
        async_db_session.add(session)
        await async_db_session.flush()
        await async_db_session.refresh(session)
        after_create = datetime.now(timezone.utc)

        # expires_at은 생성 시각 + 30분
        expected_min = before_create + timedelta(minutes=30)
        expected_max = after_create + timedelta(minutes=30)

        assert expected_min <= session.expires_at <= expected_max

    async def test_terminal_session_is_expired_property(
        self, async_db_session: AsyncSession
    ) -> None:
        """is_expired 프로퍼티 테스트"""
        # 아직 만료되지 않은 세션
        session_active = TerminalSession()
        async_db_session.add(session_active)
        await async_db_session.flush()
        await async_db_session.refresh(session_active)

        assert session_active.is_expired is False

        # 이미 만료된 세션
        past_time = datetime.now(timezone.utc) - timedelta(hours=1)
        session_expired = TerminalSession(expires_at=past_time)
        async_db_session.add(session_expired)
        await async_db_session.flush()
        await async_db_session.refresh(session_expired)

        assert session_expired.is_expired is True

    async def test_terminal_session_remaining_time_property(
        self, async_db_session: AsyncSession
    ) -> None:
        """remaining_time 프로퍼티 테스트"""
        session = TerminalSession()
        async_db_session.add(session)
        await async_db_session.flush()
        await async_db_session.refresh(session)

        # 남은 시간이 약 30분
        remaining = session.remaining_time
        assert isinstance(remaining, timedelta)
        assert timedelta(minutes=29) <= remaining <= timedelta(minutes=31)

    async def test_terminal_session_terminated_at(
        self, async_db_session: AsyncSession, terminal_session_instance: TerminalSession
    ) -> None:
        """terminated_at 시각 설정 테스트"""
        assert terminal_session_instance.terminated_at is None

        # 세션 종료
        termination_time = datetime.now(timezone.utc)
        terminal_session_instance.status = TerminalStatus.TERMINATED
        terminal_session_instance.terminated_at = termination_time

        await async_db_session.flush()
        await async_db_session.refresh(terminal_session_instance)

        assert terminal_session_instance.status == TerminalStatus.TERMINATED
        assert terminal_session_instance.terminated_at == termination_time

    async def test_terminal_session_delete(
        self, async_db_session: AsyncSession, terminal_session_instance: TerminalSession
    ) -> None:
        """TerminalSession 삭제"""
        session_id = terminal_session_instance.id

        await async_db_session.delete(terminal_session_instance)
        await async_db_session.flush()

        result = await async_db_session.execute(
            select(TerminalSession).where(TerminalSession.id == session_id)
        )
        found_session = result.scalar_one_or_none()
        assert found_session is None

    async def test_terminal_session_repr(
        self, terminal_session_instance: TerminalSession
    ) -> None:
        """__repr__ 메서드 테스트"""
        repr_str = repr(terminal_session_instance)
        assert "TerminalSession" in repr_str
        assert terminal_session_instance.id in repr_str
        assert terminal_session_instance.status.value in repr_str


@pytest.mark.unit
class TestTerminalSessionRelationships:
    """TerminalSession 모델 관계(Relationship) 테스트"""

    async def test_terminal_session_tip_relationship(
        self,
        async_db_session: AsyncSession,
        tip_instance: Tip,
        terminal_session_instance: TerminalSession,
    ) -> None:
        """TerminalSession ↔ Tip 관계 테스트"""
        # Relationship을 통해 Tip 조회
        await async_db_session.refresh(terminal_session_instance, ["tip"])
        assert terminal_session_instance.tip is not None
        assert terminal_session_instance.tip.id == tip_instance.id

        # 역방향 관계는 Tip 테스트에서 검증됨

    async def test_terminal_session_nullable_tip(
        self, async_db_session: AsyncSession
    ) -> None:
        """tip_id가 None인 익명 세션 생성 가능"""
        session = TerminalSession(tip_id=None)
        async_db_session.add(session)
        await async_db_session.flush()
        await async_db_session.refresh(session)

        assert session.tip_id is None
        await async_db_session.refresh(session, ["tip"])
        assert session.tip is None
