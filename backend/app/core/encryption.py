"""
암호화 유틸리티

Fernet 대칭키 암호화를 제공합니다.
"""

import logging

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings
from app.core.exceptions import AppException

logger = logging.getLogger(__name__)


class EncryptionService:
    """
    Fernet 암호화 서비스

    Redis 세션 데이터 암호화에 사용됩니다.

    Attributes:
        cipher: Fernet 암호화 객체
    """

    def __init__(self, encryption_key: str | None = None) -> None:
        """
        EncryptionService 초기화

        Args:
            encryption_key: Fernet 암호화 키 (None이면 settings에서 가져옴)
        """
        key = encryption_key or settings.REDIS_ENCRYPTION_KEY
        self.cipher = Fernet(key.encode())

    def encrypt(self, data: str) -> str:
        """
        문자열 암호화

        Args:
            data: 원본 문자열

        Returns:
            str: 암호화된 문자열 (base64)

        Raises:
            AppException: 암호화 실패 시 (500)
        """
        try:
            encrypted = self.cipher.encrypt(data.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"데이터 암호화 실패: {e}", exc_info=True)
            raise AppException(
                status_code=500,
                detail="데이터 암호화에 실패했습니다"
            )

    def decrypt(self, encrypted_data: str) -> str:
        """
        암호화된 문자열 복호화

        Args:
            encrypted_data: 암호화된 문자열

        Returns:
            str: 복호화된 원본 문자열

        Raises:
            AppException: 복호화 실패 시 (401 - 세션 무효)
        """
        try:
            decrypted = self.cipher.decrypt(encrypted_data.encode())
            return decrypted.decode()
        except InvalidToken:
            logger.error("세션 데이터 복호화 실패 (잘못된 키 또는 손상된 데이터)")
            raise AppException(
                status_code=401,
                detail="세션이 유효하지 않습니다. 다시 로그인해주세요."
            )
        except Exception as e:
            logger.error(f"세션 데이터 복호화 중 예상치 못한 오류: {e}", exc_info=True)
            raise AppException(
                status_code=500,
                detail="세션 처리 중 오류가 발생했습니다"
            )
