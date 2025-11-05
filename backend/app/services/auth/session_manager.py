"""
Redis 세션 관리자

Redis를 사용한 사용자 세션 생성, 조회, 무효화를 담당합니다.
세션 데이터는 암호화되어 Redis에 저장됩니다.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Optional

from app.core.cache import CacheService
from app.core.encryption import EncryptionService
from app.core.exceptions import AppException
from app.core.types import SessionData

# 로거 인스턴스
logger = logging.getLogger(__name__)


__all__ = ["SessionManager"]


class SessionManager:
    """
    Redis 세션 관리자

    주요 기능:
    - 세션 생성 (이메일 암호화)
    - 세션 조회 (이메일 복호화)
    - 세션 무효화 (로그아웃)

    Attributes:
        cache: Redis 캐시 서비스
        encryption: 암호화 서비스 (이메일 암호화/복호화)
    """

    def __init__(
        self,
        cache: CacheService,
        encryption: Optional[EncryptionService] = None,
    ):
        """
        SessionManager 초기화

        Args:
            cache: Redis 캐시 서비스
            encryption: 암호화 서비스 (None이면 새로 생성)
        """
        self.cache = cache
        self.encryption = encryption or EncryptionService()

    async def create_session(
        self,
        user_id: str,
        email: str,
        role: str = "admin",
        ttl: int = 3600,
    ) -> str:
        """
        Redis 세션 생성 (암호화 적용)

        사용자 정보를 암호화하여 Redis에 저장합니다.
        이메일 주소는 Fernet 대칭 암호화를 사용하여 보호합니다.

        Args:
            user_id: 사용자 ID (예: user_01JCAW0V1QQ9KZ2F3XHBP8TGNY)
            email: 이메일 (평문, 암호화되어 저장됨)
            role: 역할 (admin/user, 기본값: admin)
            ttl: 세션 만료 시간 (초, 기본값: 3600 = 1시간)

        Returns:
            str: session_id (user_id와 동일)

        Example:
            >>> manager = SessionManager(cache)
            >>> session_id = await manager.create_session(
            ...     "user_01JCAW...", "admin@example.com", "admin", ttl=3600
            ... )
        """
        try:
            session_key = f"session:{user_id}"

            # 이메일 암호화 (Fernet symmetric encryption)
            encrypted_email = self.encryption.encrypt(email)

            session_data: SessionData = {
                "user_id": user_id,
                "email": encrypted_email,  # 암호화된 이메일
                "role": role,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

            # Redis에 세션 저장 (JSON 직렬화)
            assert self.cache.redis_client is not None, "Redis client not connected"
            await self.cache.redis_client.setex(
                session_key,
                ttl,
                json.dumps(session_data),
            )

            logger.info(
                f"세션 생성: {session_key}",
                extra={
                    "user_id": user_id,
                    "email": email,  # 로그에는 평문 이메일 (모니터링용)
                    "role": role,
                    "ttl": ttl,
                },
            )

            return user_id

        except Exception as e:
            logger.error(
                f"세션 생성 실패: {str(e)}",
                exc_info=True,
            )
            raise AppException(
                status_code=503,
                detail="세션 생성에 실패했습니다",
            )

    async def get_session(self, session_id: str) -> Optional[SessionData]:
        """
        Redis 세션 조회 (복호화 적용)

        session_id로 Redis에서 세션 데이터를 조회하고 이메일을 복호화합니다.

        Args:
            session_id: 세션 ID (user_id)

        Returns:
            Optional[SessionData]: {"user_id": "...", "email": "...", "role": "..."}
                                   세션이 없으면 None
                                   이메일은 복호화된 평문으로 반환

        Example:
            >>> manager = SessionManager(cache)
            >>> session = await manager.get_session("user_01JCAW...")
            >>> if session:
            ...     print(f"Email: {session['email']}")  # 복호화된 평문
        """
        try:
            session_key = f"session:{session_id}"

            assert self.cache.redis_client is not None, "Redis client not connected"
            session_data_str = await self.cache.redis_client.get(session_key)

            if not session_data_str:
                logger.debug(
                    f"세션 없음 또는 만료: {session_key}",
                    extra={"session_id": session_id},
                )
                return None

            session_data: SessionData = json.loads(session_data_str)

            # 이메일 복호화 (Fernet symmetric decryption)
            encrypted_email = session_data["email"]
            decrypted_email = self.encryption.decrypt(encrypted_email)
            session_data["email"] = decrypted_email

            logger.debug(
                f"세션 조회 성공: {session_key}",
                extra={"session_id": session_id},
            )

            return session_data

        except Exception as e:
            logger.error(
                f"세션 조회 실패: {str(e)}",
                exc_info=True,
            )
            return None

    async def invalidate_session(self, session_id: str) -> None:
        """
        Redis 세션 무효화 (로그아웃)

        session_id에 해당하는 세션을 Redis에서 삭제합니다.

        Args:
            session_id: 세션 ID (user_id)

        Example:
            >>> manager = SessionManager(cache)
            >>> await manager.invalidate_session("user_01JCAW...")
        """
        try:
            session_key = f"session:{session_id}"

            assert self.cache.redis_client is not None, "Redis client not connected"
            await self.cache.redis_client.delete(session_key)

            logger.info(
                f"세션 무효화: {session_key}",
                extra={"session_id": session_id},
            )

        except Exception as e:
            logger.error(
                f"세션 무효화 실패: {str(e)}",
                exc_info=True,
            )
            raise AppException(
                status_code=503,
                detail="세션 무효화에 실패했습니다",
            )
