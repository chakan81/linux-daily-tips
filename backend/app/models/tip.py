"""
Tip 모델 - 승인된 일일 Linux 팁

매일 게시되는 Linux 사용 팁을 저장하는 메인 테이블입니다.
- ULID + 프리픽스 ID 시스템 (tip_01JCAW0V1QQ9KZ2F3XHBP8TGNY)
- 난이도 분류 (초급/중급/고급)
- 카테고리 태깅 (JSONB 배열)
- 터미널 환경 사전 구성 (JSONB)
"""

import enum
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, Enum, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.ulid_helper import generate_tip_id
from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.analytics import AnalyticsEvent
    from app.models.terminal import TerminalSession


class DifficultyLevel(str, enum.Enum):
    """
    팁 난이도 수준

    초급: 리눅스 입문자용 (파일 탐색, 기본 명령어)
    중급: 일부 경험이 있는 사용자용 (파이프, 리다이렉션, 스크립팅)
    고급: 숙련된 사용자용 (시스템 관리, 고급 스크립팅, 성능 최적화)
    """

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Tip(Base, TimestampMixin):
    """
    일일 Linux 팁 모델

    Attributes:
        id: ULID 기반 Primary Key (tip_01JCAW0V1QQ9KZ2F3XHBP8TGNY)
        title: 팁 제목 (최대 255자)
        content: 팁 내용 (Markdown 형식)
        difficulty: 난이도 (beginner/intermediate/advanced)
        category: 카테고리 태그 배열 (예: ["file-system", "permissions"])
        publish_date: 게시 날짜 (기본값: 오늘)
        terminal_setup: 터미널 사전 구성 (파일, 디렉토리 구조 JSONB)
        is_active: 활성화 여부 (비활성화 시 숨김)
        view_count: 조회수
        created_at: 생성 시각 (UTC)
        updated_at: 수정 시각 (UTC)

    Relationships:
        terminal_sessions: 이 팁과 연결된 터미널 세션들
        analytics_events: 이 팁 관련 분석 이벤트들

    Example:
        ```python
        tip = Tip(
            title="파일 권한 확인하기",
            content="```bash\\nls -l file.txt\\n```",
            difficulty=DifficultyLevel.BEGINNER,
            category=["file-system", "permissions"],
            terminal_setup={
                "files": [
                    {"path": "/home/user/file.txt", "content": "Hello World"}
                ],
                "directories": ["/home/user/test"]
            }
        )
        ```
    """

    __tablename__ = "tips"
    __table_args__ = {"schema": "linux_tips"}

    # Primary Key - ULID + 프리픽스
    id: Mapped[str] = mapped_column(
        String(30),  # tip_ (4) + ULID (26) = 30
        primary_key=True,
        default=generate_tip_id,
        comment="Format: tip_01JCAW0V1QQ9KZ2F3XHBP8TGNY (time-sortable)",
    )

    # 기본 정보
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

    # 분류
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
        comment='카테고리 태그 배열 (예: ["file-system", "permissions"])',
    )

    # 게시 정보
    publish_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        default=date.today,
        index=True,
        comment="게시 날짜",
    )

    # 터미널 환경 설정
    terminal_setup: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
        comment="터미널 사전 구성 (files, directories)",
    )

    # 상태 및 통계
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="활성화 여부 (비활성화 시 숨김)",
    )

    view_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="조회수",
    )

    # Relationships
    terminal_sessions: Mapped[list["TerminalSession"]] = relationship(
        "TerminalSession",
        back_populates="tip",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    analytics_events: Mapped[list["AnalyticsEvent"]] = relationship(
        "AnalyticsEvent",
        back_populates="tip",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Tip(id={self.id}, title={self.title[:30]}, difficulty={self.difficulty.value})>"
