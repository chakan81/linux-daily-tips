"""
Tip 비즈니스 로직 서비스

일일 Linux 팁 CRUD 및 비즈니스 로직을 처리합니다.
- 날짜별 팁 조회
- 팁 목록 필터링 (난이도, 카테고리)
- 팁 생성/수정/삭제 (soft delete)
- 조회수 증가
"""

import logging
from datetime import date

from sqlalchemy import and_, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.models.tip import DifficultyLevel, Tip
from app.schemas.tip import TipCreate, TipUpdate

# 로거 인스턴스
logger = logging.getLogger(__name__)


class TipService:
    """
    Tip 비즈니스 로직 서비스 계층

    데이터베이스 접근 및 비즈니스 규칙을 처리합니다.
    모든 메서드는 정적 메서드로 구현되어 있습니다.
    """

    @staticmethod
    async def get_daily_tip(db: AsyncSession, target_date: date) -> Tip | None:
        """
        특정 날짜의 활성화된 팁 조회

        Args:
            db: 데이터베이스 세션
            target_date: 조회할 날짜

        Returns:
            Tip | None: 해당 날짜의 팁 또는 None (팁이 없는 경우)

        Example:
            ```python
            tip = await TipService.get_daily_tip(db, date.today())
            if tip:
                print(f"Today's tip: {tip.title}")
            ```
        """
        try:
            # publish_date == target_date AND is_active = True
            stmt = select(Tip).where(
                and_(Tip.publish_date == target_date, Tip.is_active == True)  # noqa: E712
            )
            result = await db.execute(stmt)
            tip = result.scalar_one_or_none()

            if tip:
                logger.info(f"Retrieved daily tip for {target_date}: {tip.id}")
            else:
                logger.info(f"No active tip found for {target_date}")

            return tip

        except Exception as e:
            logger.error(
                f"Error retrieving daily tip for {target_date}: {str(e)}",
                exc_info=True,
            )
            raise

    @staticmethod
    async def get_tip_by_id(db: AsyncSession, tip_id: str) -> Tip:
        """
        ID로 팁 조회

        Args:
            db: 데이터베이스 세션
            tip_id: 팁 ID (tip_01JCAW0V1QQ9KZ2F3XHBP8TGNY)

        Returns:
            Tip: 조회된 팁

        Raises:
            AppException: 팁이 존재하지 않는 경우 (404)

        Example:
            ```python
            try:
                tip = await TipService.get_tip_by_id(db, "tip_01JCAW0V1QQ9KZ2F3XHBP8TGNY")
            except AppException as e:
                print(f"Tip not found: {e.detail}")
            ```
        """
        try:
            stmt = select(Tip).where(Tip.id == tip_id)
            result = await db.execute(stmt)
            tip = result.scalar_one_or_none()

            if not tip:
                logger.warning(f"Tip not found: {tip_id}")
                raise AppException(status_code=404, detail="Tip not found")

            logger.info(f"Retrieved tip: {tip.id}")
            return tip

        except AppException:
            raise
        except Exception as e:
            logger.error(
                f"Error retrieving tip {tip_id}: {str(e)}",
                exc_info=True,
            )
            raise

    @staticmethod
    async def get_tips(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10,
        difficulty: DifficultyLevel | None = None,
        category: str | None = None,
    ) -> tuple[list[Tip], int]:
        """
        필터링 및 페이지네이션된 팁 목록 조회

        Args:
            db: 데이터베이스 세션
            skip: 건너뛸 개수 (페이지네이션)
            limit: 조회할 최대 개수
            difficulty: 난이도 필터 (beginner/intermediate/advanced)
            category: 카테고리 필터 (예: "file-system")

        Returns:
            tuple[list[Tip], int]: (팁 목록, 전체 개수)

        Example:
            ```python
            # 초급 난이도만 조회 (페이지 1, 10개)
            tips, total = await TipService.get_tips(
                db, skip=0, limit=10, difficulty="beginner"
            )
            print(f"Found {total} beginner tips, showing first {len(tips)}")
            ```
        """
        try:
            # 기본 쿼리
            conditions = []

            # 난이도 필터
            if difficulty:
                conditions.append(Tip.difficulty == difficulty)

            # 카테고리 필터 (JSONB 배열 내 포함 여부)
            if category:
                # PostgreSQL JSONB contains operator (@>)
                conditions.append(Tip.category.contains([category]))

            # WHERE 절 구성
            if conditions:
                stmt = select(Tip).where(and_(*conditions))
                count_stmt = select(func.count()).select_from(Tip).where(and_(*conditions))
            else:
                stmt = select(Tip)
                count_stmt = select(func.count()).select_from(Tip)

            # 페이지네이션 적용
            stmt = stmt.offset(skip).limit(limit)

            # 팁 목록 조회
            result = await db.execute(stmt)
            tips = list(result.scalars().all())

            # 전체 개수 조회
            count_result = await db.execute(count_stmt)
            total_count = count_result.scalar() or 0

            logger.info(
                f"Retrieved {len(tips)} tips (total: {total_count}, "
                f"skip: {skip}, limit: {limit}, "
                f"difficulty: {difficulty}, category: {category})"
            )

            return tips, total_count

        except Exception as e:
            logger.error(
                f"Error retrieving tips: {str(e)}",
                exc_info=True,
            )
            raise

    @staticmethod
    async def create_tip(db: AsyncSession, tip_data: TipCreate) -> Tip:
        """
        새 팁 생성

        Args:
            db: 데이터베이스 세션
            tip_data: 팁 생성 데이터

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
            tip = await TipService.create_tip(db, tip_data)
            ```
        """
        try:
            # publish_date가 None이면 오늘 날짜로 설정
            publish_date = tip_data.publish_date or date.today()

            # 중복 날짜 체크 (비즈니스 규칙: 하루에 하나의 팁만)
            existing_tip = await TipService.get_daily_tip(db, publish_date)
            if existing_tip:
                logger.warning(
                    f"Tip already exists for date {publish_date}: {existing_tip.id}"
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

    @staticmethod
    async def update_tip(
        db: AsyncSession, tip_id: str, tip_data: TipUpdate
    ) -> Tip:
        """
        팁 수정 (부분 업데이트)

        Args:
            db: 데이터베이스 세션
            tip_id: 수정할 팁 ID
            tip_data: 수정할 데이터 (None이 아닌 필드만 업데이트)

        Returns:
            Tip: 수정된 팁

        Raises:
            AppException: 팁이 존재하지 않는 경우 (404)

        Example:
            ```python
            update_data = TipUpdate(title="새로운 제목", difficulty="advanced")
            tip = await TipService.update_tip(db, "tip_01JCAW...", update_data)
            ```
        """
        try:
            # 팁 존재 여부 확인
            tip = await TipService.get_tip_by_id(db, tip_id)

            # 업데이트할 필드만 추출 (None이 아닌 필드만)
            update_data = tip_data.model_dump(exclude_unset=True)

            if not update_data:
                logger.info(f"No fields to update for tip {tip_id}")
                return tip

            # 각 필드 업데이트
            for field, value in update_data.items():
                setattr(tip, field, value)

            await db.flush()
            await db.refresh(tip)

            logger.info(f"Updated tip {tip_id}: {list(update_data.keys())}")
            return tip

        except AppException:
            raise
        except Exception as e:
            logger.error(
                f"Error updating tip {tip_id}: {str(e)}",
                exc_info=True,
            )
            raise

    @staticmethod
    async def delete_tip(db: AsyncSession, tip_id: str) -> bool:
        """
        팁 삭제 (soft delete: is_active=False)

        Args:
            db: 데이터베이스 세션
            tip_id: 삭제할 팁 ID

        Returns:
            bool: 항상 True (성공)

        Raises:
            AppException: 팁이 존재하지 않는 경우 (404)

        Note:
            멱등성 보장: 이미 삭제된 팁도 성공 반환

        Example:
            ```python
            success = await TipService.delete_tip(db, "tip_01JCAW...")
            if success:
                print("Tip deleted successfully")
            ```
        """
        try:
            # 팁 존재 여부 확인 (없으면 AppException 404)
            tip = await TipService.get_tip_by_id(db, tip_id)

            # Soft delete: is_active를 False로 설정
            tip.is_active = False
            await db.flush()

            logger.info(f"Soft deleted tip: {tip_id}")
            return True

        except AppException:
            raise
        except Exception as e:
            logger.error(
                f"Error deleting tip {tip_id}: {str(e)}",
                exc_info=True,
            )
            raise

    @staticmethod
    async def increment_view_count(db: AsyncSession, tip_id: str) -> Tip:
        """
        조회수 1 증가

        Args:
            db: 데이터베이스 세션
            tip_id: 팁 ID

        Returns:
            Tip: 조회수가 증가된 팁

        Raises:
            AppException: 팁이 존재하지 않는 경우 (404)

        Example:
            ```python
            tip = await TipService.increment_view_count(db, "tip_01JCAW...")
            print(f"View count: {tip.view_count}")
            ```
        """
        try:
            # 팁 존재 여부 확인
            tip = await TipService.get_tip_by_id(db, tip_id)

            # 조회수 1 증가
            tip.view_count += 1
            await db.flush()
            await db.refresh(tip)

            logger.info(f"Incremented view count for tip {tip_id}: {tip.view_count}")
            return tip

        except AppException:
            raise
        except Exception as e:
            logger.error(
                f"Error incrementing view count for tip {tip_id}: {str(e)}",
                exc_info=True,
            )
            raise
