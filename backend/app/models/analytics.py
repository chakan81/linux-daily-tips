"""
AnalyticsEvent 모델 - 사용자 행동 분석

사용자의 모든 상호작용을 추적하여 서비스 개선에 활용합니다.
- ULID + 프리픽스 ID 시스템 (evt_01JCAW0V1QQ9KZ2F3XHBP8TGNY)
- 유연한 이벤트 데이터 저장 (JSONB)
- 익명 사용자 추적 가능
"""

from datetime import datetime, timezone
from ipaddress import IPv4Address, IPv6Address
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.ulid_helper import generate_id
from app.core.id_prefixes import IDPrefix
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.tip import Tip


class AnalyticsEvent(Base):
    """
    사용자 행동 분석 이벤트 모델

    모든 사용자 상호작용을 추적하여 서비스 개선 및 통계 분석에 활용합니다.

    Attributes:
        id: ULID 기반 Primary Key (evt_01JCAW0V1QQ9KZ2F3XHBP8TGNY)
        event_type: 이벤트 타입 (tip_view, terminal_start, terminal_command 등)
        tip_id: 연결된 Tip ID (FK to tips, nullable)
        session_id: 터미널 세션 ID 또는 익명 세션 ID
        ip_address: 사용자 IP 주소
        user_agent: 사용자 브라우저 정보
        event_data: 이벤트별 추가 데이터 (JSONB, 예: 명령어, 클릭 위치)
        created_at: 이벤트 발생 시각

    Relationships:
        tip: 연결된 Tip (nullable)

    Event Types:
        - tip_view: 팁 조회
        - tip_copy: 팁 코드 복사
        - terminal_start: 터미널 세션 시작
        - terminal_command: 터미널 명령어 실행
        - terminal_end: 터미널 세션 종료
        - search: 검색 실행
        - share: 공유 버튼 클릭

    Privacy:
        - IP 주소는 익명화 처리 가능 (마지막 옥텟 마스킹)
        - 개인 식별 정보 저장 금지
        - GDPR 준수를 위한 데이터 보관 기간 설정 필요

    Example:
        ```python
        # 팁 조회 이벤트
        event = AnalyticsEvent(
            event_type="tip_view",
            tip_id="tip_01JCAW0V...",
            ip_address=IPv4Address("192.168.1.1"),
            user_agent="Mozilla/5.0...",
            event_data={
                "referrer": "https://google.com",
                "device": "mobile"
            }
        )

        # 터미널 명령어 실행 이벤트
        cmd_event = AnalyticsEvent(
            event_type="terminal_command",
            tip_id="tip_01JCAW0V...",
            session_id="session_01JCAW0V...",
            event_data={
                "command": "ls -la",
                "execution_time_ms": 45
            }
        )
        ```
    """

    __tablename__ = "analytics_events"
    __table_args__ = {"schema": "linux_tips"}

    # Primary Key - ULID + 프리픽스
    id: Mapped[str] = mapped_column(
        String(30),  # evt_ (4) + ULID (26) = 30
        primary_key=True,
        default=lambda: generate_id(IDPrefix.EVENT),
        comment="Format: evt_01JCAW0V1QQ9KZ2F3XHBP8TGNY",
    )

    # 이벤트 타입
    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="이벤트 타입 (tip_view, terminal_start, terminal_command 등)",
    )

    # 연결 정보
    tip_id: Mapped[str | None] = mapped_column(
        String(30),  # tip_ (4) + ULID (26)
        ForeignKey("linux_tips.tips.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="연결된 Tip ID (익명 이벤트는 NULL)",
    )

    session_id: Mapped[str | None] = mapped_column(
        String(34),  # session_ (8) + ULID (26)
        nullable=True,
        index=True,
        comment="터미널 세션 ID 또는 익명 세션 ID",
    )

    # 사용자 정보
    ip_address: Mapped[IPv4Address | IPv6Address | None] = mapped_column(
        INET,
        nullable=True,
        comment="사용자 IP 주소 (익명화 처리 가능)",
    )

    user_agent: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="사용자 브라우저 정보",
    )

    # 이벤트 데이터 (유연한 구조)
    event_data: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
        comment='이벤트별 추가 데이터 (예: {"command": "ls", "referrer": "google.com"})',
    )

    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
        comment="이벤트 발생 시각 (UTC)",
    )

    # Relationships
    tip: Mapped["Tip | None"] = relationship(
        "Tip",
        back_populates="analytics_events",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<AnalyticsEvent(id={self.id}, type={self.event_type}, tip_id={self.tip_id})>"


# 주요 이벤트 타입 상수 정의 (타입 안전성 향상)
class EventType:
    """분석 이벤트 타입 상수"""

    TIP_VIEW = "tip_view"
    TIP_COPY = "tip_copy"
    TIP_SHARE = "tip_share"

    TERMINAL_START = "terminal_start"
    TERMINAL_COMMAND = "terminal_command"
    TERMINAL_END = "terminal_end"

    SEARCH = "search"
    CATEGORY_FILTER = "category_filter"
    DIFFICULTY_FILTER = "difficulty_filter"

    ERROR = "error"
    PAGE_VIEW = "page_view"
