"""
Tip 캐시 관리 모듈

Tip 관련 캐시 무효화 전략을 담당합니다.
"""

import logging
from datetime import date
from typing import Optional

from app.core.cache import CacheService

# 로거 인스턴스
logger = logging.getLogger(__name__)


async def invalidate_tip_cache(
    tip_id: str,
    publish_date: date,
    cache: Optional[CacheService] = None,
) -> None:
    """
    팁 관련 캐시 무효화 (관리자가 팁 수정/삭제 시 사용)

    팁이 수정되거나 삭제될 때 관련된 모든 캐시를 삭제합니다.

    Args:
        tip_id: 팁 ID
        publish_date: 팁 게시 날짜
        cache: Redis 캐시 서비스 (선택적)

    Example:
        ```python
        await invalidate_tip_cache("tip_01JCAW...", date(2024, 1, 1), cache)
        ```
    """
    if not cache:
        logger.info("캐시 서비스가 없어 무효화를 건너뜁니다")
        return

    try:
        # 1. 상세 캐시 삭제
        detail_key = f"tip:detail:{tip_id}"
        await cache.delete(detail_key)

        # 2. 일일 팁 캐시 삭제
        daily_key = f"tip:daily:{publish_date}"
        await cache.delete(daily_key)

        # 3. 목록 캐시 전체 삭제 (패턴 매칭)
        deleted_count = await cache.clear_pattern("tips:list:*")

        logger.info(
            f"캐시 무효화 완료 for tip: {tip_id} "
            f"(상세, 일일, 목록 {deleted_count}개)"
        )

    except Exception as e:
        logger.warning(
            f"캐시 무효화 실패 (계속 진행): {str(e)}",
            exc_info=True,
        )
