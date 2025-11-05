"""
Google OAuth 2.0 클라이언트

Google OAuth 인증 플로우와 관련된 HTTP 통신을 담당합니다.
- Google OAuth URL 생성
- Authorization Code → Access Token 교환
- Google 사용자 정보 조회
"""

import logging
from typing import Optional
from urllib.parse import urlencode

import httpx

from app.core.config import settings
from app.core.exceptions import AppException
from app.core.types import GoogleTokenData, GoogleUserInfo

# 로거 인스턴스
logger = logging.getLogger(__name__)

# Google OAuth 2.0 엔드포인트
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


__all__ = ["OAuthClient"]


class OAuthClient:
    """
    Google OAuth 2.0 HTTP 클라이언트

    주요 기능:
    - Google OAuth URL 생성
    - Authorization Code → Access Token 교환
    - Google 사용자 정보 조회

    Attributes:
        http_client: httpx 비동기 HTTP 클라이언트
    """

    def __init__(self, http_client: Optional[httpx.AsyncClient] = None):
        """
        OAuthClient 초기화

        Args:
            http_client: httpx 비동기 HTTP 클라이언트 (None이면 새로 생성)
        """
        if http_client is None:
            self.http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(
                    settings.HTTP_TIMEOUT,
                    connect=settings.HTTP_CONNECT_TIMEOUT
                ),
                follow_redirects=False,  # 리다이렉트 자동 추적 비활성화
            )
            self._owns_client = True  # 클라이언트를 직접 생성한 경우
        else:
            self.http_client = http_client
            self._owns_client = False  # 외부에서 주입받은 경우

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
            >>> client = OAuthClient()
            >>> state = secrets.token_urlsafe(32)
            >>> auth_url = await client.generate_google_auth_url(state)
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
            >>> client = OAuthClient()
            >>> token_data = await client.exchange_code_for_token("valid_code_123")
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
            >>> client = OAuthClient()
            >>> user_info = await client.get_user_info_from_google(access_token)
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

    async def close(self) -> None:
        """
        HTTP 클라이언트 종료

        OAuthClient 사용 종료 시 httpx 클라이언트를 닫습니다.
        직접 생성한 클라이언트만 종료합니다.
        """
        if self._owns_client:
            await self.http_client.aclose()
