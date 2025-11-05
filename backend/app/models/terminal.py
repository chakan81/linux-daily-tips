"""
TerminalSession 모델 - 웹 터미널 세션 관리

사용자가 웹 브라우저에서 실행하는 터미널 에뮬레이터 세션을 추적합니다.
- ULID + 프리픽스 ID 시스템 (session_01JCAW0V1QQ9KZ2F3XHBP8TGNY)
- Docker 컨테이너 기반 샌드박스 환경
- 자동 만료 시스템 (기본 30분)
"""

import enum
from datetime import datetime, timedelta, timezone
from ipaddress import IPv4Address, IPv6Address
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.ulid_helper import generate_session_id
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.tip import Tip


class TerminalStatus(str, enum.Enum):
    """
    터미널 세션 상태

    active: 활성 세션 (사용자가 터미널 사용 중)
    terminated: 사용자가 수동으로 종료
    expired: 자동 만료 (expires_at 초과)
    """

    ACTIVE = "active"
    TERMINATED = "terminated"
    EXPIRED = "expired"


class TerminalSession(Base):
    """
    웹 터미널 세션 모델

    각 팁마다 사용자가 실습할 수 있는 독립적인 터미널 환경을 제공합니다.
    Docker 컨테이너를 통해 안전한 샌드박스 환경을 구성합니다.

    Attributes:
        id: ULID 기반 Primary Key (session_01JCAW0V1QQ9KZ2F3XHBP8TGNY)
        tip_id: 연결된 Tip ID (FK to tips, nullable for anonymous sessions)
        container_id: Docker 컨테이너 ID
        status: 세션 상태 (active/terminated/expired)
        ip_address: 사용자 IP 주소 (INET 타입, IPv4/IPv6 지원)
        user_agent: 사용자 브라우저 정보
        session_data: 세션 메타데이터 (JSONB, 예: 사용자 설정, 터미널 크기)
        created_at: 세션 생성 시각
        expires_at: 세션 만료 시각 (기본 30분 후)
        terminated_at: 세션 종료 시각

    Relationships:
        tip: 연결된 Tip

    Security:
        - 각 세션은 격리된 Docker 컨테이너에서 실행
        - 30분 후 자동 만료 및 컨테이너 정리
        - IP 주소 및 User-Agent 추적 (악용 방지)

    Business Rules:
        - expires_at 초과 시 백그라운드 작업이 status를 'expired'로 변경
        - terminated_at은 사용자가 수동 종료하거나 자동 만료 시 설정
        - 만료된 세션의 컨테이너는 백그라운드 작업으로 정리

    Example:
        ```python
        session = TerminalSession(
            tip_id="tip_01JCAW0V...",
            container_id="abc123def456",
            ip_address=IPv4Address("192.168.1.1"),
            user_agent="Mozilla/5.0...",
            session_data={"terminal_size": {"rows": 24, "cols": 80}}
        )
        ```
    """

    __tablename__ = "terminal_sessions"
    __table_args__ = {"schema": "linux_tips"}

    # Primary Key - ULID + 프리픽스
    id: Mapped[str] = mapped_column(
        String(34),  # session_ (8) + ULID (26) = 34
        primary_key=True,
        default=generate_session_id,
        comment="Format: session_01JCAW0V1QQ9KZ2F3XHBP8TGNY",
    )

    # 연결 정보
    tip_id: Mapped[str | None] = mapped_column(
        String(30),  # tip_ (4) + ULID (26)
        ForeignKey("linux_tips.tips.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="연결된 Tip ID (익명 세션은 NULL)",
    )

    container_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Docker 컨테이너 ID",
    )

    # 상태
    status: Mapped[TerminalStatus] = mapped_column(
        Enum(
            TerminalStatus,
            values_callable=lambda x: [e.value for e in x],
            name="terminal_status",
            schema="linux_tips",
        ),
        nullable=False,
        default=TerminalStatus.ACTIVE,
        index=True,
        comment="세션 상태 (active/terminated/expired)",
    )

    # 사용자 정보
    ip_address: Mapped[IPv4Address | IPv6Address | None] = mapped_column(
        INET,
        nullable=True,
        comment="사용자 IP 주소 (IPv4/IPv6)",
    )

    user_agent: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="사용자 브라우저 정보",
    )

    # 세션 데이터
    session_data: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
        comment='세션 메타데이터 (예: {"terminal_size": {"rows": 24, "cols": 80}})',
    )

    # 타임스탬프 (created_at만 필요, 터미널 세션은 수정되지 않음)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        comment="세션 생성 시각 (UTC)",
    )

    # 만료 시간
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc) + timedelta(minutes=30),
        index=True,
        comment="세션 만료 시각 (기본 30분 후)",
    )

    terminated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="세션 종료 시각 (수동/자동 종료 시)",
    )

    # Relationships
    tip: Mapped["Tip | None"] = relationship(
        "Tip",
        back_populates="terminal_sessions",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<TerminalSession(id={self.id}, tip_id={self.tip_id}, status={self.status.value})>"

    @property
    def is_expired(self) -> bool:
        """세션이 만료되었는지 확인"""
        return datetime.now(timezone.utc) > self.expires_at

    @property
    def remaining_time(self) -> timedelta:
        """세션 남은 시간 (음수일 경우 이미 만료됨)"""
        return self.expires_at - datetime.now(timezone.utc)
