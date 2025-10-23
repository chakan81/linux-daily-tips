"""
Google OAuth 2.0 인증 서비스

OAuth 인증 플로우 및 세션 관리 비즈니스 로직을 처리합니다.
- Google OAuth URL 생성 (CSRF 방어용 state 파라미터 포함)
- Authorization Code → Access Token 교환
- Google 사용자 정보 조회
- 관리자 계정 생성/조회
- Redis 세션 생성/관리 (암호화 적용)
- OAuth State Parameter 검증 (CSRF 방어)
"""

import json
import logging
import secrets
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlencode

import httpx
from cryptography.fernet import Fernet
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import CacheService
from app.core.config import settings
from app.core.exceptions import AppException
from app.core.types import GoogleTokenData, GoogleUserInfo, SessionData
from app.models.user import AdminUser

# 로거 인스턴스
logger = logging.getLogger(__name__)

# Google OAuth 2.0 엔드포인트
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


class AuthService:
    """
    Google OAuth 2.0 인증 서비스

    주요 기능:
    - Google OAuth URL 생성
    - Authorization Code → Access Token 교환
    - Google 사용자 정보 조회
    - 관리자 계정 생성/조회
    - Redis 세션 생성/관리 (암호화 적용)

    Attributes:
        cache: Redis 캐시 서비스 (세션 관리용)
        http_client: httpx 비동기 HTTP 클라이언트
        cipher: Fernet 암호화 객체 (세션 데이터 암호화)
    """

    def __init__(self, cache: CacheService):
        """
        AuthService 초기화

        Args:
            cache: Redis 캐시 서비스 (세션 관리)
        """
        self.cache = cache
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(10.0, connect=5.0),  # 명시적 타임아웃
            follow_redirects=False,  # 리다이렉트 자동 추적 비활성화
        )
        # Fernet 암호화 객체 초기화 (세션 데이터 암호화용)
        self.cipher = Fernet(settings.REDIS_ENCRYPTION_KEY.encode())

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
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent",
            "state": state,  # CSRF 방어용 state 파라미터
        }

        auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

        logger.info(
            "Google OAuth URL 생성 (state 포함)",
            extra={
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "state_length": len(state),
            },
        )

        return auth_url

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
        try:
            payload = {
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            }

            response = await self.http_client.post(GOOGLE_TOKEN_URL, data=payload)

            if response.status_code != 200:
                error_data = response.json()
                logger.error(
                    f"Google token exchange 실패: {error_data.get('error')}",
                    extra={
                        "status_code": response.status_code,
                        "error": error_data,
                    },
                )
                raise AppException(
                    status_code=400,
                    detail=f"Google 인증 실패: {error_data.get('error_description', 'Invalid authorization code')}",
                )

            token_data: GoogleTokenData = response.json()

            logger.info(
                "Google token exchange 성공",
                extra={
                    "expires_in": token_data.get("expires_in"),
                },
            )

            return token_data

        except httpx.HTTPError as e:
            logger.error(
                f"Google API HTTP 오류: {str(e)}",
                exc_info=True,
            )
            raise AppException(
                status_code=503,
                detail="Google 인증 서버에 연결할 수 없습니다",
            )
        except Exception as e:
            logger.error(
                f"Token exchange 예상치 못한 오류: {str(e)}",
                exc_info=True,
            )
            raise

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
        try:
            headers = {"Authorization": f"Bearer {access_token}"}

            response = await self.http_client.get(GOOGLE_USERINFO_URL, headers=headers)

            if response.status_code != 200:
                logger.error(
                    f"Google userinfo 조회 실패: {response.status_code}",
                    extra={
                        "status_code": response.status_code,
                    },
                )
                raise AppException(
                    status_code=401,
                    detail="Google 사용자 정보를 가져올 수 없습니다",
                )

            user_info: GoogleUserInfo = response.json()

            logger.info(
                "Google userinfo 조회 성공",
                extra={
                    "email": user_info.get("email"),
                    "verified_email": user_info.get("verified_email"),
                },
            )

            return user_info

        except httpx.HTTPError as e:
            logger.error(
                f"Google API HTTP 오류: {str(e)}",
                exc_info=True,
            )
            raise AppException(
                status_code=503,
                detail="Google 사용자 정보 서버에 연결할 수 없습니다",
            )
        except Exception as e:
            logger.error(
                f"Userinfo 조회 예상치 못한 오류: {str(e)}",
                exc_info=True,
            )
            raise

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
        try:
            # 1. 기존 관리자 계정 조회
            stmt = select(AdminUser).where(AdminUser.email == email)
            result = await db.execute(stmt)
            admin = result.scalar_one_or_none()

            if admin:
                # 2. 기존 사용자 → last_login 업데이트
                admin.last_login = datetime.now(timezone.utc)
                await db.flush()

                logger.info(
                    f"기존 관리자 로그인: {admin.id}",
                    extra={
                        "email": email,
                        "last_login": admin.last_login.isoformat(),
                    },
                )

                return admin

            # 3. 신규 사용자 → 계정 생성
            # OAuth 사용자는 password_hash 불필요 (빈 문자열)
            admin = AdminUser(
                username=email.split("@")[0],  # 이메일 @ 앞부분을 username으로
                email=email,
                password_hash="",  # OAuth 사용자는 비밀번호 불필요
                is_active=True,
                is_superuser=False,  # 기본 권한은 일반 관리자
                last_login=datetime.now(timezone.utc),
            )

            db.add(admin)
            await db.flush()
            await db.refresh(admin)

            logger.info(
                f"신규 관리자 생성: {admin.id}",
                extra={
                    "email": email,
                    "username": admin.username,
                },
            )

            return admin

        except Exception as e:
            logger.error(
                f"관리자 계정 생성/조회 실패: {str(e)}",
                exc_info=True,
            )
            raise

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
        try:
            session_key = f"session:{user_id}"

            # 이메일 암호화 (Fernet symmetric encryption)
            encrypted_email = self.cipher.encrypt(email.encode()).decode()

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
            >>> service = AuthService(cache)
            >>> session = await service.get_session("user_01JCAW...")
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
            decrypted_email = self.cipher.decrypt(encrypted_email.encode()).decode()
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
            >>> service = AuthService(cache)
            >>> await service.invalidate_session("user_01JCAW...")
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
            >>> service = AuthService(cache)
            >>> is_valid = await service.verify_oauth_state(state)
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

    async def close(self) -> None:
        """
        HTTP 클라이언트 종료

        AuthService 사용 종료 시 httpx 클라이언트를 닫습니다.
        """
        await self.http_client.aclose()
