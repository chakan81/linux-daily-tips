"""
Tip CRUD 작업 모듈

Tip 엔티티의 생성, 수정, 삭제 및 조회수 증가를 담당합니다.
"""

import logging
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.models.tip import Tip
from app.schemas.tip import TipCreate, TipUpdate

# 로거 인스턴스
logger = logging.getLogger(__name__)


async def create_tip(
    db: AsyncSession,
    tip_data: TipCreate,
    existing_tip_check: Tip | None = None,
) -> Tip:
    """
    새 팁 생성

    Args:
        db: 데이터베이스 세션
        tip_data: 팁 생성 데이터
        existing_tip_check: 중복 체크 결과 (이미 조회한 경우)

    Returns:
        Tip: 생성된 팁

    Raises:
        AppException: 같은 날짜에 이미 팁이 존재하는 경우 (409)

    Example:
        ```python
        tip_data = TipCreate(
            title="파일 검색하기",
            content="find 명령어 사용법...",
            difficulty=DifficultyLevel.BEGINNER,
        )
        tip = await create_tip(db, tip_data)
        ```
    """
    try:
        # publish_date가 None이면 오늘 날짜로 설정
        publish_date = tip_data.publish_date or date.today()

        # 중복 날짜 체크 (비즈니스 규칙: 하루에 하나의 팁만)
        if existing_tip_check:
            logger.warning(
                f"Tip already exists for date {publish_date}: {existing_tip_check.id}"
            )
            raise AppException(
                status_code=409,
                detail=f"{publish_date} 날짜의 팁이 이미 존재합니다",
            )

        # Tip 모델 생성
        tip = Tip(
            title=tip_data.title,
            content=tip_data.content,
            difficulty=tip_data.difficulty,
            category=tip_data.category,
            publish_date=publish_date,
            terminal_setup=tip_data.terminal_setup,
            is_active=tip_data.is_active,
        )

        db.add(tip)
        await db.flush()
        await db.refresh(tip)

        logger.info(f"Created new tip: {tip.id} for date {publish_date}")
        return tip

    except AppException:
        raise
    except Exception as e:
        logger.error(
            f"Error creating tip: {str(e)}",
            exc_info=True,
        )
        raise


async def update_tip(db: AsyncSession, tip: Tip, tip_data: TipUpdate) -> Tip:
    """
    팁 수정 (부분 업데이트)

    Args:
        db: 데이터베이스 세션
        tip: 수정할 팁 엔티티
        tip_data: 수정할 데이터 (None이 아닌 필드만 업데이트)

    Returns:
        Tip: 수정된 팁

    Example:
        ```python
        update_data = TipUpdate(title="새로운 제목", difficulty="advanced")
        tip = await update_tip(db, existing_tip, update_data)
        ```
    """
    try:
        # 업데이트할 필드만 추출 (None이 아닌 필드만)
        update_data = tip_data.model_dump(exclude_unset=True)

        if not update_data:
            logger.info(f"No fields to update for tip {tip.id}")
            return tip

        # 각 필드 업데이트
        for field, value in update_data.items():
            setattr(tip, field, value)

        await db.flush()
        await db.refresh(tip)

        logger.info(f"Updated tip {tip.id}: {list(update_data.keys())}")
        return tip

    except Exception as e:
        logger.error(
            f"Error updating tip {tip.id}: {str(e)}",
            exc_info=True,
        )
        raise


async def delete_tip(db: AsyncSession, tip: Tip) -> bool:
    """
    팁 삭제 (soft delete: is_active=False)

    Args:
        db: 데이터베이스 세션
        tip: 삭제할 팁 엔티티

    Returns:
        bool: 항상 True (성공)

    Note:
        멱등성 보장: 이미 삭제된 팁도 성공 반환

    Example:
        ```python
        success = await delete_tip(db, existing_tip)
        if success:
            print("Tip deleted successfully")
        ```
    """
    try:
        # Soft delete: is_active를 False로 설정
        tip.is_active = False
        await db.flush()

        logger.info(f"Soft deleted tip: {tip.id}")
        return True

    except Exception as e:
        logger.error(
            f"Error deleting tip {tip.id}: {str(e)}",
            exc_info=True,
        )
        raise


async def increment_view_count(db: AsyncSession, tip: Tip) -> Tip:
    """
    조회수 1 증가

    Args:
        db: 데이터베이스 세션
        tip: 팁 엔티티

    Returns:
        Tip: 조회수가 증가된 팁

    Example:
        ```python
        tip = await increment_view_count(db, existing_tip)
        print(f"View count: {tip.view_count}")
        ```
    """
    try:
        # 조회수 1 증가
        tip.view_count += 1
        await db.flush()
        await db.refresh(tip)

        logger.info(f"Incremented view count for tip {tip.id}: {tip.view_count}")
        return tip

    except Exception as e:
        logger.error(
            f"Error incrementing view count for tip {tip.id}: {str(e)}",
            exc_info=True,
        )
        raise
