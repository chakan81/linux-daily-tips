"""
OAuth State Parameter 검증기

CSRF 공격을 방어하기 위한 OAuth state 파라미터 저장 및 검증을 담당합니다.
"""

import logging

from app.core.cache import CacheService
from app.core.exceptions import AppException

# 로거 인스턴스
logger = logging.getLogger(__name__)


__all__ = ["OAuthStateValidator"]


class OAuthStateValidator:
    """
    OAuth State Parameter 검증기

    주요 기능:
    - OAuth state 저장 (Redis)
    - OAuth state 검증 (CSRF 방어)

    Attributes:
        cache: Redis 캐시 서비스
    """

    def __init__(self, cache: CacheService):
        """
        OAuthStateValidator 초기화

        Args:
            cache: Redis 캐시 서비스
        """
        self.cache = cache

    async def save_oauth_state(self, state: str, ttl: int = 600) -> None:
        """
        OAuth State Parameter를 Redis에 저장 (CSRF 방어)

        OAuth 로그인 시작 시 생성한 state를 Redis에 저장합니다.
        콜백에서 동일한 state가 반환되는지 검증하여 CSRF 공격을 방어합니다.

        Args:
            state: CSRF 방어용 랜덤 state 문자열
            ttl: 만료 시간 (초, 기본값: 600 = 10분)

        Example:
            >>> validator = OAuthStateValidator(cache)
            >>> state = secrets.token_urlsafe(32)
            >>> await validator.save_oauth_state(state, ttl=600)
        """
        try:
            state_key = f"oauth_state:{state}"
            assert self.cache.redis_client is not None, "Redis client not connected"
            await self.cache.redis_client.setex(
                state_key,
                ttl,
                "valid",  # 단순히 존재 여부만 확인
            )

            logger.debug(
                f"OAuth state 저장: {state_key}",
                extra={
                    "ttl": ttl,
                },
            )

        except Exception as e:
            logger.error(
                f"OAuth state 저장 실패: {str(e)}",
                exc_info=True,
            )
            raise AppException(
                status_code=503,
                detail="OAuth state 저장에 실패했습니다",
            )

    async def verify_oauth_state(self, state: str) -> bool:
        """
        OAuth State Parameter 검증 (CSRF 방어)

        콜백에서 받은 state가 이전에 저장한 state와 일치하는지 확인합니다.
        검증 후 state는 Redis에서 삭제하여 재사용을 방지합니다.

        Args:
            state: 검증할 state 문자열

        Returns:
            bool: state가 유효하면 True, 그렇지 않으면 False

        Example:
            >>> validator = OAuthStateValidator(cache)
            >>> is_valid = await validator.verify_oauth_state(state)
            >>> if not is_valid:
            >>>     raise HTTPException(400, "Invalid OAuth state")
        """
        try:
            state_key = f"oauth_state:{state}"
            assert self.cache.redis_client is not None, "Redis client not connected"
            state_value = await self.cache.redis_client.get(state_key)

            if not state_value:
                logger.warning(
                    f"OAuth state 검증 실패: 존재하지 않거나 만료됨",
                    extra={
                        "state_key": state_key,
                    },
                )
                return False

            # State 사용 후 즉시 삭제 (재사용 방지)
            await self.cache.redis_client.delete(state_key)

            logger.debug(
                f"OAuth state 검증 성공: {state_key}",
            )

            return True

        except Exception as e:
            logger.error(
                f"OAuth state 검증 중 오류: {str(e)}",
                exc_info=True,
            )
            return False
