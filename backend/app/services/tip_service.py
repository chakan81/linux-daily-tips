"""
Tip 비즈니스 로직 서비스

일일 Linux 팁 CRUD 및 비즈니스 로직을 처리합니다.
- 날짜별 팁 조회
- 팁 목록 필터링 (난이도, 카테고리)
- 팁 생성/수정/삭제 (soft delete)
- 조회수 증가
- Redis 캐싱 (Day 14)
"""

import logging
from datetime import date
from typing import Optional

from sqlalchemy import and_, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import CacheService
from app.core.exceptions import AppException
from app.models.tip import DifficultyLevel, Tip
from app.schemas.tip import TipCreate, TipUpdate

# 로거 인스턴스
logger = logging.getLogger(__name__)


class TipService:
    """
    Tip 비즈니스 로직 서비스 계층

    데이터베이스 접근 및 비즈니스 규칙을 처리합니다.
    Redis 캐싱을 통한 성능 최적화를 지원합니다.

    Attributes:
        cache: Redis 캐시 서비스 (선택적, None이면 캐싱 비활성화)
    """

    def __init__(self, cache: Optional[CacheService] = None) -> None:
        """
        TipService 초기화

        Args:
            cache: Redis 캐시 서비스 (선택적)
        """
        self.cache = cache

    async def get_daily_tip(self, db: AsyncSession, target_date: date) -> Tip | None:
        """
        특정 날짜의 활성화된 팁 조회 (캐싱 적용)

        캐싱 전략:
        - Key: "tip:daily:{YYYY-MM-DD}"
        - TTL: 86400초 (24시간)
        - 이유: 일일 팁은 하루에 한 번만 바뀜

        Args:
            db: 데이터베이스 세션
            target_date: 조회할 날짜

        Returns:
            Tip | None: 해당 날짜의 팁 또는 None (팁이 없는 경우)

        Example:
            ```python
            service = TipService(cache)
            tip = await service.get_daily_tip(db, date.today())
            if tip:
                print(f"Today's tip: {tip.title}")
            ```
        """
        try:
            # 1. 캐시 확인 (캐시 서비스가 있는 경우만)
            cache_key = f"tip:daily:{target_date}"
            if self.cache:
                cached_tip = await self.cache.get(cache_key)
                if cached_tip:
                    logger.info(f"캐시 HIT for daily tip: {cache_key}")
                    return Tip(**cached_tip)
                logger.info(f"캐시 MISS for daily tip: {cache_key}")

            # 2. 캐시 MISS 또는 캐시 비활성 → DB 조회
            stmt = select(Tip).where(
                and_(Tip.publish_date == target_date, Tip.is_active == True)  # noqa: E712
            )
            result = await db.execute(stmt)
            tip = result.scalar_one_or_none()

            if tip:
                logger.info(f"Retrieved daily tip for {target_date}: {tip.id}")
                # 3. 캐싱 (24시간 TTL)
                if self.cache:
                    # Pydantic V2: model_dump() 사용
                    tip_dict = {
                        "id": tip.id,
                        "title": tip.title,
                        "content": tip.content,
                        "difficulty": tip.difficulty.value,
                        "category": tip.category,
                        "publish_date": tip.publish_date.isoformat(),
                        "view_count": tip.view_count,
                        "is_active": tip.is_active,
                        "terminal_setup": tip.terminal_setup,
                        "created_at": tip.created_at.isoformat(),
                        "updated_at": tip.updated_at.isoformat(),
                    }
                    await self.cache.set(cache_key, tip_dict, ttl=86400)
            else:
                logger.info(f"No active tip found for {target_date}")

            return tip

        except Exception as e:
            logger.error(
                f"Error retrieving daily tip for {target_date}: {str(e)}",
                exc_info=True,
            )
            raise

    async def get_tip_by_id(self, db: AsyncSession, tip_id: str) -> Tip:
        """
        ID로 팁 조회 (캐싱 적용)

        캐싱 전략:
        - Key: "tip:detail:{tip_id}"
        - TTL: 3600초 (1시간)
        - 이유: 관리자가 수정할 수 있어 짧은 TTL

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
                service = TipService(cache)
                tip = await service.get_tip_by_id(db, "tip_01JCAW0V1QQ9KZ2F3XHBP8TGNY")
            except AppException as e:
                print(f"Tip not found: {e.detail}")
            ```
        """
        try:
            # 1. 캐시 확인
            cache_key = f"tip:detail:{tip_id}"
            if self.cache:
                cached_tip = await self.cache.get(cache_key)
                if cached_tip:
                    logger.info(f"캐시 HIT for tip detail: {cache_key}")
                    return Tip(**cached_tip)
                logger.info(f"캐시 MISS for tip detail: {cache_key}")

            # 2. 캐시 MISS 또는 캐시 비활성 → DB 조회
            stmt = select(Tip).where(Tip.id == tip_id)
            result = await db.execute(stmt)
            tip = result.scalar_one_or_none()

            if not tip:
                logger.warning(f"Tip not found: {tip_id}")
                raise AppException(status_code=404, detail="Tip not found")

            logger.info(f"Retrieved tip: {tip.id}")

            # 3. 캐싱 (1시간 TTL)
            if self.cache:
                tip_dict = {
                    "id": tip.id,
                    "title": tip.title,
                    "content": tip.content,
                    "difficulty": tip.difficulty.value,
                    "category": tip.category,
                    "publish_date": tip.publish_date.isoformat(),
                    "view_count": tip.view_count,
                    "is_active": tip.is_active,
                    "terminal_setup": tip.terminal_setup,
                    "created_at": tip.created_at.isoformat(),
                    "updated_at": tip.updated_at.isoformat(),
                }
                await self.cache.set(cache_key, tip_dict, ttl=3600)

            return tip

        except AppException:
            raise
        except Exception as e:
            logger.error(
                f"Error retrieving tip {tip_id}: {str(e)}",
                exc_info=True,
            )
            raise

    async def get_tips(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10,
        difficulty: DifficultyLevel | None = None,
        category: str | None = None,
    ) -> tuple[list[Tip], int]:
        """
        필터링 및 페이지네이션된 팁 목록 조회 (캐싱 적용)

        캐싱 전략:
        - Key: "tips:list:page-{page}:size-{limit}:diff-{difficulty}:cat-{category}"
        - TTL: 600초 (10분)
        - 이유: 새 팁 추가 시 빠른 반영

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
            service = TipService(cache)
            tips, total = await service.get_tips(
                db, skip=0, limit=10, difficulty="beginner"
            )
            print(f"Found {total} beginner tips, showing first {len(tips)}")
            ```
        """
        try:
            # 1. 캐시 키 생성
            page = (skip // limit) + 1
            # difficulty가 문자열이거나 Enum일 수 있음
            if difficulty:
                diff_str = difficulty.value if isinstance(difficulty, DifficultyLevel) else difficulty
            else:
                diff_str = "all"
            cat_str = category or "all"
            cache_key = f"tips:list:page-{page}:size-{limit}:diff-{diff_str}:cat-{cat_str}"

            # 2. 캐시 확인
            if self.cache:
                cached_result = await self.cache.get(cache_key)
                if cached_result:
                    logger.info(f"캐시 HIT for tips list: {cache_key}")
                    tips = [Tip(**t) for t in cached_result["tips"]]
                    total = cached_result["total"]
                    return tips, total
                logger.info(f"캐시 MISS for tips list: {cache_key}")

            # 3. 캐시 MISS 또는 캐시 비활성 → DB 조회
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

            # 4. 캐싱 (10분 TTL)
            if self.cache:
                cache_data = {
                    "tips": [
                        {
                            "id": t.id,
                            "title": t.title,
                            "content": t.content,
                            "difficulty": t.difficulty.value,
                            "category": t.category,
                            "publish_date": t.publish_date.isoformat(),
                            "view_count": t.view_count,
                            "is_active": t.is_active,
                            "terminal_setup": t.terminal_setup,
                            "created_at": t.created_at.isoformat(),
                            "updated_at": t.updated_at.isoformat(),
                        }
                        for t in tips
                    ],
                    "total": total_count,
                }
                await self.cache.set(cache_key, cache_data, ttl=600)

            return tips, total_count

        except Exception as e:
            logger.error(
                f"Error retrieving tips: {str(e)}",
                exc_info=True,
            )
            raise

    async def create_tip(self, db: AsyncSession, tip_data: TipCreate) -> Tip:
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
            service = TipService(cache)
            tip_data = TipCreate(
                title="파일 검색하기",
                content="find 명령어 사용법...",
                difficulty=DifficultyLevel.BEGINNER,
            )
            tip = await service.create_tip(db, tip_data)
            ```
        """
        try:
            # publish_date가 None이면 오늘 날짜로 설정
            publish_date = tip_data.publish_date or date.today()

            # 중복 날짜 체크 (비즈니스 규칙: 하루에 하나의 팁만)
            existing_tip = await self.get_daily_tip(db, publish_date)
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

    async def update_tip(
        self, db: AsyncSession, tip_id: str, tip_data: TipUpdate
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
            service = TipService(cache)
            update_data = TipUpdate(title="새로운 제목", difficulty="advanced")
            tip = await service.update_tip(db, "tip_01JCAW...", update_data)
            ```
        """
        try:
            # 팁 존재 여부 확인
            tip = await self.get_tip_by_id(db, tip_id)

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

            # 캐시 무효화 (stale 데이터 방지)
            await self.invalidate_tip_cache(tip_id, tip.publish_date)

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

    async def delete_tip(self, db: AsyncSession, tip_id: str) -> bool:
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
            service = TipService(cache)
            success = await service.delete_tip(db, "tip_01JCAW...")
            if success:
                print("Tip deleted successfully")
            ```
        """
        try:
            # 팁 존재 여부 확인 (없으면 AppException 404)
            tip = await self.get_tip_by_id(db, tip_id)

            # Soft delete: is_active를 False로 설정
            tip.is_active = False
            await db.flush()

            # 캐시 무효화 (삭제된 팁이 캐시에서 계속 조회되는 것 방지)
            await self.invalidate_tip_cache(tip_id, tip.publish_date)

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

    async def increment_view_count(self, db: AsyncSession, tip_id: str) -> Tip:
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
            service = TipService(cache)
            tip = await service.increment_view_count(db, "tip_01JCAW...")
            print(f"View count: {tip.view_count}")
            ```
        """
        try:
            # 팁 존재 여부 확인
            tip = await self.get_tip_by_id(db, tip_id)

            # 조회수 1 증가
            tip.view_count += 1
            await db.flush()
            await db.refresh(tip)

            # 캐시 무효화 (조회수 변경 반영)
            await self.invalidate_tip_cache(tip_id, tip.publish_date)

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

    async def invalidate_tip_cache(self, tip_id: str, publish_date: date) -> None:
        """
        팁 관련 캐시 무효화 (관리자가 팁 수정/삭제 시 사용)

        팁이 수정되거나 삭제될 때 관련된 모든 캐시를 삭제합니다.

        Args:
            tip_id: 팁 ID
            publish_date: 팁 게시 날짜

        Example:
            ```python
            service = TipService(cache)
            await service.invalidate_tip_cache("tip_01JCAW...", date(2024, 1, 1))
            ```
        """
        if not self.cache:
            logger.info("캐시 서비스가 없어 무효화를 건너뜁니다")
            return

        try:
            # 1. 상세 캐시 삭제
            detail_key = f"tip:detail:{tip_id}"
            await self.cache.delete(detail_key)

            # 2. 일일 팁 캐시 삭제
            daily_key = f"tip:daily:{publish_date}"
            await self.cache.delete(daily_key)

            # 3. 목록 캐시 전체 삭제 (패턴 매칭)
            deleted_count = await self.cache.clear_pattern("tips:list:*")

            logger.info(
                f"캐시 무효화 완료 for tip: {tip_id} "
                f"(상세, 일일, 목록 {deleted_count}개)"
            )

        except Exception as e:
            logger.warning(
                f"캐시 무효화 실패 (계속 진행): {str(e)}",
                exc_info=True,
            )
