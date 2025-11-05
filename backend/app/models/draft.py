"""
Draft 모델 - LLM 생성 드래프트 시스템

LLM이 생성한 일주일치(7개) 팁 드래프트를 관리합니다.
- DraftWeek: 일주일 단위 드래프트 묶음
- DraftTip: 개별 드래프트 팁 (하루 1개)
- 관리자 승인 워크플로우 (draft → approved → rejected)
"""

import enum
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.ulid_helper import generate_draft_id
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import AdminUser

# DifficultyLevel Enum은 tip.py에서 import (TYPE_CHECKING 외부에서 사용)
from app.models.tip import DifficultyLevel


class DraftStatus(str, enum.Enum):
    """
    드래프트 승인 상태

    draft: LLM 생성 후 대기 중
    approved: 관리자 승인 완료 (Tips 테이블로 이동 예정)
    rejected: 관리자 거부 (재생성 필요)
    """

    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"


class DraftWeek(Base):
    """
    일주일치 드래프트 묶음 모델

    LLM이 한 번에 7개의 팁을 생성하며, 관리자는 주간 단위로 검토합니다.

    Attributes:
        id: ULID 기반 Primary Key (draft_01JCAW0V1QQ9KZ2F3XHBP8TGNY)
        week_start_date: 해당 주의 시작 날짜 (월요일)
        status: 승인 상태 (draft/approved/rejected)
        generated_by: 생성 주체 (기본값: 'llm')
        approved_by: 승인한 관리자 ID (FK to admin_users)
        approval_notes: 승인/거부 시 관리자 메모
        created_at: 드래프트 생성 시각
        approved_at: 승인/거부 시각

    Relationships:
        draft_tips: 이 주간에 속한 7개의 드래프트 팁
        approver: 승인한 관리자 (AdminUser)

    Business Rules:
        - 한 주에는 반드시 7개의 팁이 있어야 함 (월~일)
        - 동일 week_start_date에 대해 rejected가 아닌 드래프트는 1개만 존재
        - approved 상태가 되면 Tips 테이블로 복사 후 게시

    Example:
        ```python
        draft_week = DraftWeek(
            week_start_date=date(2024, 1, 1),  # 월요일
            status=DraftStatus.DRAFT,
            generated_by="gpt-4"
        )
        ```
    """

    __tablename__ = "draft_weeks"
    __table_args__ = {"schema": "linux_tips"}

    # Primary Key - ULID + 프리픽스
    id: Mapped[str] = mapped_column(
        String(32),  # draft_ (6) + ULID (26) = 32
        primary_key=True,
        default=generate_draft_id,
        comment="Format: draft_01JCAW0V1QQ9KZ2F3XHBP8TGNY",
    )

    # 주간 정보
    week_start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="해당 주의 시작 날짜 (월요일)",
    )

    # 승인 상태
    status: Mapped[DraftStatus] = mapped_column(
        Enum(
            DraftStatus,
            values_callable=lambda x: [e.value for e in x],
            name="draft_status",
            schema="linux_tips",
        ),
        nullable=False,
        default=DraftStatus.DRAFT,
        index=True,
        comment="승인 상태 (draft/approved/rejected)",
    )

    # 생성 및 승인 정보
    generated_by: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="llm",
        comment="생성 주체 (예: gpt-4, claude-3)",
    )

    approved_by: Mapped[str | None] = mapped_column(
        String(31),  # user_ (5) + ULID (26)
        ForeignKey("linux_tips.admin_users.id", ondelete="SET NULL"),
        nullable=True,
        comment="승인한 관리자 ID",
    )

    approval_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="승인/거부 시 관리자 메모",
    )

    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="승인/거부 시각 (UTC)",
    )

    # 타임스탬프 (created_at만 필요, draft는 수정되지 않음)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        comment="드래프트 생성 시각 (UTC)",
    )

    # Relationships
    draft_tips: Mapped[list["DraftTip"]] = relationship(
        "DraftTip",
        back_populates="draft_week",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    approver: Mapped["AdminUser | None"] = relationship(
        "AdminUser",
        back_populates="approved_draft_weeks",
        foreign_keys=[approved_by],
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<DraftWeek(id={self.id}, week_start={self.week_start_date}, status={self.status})>"


class DraftTip(Base):
    """
    개별 드래프트 팁 모델

    일주일치 드래프트에 속하는 개별 팁 (하루 1개, 총 7개)

    Attributes:
        id: ULID 기반 Primary Key (draft_01JCAW0V1QQ9KZ2F3XHBP8TGNY)
        draft_week_id: 소속 DraftWeek ID (FK)
        day_of_week: 요일 (1=월요일, 7=일요일)
        title: 팁 제목
        content: 팁 내용 (Markdown)
        difficulty: 난이도 (beginner/intermediate/advanced)
        category: 카테고리 태그 배열
        terminal_setup: 터미널 사전 구성 (JSONB)
        llm_confidence_score: LLM 신뢰도 점수 (0.0~1.0)
        created_at: 생성 시각

    Relationships:
        draft_week: 소속 DraftWeek

    Business Rules:
        - 한 DraftWeek 내에서 day_of_week는 고유 (1~7)
        - approved 상태의 DraftWeek에 속한 팁은 Tips 테이블로 복사됨

    Example:
        ```python
        draft_tip = DraftTip(
            draft_week_id="draft_01JCAW0V...",
            day_of_week=1,  # 월요일
            title="파일 검색하기",
            content="```bash\\nfind . -name '*.log'\\n```",
            difficulty=DifficultyLevel.BEGINNER,
            category=["file-system", "search"],
            llm_confidence_score=0.95
        )
        ```
    """

    __tablename__ = "draft_tips"
    __table_args__ = {"schema": "linux_tips"}

    # Primary Key - ULID + 프리픽스
    id: Mapped[str] = mapped_column(
        String(32),  # draft_ (6) + ULID (26) = 32
        primary_key=True,
        default=generate_draft_id,
        comment="Format: draft_01JCAW0V1QQ9KZ2F3XHBP8TGNY",
    )

    # 소속 정보
    draft_week_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("linux_tips.draft_weeks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="소속 DraftWeek ID",
    )

    day_of_week: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="요일 (1=월요일, 7=일요일)",
    )

    # 팁 내용 (Tip 모델과 동일 구조)
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="팁 제목",
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="팁 내용 (Markdown 형식)",
    )

    # DifficultyLevel Enum 재사용 (tip.py에서 import)
    difficulty: Mapped[DifficultyLevel] = mapped_column(
        Enum(
            DifficultyLevel,
            values_callable=lambda x: [e.value for e in x],
            name="difficulty_level",
            schema="linux_tips",
        ),
        nullable=False,
        default=DifficultyLevel.BEGINNER,
        comment="난이도 (beginner/intermediate/advanced)",
    )

    category: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default="[]",
        comment="카테고리 태그 배열",
    )

    terminal_setup: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
        comment="터미널 사전 구성",
    )

    # LLM 메타데이터
    llm_confidence_score: Mapped[Decimal | None] = mapped_column(
        Numeric(3, 2),  # 0.00 ~ 9.99 (실제로는 0.00~1.00)
        nullable=True,
        comment="LLM 신뢰도 점수 (0.0~1.0)",
    )

    # 타임스탬프 (created_at만 필요, updated_at 불필요)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        comment="생성 시각 (UTC)",
    )

    # Relationships
    draft_week: Mapped["DraftWeek"] = relationship(
        "DraftWeek",
        back_populates="draft_tips",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<DraftTip(id={self.id}, week_id={self.draft_week_id}, day={self.day_of_week}, title={self.title[:30]})>"
