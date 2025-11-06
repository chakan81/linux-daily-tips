"""
Tip 조회 작업 모듈

Tip 엔티티의 다양한 조회 로직을 담당합니다.
캐싱 전략을 지원하여 성능을 최적화합니다.
"""

import logging
from datetime import date
from typing import Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import CacheService
from app.core.exceptions import AppException
from app.models.tip import DifficultyLevel, Tip
from app.schemas.tip import Tip as TipSchema

# 로거 인스턴스
logger = logging.getLogger(__name__)


async def get_daily_tip(
    db: AsyncSession,
    target_date: date,
    cache: Optional[CacheService] = None,
) -> Tip | None:
    """
    가장 최근의 활성화된 팁 조회 (캐싱 적용)

    날짜 기반이 아니라 publish_date가 오늘 이전인 팁 중 가장 최근 팁을 반환합니다.
    이렇게 하면 팁 업데이트를 건너뛰어도 항상 최신 팁을 보여줄 수 있습니다.

    캐싱 전략:
    - Key: "tip:daily:{YYYY-MM-DD}"
    - TTL: 3600초 (1시간)
    - 이유: 하루에 여러 번 팁이 추가될 수 있으므로 짧은 TTL

    Args:
        db: 데이터베이스 세션
        target_date: 기준 날짜 (이 날짜 이전의 가장 최근 팁 반환)
        cache: Redis 캐시 서비스 (선택적)

    Returns:
        Tip | None: 가장 최근의 팁 또는 None (팁이 없는 경우)

    Example:
        ```python
        tip = await get_daily_tip(db, date.today(), cache)
        if tip:
            print(f"Latest tip: {tip.title}")
        ```
    """
    try:
        # 1. 캐시 확인 (캐시 서비스가 있는 경우만)
        cache_key = f"tip:daily:{target_date}"
        if cache:
            cached_tip = await cache.get(cache_key)
            if cached_tip:
                logger.info(f"캐시 HIT for daily tip: {cache_key}")
                return Tip(**cached_tip)
            logger.info(f"캐시 MISS for daily tip: {cache_key}")

        # 2. 캐시 MISS 또는 캐시 비활성 → DB 조회
        # publish_date가 target_date 이하인 팁 중 가장 최근 것
        stmt = (
            select(Tip)
            .where(
                and_(
                    Tip.publish_date <= target_date,
                    Tip.is_active == True  # noqa: E712
                )
            )
            .order_by(Tip.publish_date.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        tip = result.scalar_one_or_none()

        if tip:
            logger.info(f"Retrieved latest tip (publish_date: {tip.publish_date}): {tip.id}")
            # 3. 캐싱 (1시간 TTL - 짧게 설정하여 새 팁이 추가되면 빠르게 반영)
            if cache:
                tip_dict = TipSchema.model_validate(tip).model_dump(mode='json')
                await cache.set(cache_key, tip_dict, ttl=3600)
        else:
            logger.info(f"No active tip found before {target_date}")

        return tip

    except Exception as e:
        logger.error(
            f"Error retrieving daily tip for {target_date}: {str(e)}",
            exc_info=True,
        )
        raise


async def get_tip_by_id(
    db: AsyncSession,
    tip_id: str,
    cache: Optional[CacheService] = None,
) -> Tip:
    """
    ID로 팁 조회 (캐싱 적용)

    캐싱 전략:
    - Key: "tip:detail:{tip_id}"
    - TTL: 3600초 (1시간)
    - 이유: 관리자가 수정할 수 있어 짧은 TTL

    Args:
        db: 데이터베이스 세션
        tip_id: 팁 ID (tip_01JCAW0V1QQ9KZ2F3XHBP8TGNY)
        cache: Redis 캐시 서비스 (선택적)

    Returns:
        Tip: 조회된 팁

    Raises:
        AppException: 팁이 존재하지 않는 경우 (404)

    Example:
        ```python
        try:
            tip = await get_tip_by_id(db, "tip_01JCAW0V1QQ9KZ2F3XHBP8TGNY", cache)
        except AppException as e:
            print(f"Tip not found: {e.detail}")
        ```
    """
    try:
        # 1. 캐시 확인
        cache_key = f"tip:detail:{tip_id}"
        if cache:
            cached_tip = await cache.get(cache_key)
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
        if cache:
            tip_dict = TipSchema.model_validate(tip).model_dump(mode='json')
            await cache.set(cache_key, tip_dict, ttl=3600)

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
    db: AsyncSession,
    skip: int = 0,
    limit: int = 10,
    difficulty: DifficultyLevel | None = None,
    category: str | None = None,
    search_query: str | None = None,
    sort_by: str = "publish_date",
    order: str = "desc",
    cache: Optional[CacheService] = None,
) -> tuple[list[Tip], int]:
    """
    필터링 및 페이지네이션된 팁 목록 조회 (캐싱 적용)

    캐싱 전략:
    - Key: "tips:list:page-{page}:size-{limit}:diff-{difficulty}:cat-{category}:q-{search}:sort-{sort_by}:{order}"
    - TTL: 600초 (10분)
    - 이유: 새 팁 추가 시 빠른 반영

    Args:
        db: 데이터베이스 세션
        skip: 건너뛸 개수 (페이지네이션)
        limit: 조회할 최대 개수
        difficulty: 난이도 필터 (beginner/intermediate/advanced)
        category: 카테고리 필터 (예: "file-system")
        search_query: 검색 쿼리 (제목 또는 내용에서 검색, 대소문자 무시)
        sort_by: 정렬 필드 (publish_date 또는 title, 기본값: publish_date)
        order: 정렬 순서 (asc 또는 desc, 기본값: desc)
        cache: Redis 캐시 서비스 (선택적)

    Returns:
        tuple[list[Tip], int]: (팁 목록, 전체 개수)

    Example:
        ```python
        # 초급 난이도만 조회 (페이지 1, 10개)
        tips, total = await get_tips(
            db, skip=0, limit=10, difficulty="beginner", cache=cache
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
        search_str = search_query or "none"
        cache_key = f"tips:list:page-{page}:size-{limit}:diff-{diff_str}:cat-{cat_str}:q-{search_str}:sort-{sort_by}:{order}"

        # 2. 캐시 확인
        if cache:
            cached_result = await cache.get(cache_key)
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

        # 검색 쿼리 (제목 또는 내용에서 검색, 대소문자 무시)
        if search_query:
            from sqlalchemy import or_
            search_pattern = f"%{search_query}%"
            conditions.append(
                or_(
                    Tip.title.ilike(search_pattern),
                    Tip.content.ilike(search_pattern),
                )
            )

        # WHERE 절 구성
        if conditions:
            stmt = select(Tip).where(and_(*conditions))
            count_stmt = select(func.count()).select_from(Tip).where(and_(*conditions))
        else:
            stmt = select(Tip)
            count_stmt = select(func.count()).select_from(Tip)

        # 정렬 적용 (보안: 허용된 필드만)
        ALLOWED_SORT_FIELDS = {"publish_date", "title"}
        if sort_by in ALLOWED_SORT_FIELDS:
            sort_column = getattr(Tip, sort_by)
            if order == "asc":
                stmt = stmt.order_by(sort_column.asc())
            else:
                stmt = stmt.order_by(sort_column.desc())
        else:
            # 잘못된 필드 시 기본 정렬 (publish_date desc)
            logger.warning(f"Invalid sort_by field: {sort_by}, using default (publish_date desc)")
            stmt = stmt.order_by(Tip.publish_date.desc())

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
            f"difficulty: {difficulty}, category: {category}, "
            f"search_query: {search_query}, sort_by: {sort_by}, order: {order})"
        )

        # 4. 캐싱 (10분 TTL)
        if cache:
            cache_data = {
                "tips": [TipSchema.model_validate(t).model_dump(mode='json') for t in tips],
                "total": total_count,
            }
            await cache.set(cache_key, cache_data, ttl=600)

        return tips, total_count

    except Exception as e:
        logger.error(
            f"Error retrieving tips: {str(e)}",
            exc_info=True,
        )
        raise
