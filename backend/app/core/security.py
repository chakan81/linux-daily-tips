"""
보안 관련 유틸리티

JWT 토큰 생성/검증 및 패스워드 해싱 기능을 제공합니다.
OAuth + JWT + Redis 블랙리스트 패턴을 지원합니다.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# 패스워드 해싱 컨텍스트 (bcrypt 사용)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    평문 패스워드와 해시된 패스워드를 비교하여 일치 여부를 확인합니다.

    Args:
        plain_password: 평문 패스워드
        hashed_password: bcrypt로 해시된 패스워드

    Returns:
        bool: 패스워드 일치 여부
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    평문 패스워드를 bcrypt로 해싱합니다.

    Args:
        password: 평문 패스워드

    Returns:
        str: bcrypt로 해시된 패스워드
    """
    return pwd_context.hash(password)


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    JWT Access Token을 생성합니다.

    HttpOnly Cookie에 저장되어 XSS 공격으로부터 보호됩니다.
    Redis 블랙리스트와 함께 사용하여 로그아웃 기능을 구현합니다.

    Args:
        data: 토큰에 포함할 페이로드 데이터 (예: {"sub": user_id, "email": user_email})
        expires_delta: 만료 시간 (기본값: settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    Returns:
        str: 생성된 JWT 토큰

    Example:
        >>> token = create_access_token({"sub": "user123", "email": "user@example.com"})
        >>> # HttpOnly Cookie에 저장: Set-Cookie: access_token=<token>; HttpOnly; Secure; SameSite=Lax
    """
    to_encode = data.copy()

    # 만료 시간 설정 (timezone-aware datetime 사용)
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # JWT 표준 클레임 추가
    to_encode.update(
        {
            "exp": expire,  # 만료 시간
            "iat": now,  # 발급 시간
        }
    )

    # JWT 생성 (HS256 알고리즘 사용)
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    JWT Access Token을 검증하고 디코딩합니다.

    토큰의 서명과 만료 시간을 검증합니다.
    Day 14에서 Redis 블랙리스트 확인 기능이 추가될 예정입니다.

    Args:
        token: 검증할 JWT 토큰

    Returns:
        Optional[Dict[str, Any]]: 디코딩된 페이로드 (실패 시 None)

    Example:
        >>> payload = decode_access_token(token)
        >>> if payload:
        >>>     user_id = payload.get("sub")
        >>>     email = payload.get("email")
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        # 토큰이 유효하지 않거나 만료됨
        return None


# TODO: Day 14에서 구현 예정
# async def add_token_to_blacklist(token: str, redis_client) -> None:
#     """
#     로그아웃 시 토큰을 Redis 블랙리스트에 추가합니다.
#
#     Args:
#         token: 블랙리스트에 추가할 JWT 토큰
#         redis_client: Redis 클라이언트 인스턴스
#     """
#     payload = decode_access_token(token)
#     if payload:
#         exp = payload.get("exp")
#         ttl = exp - datetime.now(timezone.utc).timestamp()
#         await redis_client.setex(f"blacklist:{token}", int(ttl), "1")
#
#
# async def is_token_blacklisted(token: str, redis_client) -> bool:
#     """
#     토큰이 블랙리스트에 있는지 확인합니다.
#
#     Args:
#         token: 확인할 JWT 토큰
#         redis_client: Redis 클라이언트 인스턴스
#
#     Returns:
#         bool: 블랙리스트에 있으면 True
#     """
#     result = await redis_client.exists(f"blacklist:{token}")
#     return bool(result)
