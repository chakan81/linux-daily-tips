"""
FastAPI 의존성 함수들

공통으로 사용되는 FastAPI 의존성 함수를 정의합니다.
인증, 데이터베이스 세션, Redis 캐시 등의 의존성을 제공합니다.
"""

import json
from typing import Any, AsyncGenerator, Optional

from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from app.core.cache import CacheService
from app.core.security import decode_access_token, verify_token
from app.core.types import SessionData

# HTTP Bearer 스키마 (Authorization 헤더에서 토큰 추출)
security = HTTPBearer()


async def get_current_user(
    access_token: Optional[str] = Cookie(None)
) -> dict[str, Any]:
    """
    현재 로그인한 사용자 정보를 가져옵니다.

    HttpOnly Cookie에서 JWT 토큰을 추출하고 검증하여 사용자 정보를 반환합니다.
    Day 14에서 Redis 블랙리스트 확인 기능이 추가될 예정입니다.

    Args:
        access_token: HttpOnly Cookie에서 추출한 JWT 토큰

    Returns:
        dict[str, Any]: 사용자 정보 페이로드 (sub, email 등)

    Raises:
        HTTPException: 인증 실패 시 401 Unauthorized

    Example:
        ```python
        @router.get("/me")
        async def get_me(current_user: dict = Depends(get_current_user)):
            return {"user_id": current_user["sub"], "email": current_user["email"]}
        ```

    Security Flow:
        1. HttpOnly Cookie에서 access_token 추출
        2. JWT 서명 및 만료 시간 검증
        3. [Day 14] Redis 블랙리스트 확인 (로그아웃된 토큰 차단)
        4. 사용자 정보 페이로드 반환
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Cookie에서 토큰 추출
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # JWT 토큰 검증 및 디코딩
    payload = decode_access_token(access_token)
    if payload is None:
        raise credentials_exception

    # TODO: Day 14에서 Redis 블랙리스트 확인 추가
    # if await is_token_blacklisted(access_token, redis_client):
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Token has been revoked",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )

    return payload


# get_db는 app.db.session에서 import하여 사용
# from app.db.session import get_db


async def get_cache() -> AsyncGenerator[CacheService, None]:
    """
    Redis CacheService 의존성을 제공합니다.

    캐싱 및 세션 관리를 위한 CacheService 인스턴스를 생성하고 반환합니다.
    요청 종료 시 자동으로 Redis 연결을 종료합니다.

    Yields:
        CacheService: Redis 캐시 서비스 인스턴스

    Example:
        ```python
        @router.get("/tips/daily")
        async def get_daily_tip(cache: CacheService = Depends(get_cache)):
            # 캐시에서 조회 시도
            cached_tip = await cache.get("tips:daily:2024-01-01")
            if cached_tip:
                return cached_tip

            # 캐시 미스 시 DB 조회 후 캐싱
            tip = await fetch_from_db()
            await cache.set("tips:daily:2024-01-01", tip, ttl=3600)
            return tip
        ```

    Note:
        - 요청마다 독립적인 CacheService 인스턴스 생성
        - 요청 종료 시 자동으로 Redis 연결 종료
        - 연결 실패 시 AppException 발생 (503 Service Unavailable)
    """
    cache = CacheService()
    await cache.connect()
    try:
        yield cache
    finally:
        await cache.disconnect()


async def get_tip_service(
    cache: CacheService = Depends(get_cache),
) -> "TipService":  # type: ignore[name-defined]
    """
    TipService 의존성을 제공합니다.

    Redis 캐싱이 통합된 TipService 인스턴스를 반환합니다.

    Args:
        cache: Redis 캐시 서비스 (자동 주입)

    Returns:
        TipService: 캐싱이 활성화된 TipService 인스턴스

    Example:
        ```python
        @router.get("/tips/daily")
        async def get_daily_tip(
            db: AsyncSession = Depends(get_db),
            service: TipService = Depends(get_tip_service)
        ):
            tip = await service.get_daily_tip(db, date.today())
            return tip
        ```

    Note:
        - 캐싱 활성화된 서비스 인스턴스
        - 캐시 MISS 시 자동으로 DB 조회
        - 캐시 HIT/MISS 로깅 포함
    """
    from app.services.tip import TipService

    return TipService(cache=cache)


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    cache: CacheService = Depends(get_cache),
) -> SessionData:
    """
    현재 인증된 관리자 정보 조회

    JWT 토큰 검증 → Redis 세션 확인 → 관리자 정보 반환 (복호화 적용)

    Args:
        credentials: HTTP Bearer 토큰
        cache: Redis 캐시 서비스

    Returns:
        SessionData: {"user_id": "...", "email": "...", "role": "admin", "created_at": "..."}
                     이메일은 복호화된 평문으로 반환

    Raises:
        HTTPException: 인증 실패 시 401/403

    Example:
        ```python
        @router.get("/admin/me")
        async def get_me(admin: SessionData = Depends(get_current_admin)):
            return {"user_id": admin["user_id"], "email": admin["email"]}
        ```

    Security Flow:
        1. Authorization 헤더에서 JWT 토큰 추출 (Bearer scheme)
        2. JWT 서명 및 만료 시간 검증
        3. Redis 세션 존재 여부 확인 (이메일 복호화)
        4. 관리자 역할(role="admin") 확인
        5. 사용자 정보 반환 (SessionData 타입)
    """
    try:
        # 1. JWT 토큰 검증
        token = credentials.credentials
        payload = verify_token(token)

        # 2. user_id 추출
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload: user_id missing",
            )

        # 3. Redis 세션 확인 (AuthService를 통해 복호화)
        # Note: 순환 import 방지를 위해 여기서 직접 import
        from app.services.auth_service import AuthService
        auth_service = AuthService(cache)

        session_data = await auth_service.get_session(user_id)

        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired",
            )

        # 4. 관리자 역할 확인
        if session_data.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin role required",
            )

        return session_data

    except HTTPException:
        # HTTPException은 그대로 re-raise (401/403)
        raise
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
        )


async def get_auth_service(cache: CacheService = Depends(get_cache)) -> "AuthService":  # type: ignore[name-defined]
    """
    AuthService 의존성을 제공합니다.

    Google OAuth 인증 및 세션 관리를 위한 AuthService 인스턴스를 반환합니다.

    Args:
        cache: Redis 캐시 서비스 (자동 주입)

    Returns:
        AuthService: 인증 서비스 인스턴스

    Example:
        ```python
        @router.get("/auth/login")
        async def login(auth_service: AuthService = Depends(get_auth_service)):
            auth_url = await auth_service.generate_google_auth_url()
            return RedirectResponse(auth_url)
        ```

    Note:
        - Redis 세션 관리 통합
        - Google OAuth 2.0 지원
        - JWT 토큰 발급 및 검증
    """
    from app.services.auth_service import AuthService

    return AuthService(cache=cache)


def get_terminal_service() -> "TerminalService":  # type: ignore[name-defined]
    """
    TerminalService 의존성을 제공합니다.

    Docker 기반 터미널 에뮬레이터 세션 관리를 위한 TerminalService 인스턴스를 반환합니다.

    Returns:
        TerminalService: 터미널 서비스 인스턴스

    Example:
        ```python
        @router.post("/terminal/session")
        async def create_session(
            db: AsyncSession = Depends(get_db),
            service: TerminalService = Depends(get_terminal_service)
        ):
            session = await service.create_session(db, session_data)
            return session
        ```

    Note:
        - Docker 컨테이너 생명주기 관리
        - 보안 명령어 실행 (블랙리스트 검증)
        - 자동 세션 만료 (30분)
    """
    from app.services.terminal import TerminalService

    return TerminalService()
