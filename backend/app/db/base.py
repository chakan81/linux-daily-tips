"""
SQLAlchemy Base 모델 및 공통 Mixin 클래스

모든 모델이 상속받는 기본 클래스와 재사용 가능한 Mixin을 정의합니다.
- DeclarativeBase: SQLAlchemy 2.0 선언적 베이스
- TimestampMixin: created_at, updated_at 자동 관리
- ULIDMixin: ULID + 프리픽스 자동 생성
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    모든 SQLAlchemy 모델의 기본 클래스

    SQLAlchemy 2.0의 선언적 베이스를 사용합니다.
    모든 모델은 이 클래스를 상속받아야 합니다.
    """

    pass


class TimestampMixin:
    """
    생성 및 수정 타임스탬프 자동 관리 Mixin

    모든 모델에 created_at, updated_at 컬럼을 자동으로 추가하고,
    PostgreSQL 트리거와 함께 작동하여 타임스탬프를 관리합니다.

    Database Triggers:
        - INSERT 시: created_at, updated_at 모두 CURRENT_TIMESTAMP로 설정
        - UPDATE 시: updated_at만 CURRENT_TIMESTAMP로 갱신

    Note:
        - timezone-aware datetime 사용 (PostgreSQL TIMESTAMP WITH TIME ZONE)
        - 애플리케이션 레벨 기본값도 설정하여 이중 보호
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        comment="레코드 생성 시각 (UTC)",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        comment="레코드 최종 수정 시각 (UTC)",
    )


# Note: ULID 자동 생성은 각 모델에서 개별적으로 구현
# 이유: 각 모델마다 다른 프리픽스를 사용하므로 Mixin으로 통일할 수 없음
# 대신 아래와 같은 패턴을 각 모델에서 사용:
#
# from app.core.ulid_helper import generate_tip_id
#
# class Tip(Base, TimestampMixin):
#     __tablename__ = "linux_tips.tips"
#
#     id: Mapped[str] = mapped_column(
#         String(30),  # tip_ (4) + ULID (26)
#         primary_key=True,
#         default=generate_tip_id,  # 각 모델마다 다른 생성 함수 사용
#     )
