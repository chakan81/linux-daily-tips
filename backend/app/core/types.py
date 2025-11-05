"""
타입 정의 모듈

TypedDict를 사용하여 구조화된 딕셔너리 타입을 정의합니다.
타입 안전성을 강화하고 MyPy 에러를 해결합니다.
"""

from typing import TypedDict


class SessionData(TypedDict):
    """
    Redis 세션 데이터 구조

    Attributes:
        user_id: 사용자 ID (ULID 형식: user_01JCAW...)
        email: 암호화된 이메일 주소
        role: 사용자 역할 (admin/user)
        created_at: 세션 생성 시간 (ISO 8601 형식)

    Example:
        ```python
        session: SessionData = {
            "user_id": "user_01JCAW0V1QQ9KZ2F3XHBP8TGNY",
            "email": "gAAAAABl...",  # 암호화된 이메일
            "role": "admin",
            "created_at": "2024-01-01T00:00:00.000Z",
        }
        ```
    """
    user_id: str
    email: str
    role: str
    created_at: str


class GoogleUserInfo(TypedDict):
    """
    Google OAuth 사용자 정보 구조

    Attributes:
        id: Google 사용자 고유 ID
        email: 이메일 주소
        verified_email: 이메일 인증 여부
        name: 사용자 이름
        picture: 프로필 사진 URL

    Example:
        ```python
        user_info: GoogleUserInfo = {
            "id": "google_user_123456789",
            "email": "user@example.com",
            "verified_email": True,
            "name": "John Doe",
            "picture": "https://lh3.googleusercontent.com/...",
        }
        ```
    """
    id: str
    email: str
    verified_email: bool
    name: str
    picture: str


class GoogleTokenData(TypedDict, total=False):
    """
    Google OAuth 토큰 응답 구조

    Attributes:
        access_token: Google access token
        expires_in: 만료 시간 (초 단위)
        token_type: 토큰 타입 (Bearer)
        scope: 권한 범위
        refresh_token: 리프레시 토큰 (선택적)

    Example:
        ```python
        token_data: GoogleTokenData = {
            "access_token": "ya29.a0AfH6SMB...",
            "expires_in": 3599,
            "token_type": "Bearer",
            "scope": "openid email profile",
        }
        ```
    """
    access_token: str
    expires_in: int
    token_type: str
    scope: str
    refresh_token: str  # Optional (total=False)
