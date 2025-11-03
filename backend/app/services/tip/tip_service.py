"""
Tip 비즈니스 로직 서비스 (조율 레이어)

일일 Linux 팁 CRUD 및 비즈니스 로직을 조율합니다.
- 날짜별 팁 조회
- 팁 목록 필터링 (난이도, 카테고리)
- 팁 생성/수정/삭제 (soft delete)
- 조회수 증가
- Redis 캐싱 (Day 14)
"""

from datetime import date
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import CacheService
from app.models.tip import DifficultyLevel, Tip
from app.schemas.tip import TipCreate, TipUpdate
from app.services.tip import tip_cache, tip_crud, tip_query


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

        Args:
            db: 데이터베이스 세션
            target_date: 조회할 날짜

        Returns:
            Tip | None: 해당 날짜의 팁 또는 None (팁이 없는 경우)
        """
        return await tip_query.get_daily_tip(db, target_date, self.cache)

    async def get_tip_by_id(self, db: AsyncSession, tip_id: str) -> Tip:
        """
        ID로 팁 조회 (캐싱 적용)

        Args:
            db: 데이터베이스 세션
            tip_id: 팁 ID (tip_01JCAW0V1QQ9KZ2F3XHBP8TGNY)

        Returns:
            Tip: 조회된 팁

        Raises:
            AppException: 팁이 존재하지 않는 경우 (404)
        """
        return await tip_query.get_tip_by_id(db, tip_id, self.cache)

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

        Args:
            db: 데이터베이스 세션
            skip: 건너뛸 개수 (페이지네이션)
            limit: 조회할 최대 개수
            difficulty: 난이도 필터 (beginner/intermediate/advanced)
            category: 카테고리 필터 (예: "file-system")

        Returns:
            tuple[list[Tip], int]: (팁 목록, 전체 개수)
        """
        return await tip_query.get_tips(
            db, skip, limit, difficulty, category, self.cache
        )

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
        """
        # publish_date가 None이면 오늘 날짜로 설정
        publish_date = tip_data.publish_date or date.today()

        # 중복 날짜 체크 (비즈니스 규칙: 하루에 하나의 팁만)
        existing_tip = await self.get_daily_tip(db, publish_date)

        # CRUD 실행
        return await tip_crud.create_tip(db, tip_data, existing_tip)

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
        """
        # 팁 존재 여부 확인
        tip = await self.get_tip_by_id(db, tip_id)

        # CRUD 실행
        updated_tip = await tip_crud.update_tip(db, tip, tip_data)

        # 캐시 무효화 (stale 데이터 방지)
        await self.invalidate_tip_cache(tip_id, updated_tip.publish_date)

        return updated_tip

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
        """
        # 팁 존재 여부 확인 (없으면 AppException 404)
        tip = await self.get_tip_by_id(db, tip_id)

        # CRUD 실행
        result = await tip_crud.delete_tip(db, tip)

        # 캐시 무효화 (삭제된 팁이 캐시에서 계속 조회되는 것 방지)
        await self.invalidate_tip_cache(tip_id, tip.publish_date)

        return result

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
        """
        # 팁 존재 여부 확인
        tip = await self.get_tip_by_id(db, tip_id)

        # CRUD 실행
        updated_tip = await tip_crud.increment_view_count(db, tip)

        # 캐시 무효화 (조회수 변경 반영)
        await self.invalidate_tip_cache(tip_id, updated_tip.publish_date)

        return updated_tip

    async def invalidate_tip_cache(self, tip_id: str, publish_date: date) -> None:
        """
        팁 관련 캐시 무효화 (관리자가 팁 수정/삭제 시 사용)

        Args:
            tip_id: 팁 ID
            publish_date: 팁 게시 날짜
        """
        await tip_cache.invalidate_tip_cache(tip_id, publish_date, self.cache)
