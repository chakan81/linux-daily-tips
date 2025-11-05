"""
AdminUser 모델 - 관리자 사용자

드래프트 승인 및 관리 기능을 수행하는 관리자 계정을 저장합니다.
- ULID + 프리픽스 ID 시스템 (user_01JCAW0V1QQ9KZ2F3XHBP8TGNY)
- JWT 기반 인증 (password_hash 저장)
- 슈퍼유저 권한 관리
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.ulid_helper import generate_user_id
from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.draft import DraftWeek


class AdminUser(Base, TimestampMixin):
    """
    관리자 사용자 모델

    드래프트 승인, 팁 관리, 시스템 설정을 담당하는 관리자 계정입니다.

    Attributes:
        id: ULID 기반 Primary Key (user_01JCAW0V1QQ9KZ2F3XHBP8TGNY)
        username: 사용자명 (고유)
        email: 이메일 주소 (고유)
        password_hash: bcrypt 해시된 비밀번호
        is_active: 계정 활성화 여부
        is_superuser: 슈퍼유저 권한 여부
        last_login: 마지막 로그인 시각
        created_at: 계정 생성 시각 (UTC)
        updated_at: 계정 정보 수정 시각 (UTC)

    Relationships:
        approved_draft_weeks: 이 관리자가 승인한 드래프트 주간들

    Security:
        - 비밀번호는 절대 평문 저장하지 않음 (bcrypt hash만 저장)
        - JWT 토큰 기반 인증 사용
        - is_active=False 시 로그인 불가

    Example:
        ```python
        from passlib.context import CryptContext

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        admin = AdminUser(
            username="admin",
            email="admin@example.com",
            password_hash=pwd_context.hash("secure_password"),
            is_superuser=True
        )
        ```
    """

    __tablename__ = "admin_users"
    __table_args__ = {"schema": "linux_tips"}

    # Primary Key - ULID + 프리픽스
    id: Mapped[str] = mapped_column(
        String(31),  # user_ (5) + ULID (26) = 31
        primary_key=True,
        default=generate_user_id,
        comment="Format: user_01JCAW0V1QQ9KZ2F3XHBP8TGNY",
    )

    # 인증 정보
    username: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
        comment="사용자명 (고유)",
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        comment="이메일 주소 (고유)",
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="bcrypt 해시된 비밀번호",
    )

    # 권한 및 상태
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="계정 활성화 여부 (False 시 로그인 불가)",
    )

    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="슈퍼유저 권한 (모든 관리 기능 접근 가능)",
    )

    # 로그인 추적
    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="마지막 로그인 시각 (UTC)",
    )

    # Relationships
    approved_draft_weeks: Mapped[list["DraftWeek"]] = relationship(
        "DraftWeek",
        back_populates="approver",
        foreign_keys="DraftWeek.approved_by",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<AdminUser(id={self.id}, username={self.username}, is_superuser={self.is_superuser})>"
