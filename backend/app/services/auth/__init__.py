"""
Google OAuth 2.0 인증 서비스 (모듈화 버전)

OAuth 인증 플로우 및 세션 관리 비즈니스 로직을 처리합니다.
- Google OAuth URL 생성 (CSRF 방어용 state 파라미터 포함)
- Authorization Code → Access Token 교환
- Google 사용자 정보 조회
- 관리자 계정 생성/조회
- Redis 세션 생성/관리 (암호화 적용)
- OAuth State Parameter 검증 (CSRF 방어)

이 모듈은 기존 auth_service.py를 5개의 하위 모듈로 분리하여 관리합니다:
- oauth_client: Google OAuth HTTP 통신
- session_manager: Redis 세션 관리
- oauth_state_validator: OAuth state 검증
- user_service: 데이터베이스 사용자 관리
- __init__.py: 통합 인터페이스 (AuthService)
"""

import logging
from typing import Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import CacheService
from app.core.encryption import EncryptionService
from app.core.types import GoogleTokenData, GoogleUserInfo, SessionData
from app.models.user import AdminUser

from .oauth_client import OAuthClient
from .oauth_state_validator import OAuthStateValidator
from .session_manager import SessionManager
from .user_service import UserService

# 로거 인스턴스
logger = logging.getLogger(__name__)


__all__ = ["AuthService"]


class AuthService:
    """
    Google OAuth 2.0 인증 서비스 (통합 인터페이스)

    주요 기능:
    - Google OAuth URL 생성
    - Authorization Code → Access Token 교환
    - Google 사용자 정보 조회
    - 관리자 계정 생성/조회
    - Redis 세션 생성/관리 (암호화 적용)
    - OAuth State Parameter 검증 (CSRF 방어)

    Attributes:
        cache: Redis 캐시 서비스 (세션 관리용)
        oauth_client: Google OAuth HTTP 클라이언트
        session_manager: Redis 세션 관리자
        oauth_state_validator: OAuth state 검증기
        user_service: 사용자 서비스
        http_client: httpx 비동기 HTTP 클라이언트 (하위 호환성)
    """

    def __init__(self, cache: CacheService):
        """
        AuthService 초기화

        Args:
            cache: Redis 캐시 서비스 (세션 관리)
        """
        self.cache = cache

        # httpx 클라이언트 생성 (모든 하위 모듈에서 공유)
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(10.0, connect=5.0),  # 명시적 타임아웃
            follow_redirects=False,  # 리다이렉트 자동 추적 비활성화
        )

        # 암호화 서비스 생성 (세션 관리에서 사용)
        encryption = EncryptionService()

        # 하위 모듈 초기화
        self.oauth_client = OAuthClient(http_client=self.http_client)
        self.session_manager = SessionManager(cache=cache, encryption=encryption)
        self.oauth_state_validator = OAuthStateValidator(cache=cache)
        self.user_service = UserService()

    # =========================================================================
    # OAuth Client 메서드 (위임)
    # =========================================================================

    async def generate_google_auth_url(self, state: str) -> str:
        """
        Google OAuth 2.0 로그인 URL 생성 (CSRF 방어용 state 파라미터 포함)

        사용자를 Google 로그인 페이지로 리다이렉트할 URL을 생성합니다.
        CSRF 공격을 방어하기 위해 state 파라미터를 포함하여 전송합니다.

        Args:
            state: CSRF 방어용 랜덤 state 문자열 (Redis에 저장됨)

        Returns:
            str: Google OAuth URL (https://accounts.google.com/o/oauth2/v2/auth?...)

        Example:
            >>> service = AuthService(cache)
            >>> state = secrets.token_urlsafe(32)
            >>> await service.save_oauth_state(state, ttl=600)
            >>> auth_url = await service.generate_google_auth_url(state)
            >>> # 브라우저를 auth_url로 리다이렉트
        """
        return await self.oauth_client.generate_google_auth_url(state)

    async def exchange_code_for_token(self, code: str) -> GoogleTokenData:
        """
        Authorization Code → Access Token 교환

        Google OAuth 인증 후 받은 authorization code를 access token으로 교환합니다.

        Args:
            code: Google OAuth authorization code

        Returns:
            GoogleTokenData: {"access_token": "...", "expires_in": 3600, "token_type": "Bearer"}

        Raises:
            AppException: Google API 호출 실패 시 (400/401)

        Example:
            >>> service = AuthService(cache)
            >>> token_data = await service.exchange_code_for_token("valid_code_123")
            >>> access_token = token_data["access_token"]
        """
        return await self.oauth_client.exchange_code_for_token(code)

    async def get_user_info_from_google(self, access_token: str) -> GoogleUserInfo:
        """
        Google Access Token으로 사용자 정보 조회

        Google API를 호출하여 사용자의 이메일, 이름, 프로필 사진 등을 조회합니다.

        Args:
            access_token: Google OAuth access token

        Returns:
            GoogleUserInfo: {"email": "...", "id": "...", "name": "...", "picture": "..."}

        Raises:
            AppException: Google API 호출 실패 시 (401/403)

        Example:
            >>> service = AuthService(cache)
            >>> user_info = await service.get_user_info_from_google(access_token)
            >>> email = user_info["email"]
        """
        return await self.oauth_client.get_user_info_from_google(access_token)

    # =========================================================================
    # Session Manager 메서드 (위임)
    # =========================================================================

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
            >>> service = AuthService(cache)
            >>> session_id = await service.create_session(
            ...     "user_01JCAW...", "admin@example.com", "admin", ttl=3600
            ... )
        """
        return await self.session_manager.create_session(user_id, email, role, ttl)

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
            >>> service = AuthService(cache)
            >>> session = await service.get_session("user_01JCAW...")
            >>> if session:
            ...     print(f"Email: {session['email']}")  # 복호화된 평문
        """
        return await self.session_manager.get_session(session_id)

    async def invalidate_session(self, session_id: str) -> None:
        """
        Redis 세션 무효화 (로그아웃)

        session_id에 해당하는 세션을 Redis에서 삭제합니다.

        Args:
            session_id: 세션 ID (user_id)

        Example:
            >>> service = AuthService(cache)
            >>> await service.invalidate_session("user_01JCAW...")
        """
        return await self.session_manager.invalidate_session(session_id)

    # =========================================================================
    # OAuth State Validator 메서드 (위임)
    # =========================================================================

    async def save_oauth_state(self, state: str, ttl: int = 600) -> None:
        """
        OAuth State Parameter를 Redis에 저장 (CSRF 방어)

        OAuth 로그인 시작 시 생성한 state를 Redis에 저장합니다.
        콜백에서 동일한 state가 반환되는지 검증하여 CSRF 공격을 방어합니다.

        Args:
            state: CSRF 방어용 랜덤 state 문자열
            ttl: 만료 시간 (초, 기본값: 600 = 10분)

        Example:
            >>> service = AuthService(cache)
            >>> state = secrets.token_urlsafe(32)
            >>> await service.save_oauth_state(state, ttl=600)
        """
        return await self.oauth_state_validator.save_oauth_state(state, ttl)

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
            >>> service = AuthService(cache)
            >>> is_valid = await service.verify_oauth_state(state)
            >>> if not is_valid:
            >>>     raise HTTPException(400, "Invalid OAuth state")
        """
        return await self.oauth_state_validator.verify_oauth_state(state)

    # =========================================================================
    # User Service 메서드 (위임)
    # =========================================================================

    async def create_or_get_admin_user(
        self,
        db: AsyncSession,
        email: str,
        google_id: str,
    ) -> AdminUser:
        """
        관리자 계정 생성 또는 조회

        이메일로 기존 관리자를 찾거나, 없으면 새로 생성합니다.
        Google OAuth를 통한 로그인이므로 password_hash는 빈 문자열로 설정합니다.

        Args:
            db: 데이터베이스 세션
            email: Google 이메일
            google_id: Google 사용자 ID

        Returns:
            AdminUser: 관리자 사용자 모델 인스턴스

        Example:
            >>> service = AuthService(cache)
            >>> admin = await service.create_or_get_admin_user(
            ...     db, "admin@example.com", "google_user_123"
            ... )
        """
        return await self.user_service.create_or_get_admin_user(db, email, google_id)

    # =========================================================================
    # 리소스 정리
    # =========================================================================

    async def close(self) -> None:
        """
        HTTP 클라이언트 종료

        AuthService 사용 종료 시 httpx 클라이언트를 닫습니다.
        """
        await self.http_client.aclose()
