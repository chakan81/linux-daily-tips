"""
Google OAuth 2.0 인증 API 엔드포인트

OAuth 인증 플로우 및 JWT 토큰 관리를 제공합니다.
- Google OAuth 로그인 리다이렉트
- OAuth 콜백 처리 (토큰 교환 + 세션 생성)
- 리프레시 토큰 갱신
- 로그아웃 (세션 무효화)
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from jose import JWTError
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_auth_service, get_current_admin
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.core.types import SessionData
from app.db.session import get_db
from app.services.auth_service import AuthService

# 로거 인스턴스
logger = logging.getLogger(__name__)

# APIRouter 생성
router = APIRouter()


# ============================================================
# Pydantic 스키마
# ============================================================


class RefreshTokenRequest(BaseModel):
    """리프레시 토큰 요청 스키마"""

    refresh_token: str


class TokenResponse(BaseModel):
    """JWT 토큰 응답 스키마"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30분 (초 단위)


class LogoutResponse(BaseModel):
    """로그아웃 응답 스키마"""

    message: str


# ============================================================
# OAuth 엔드포인트
# ============================================================


@router.get("/login")
async def google_login(
    auth_service: AuthService = Depends(get_auth_service),
) -> RedirectResponse:
    """
    Google OAuth 2.0 로그인 리다이렉트 (CSRF 방어 포함)

    사용자를 Google OAuth 인증 페이지로 리다이렉트합니다.
    CSRF 공격 방어를 위해 랜덤 state 파라미터를 생성하고 Redis에 저장합니다.

    Args:
        auth_service: 인증 서비스 (자동 주입)

    Returns:
        RedirectResponse: Google OAuth URL로 리다이렉트 (302)

    Security:
        - 랜덤 state 파라미터 생성 (32바이트 URL-safe)
        - state를 Redis에 10분간 저장 (콜백에서 검증)

    Example:
        GET /api/v1/auth/login
        → 302 Redirect to https://accounts.google.com/o/oauth2/v2/auth?state=...&...
    """
    import secrets

    # CSRF 방어용 랜덤 state 생성 (32바이트 = 43자 URL-safe)
    state = secrets.token_urlsafe(32)

    # Redis에 state 저장 (10분 TTL)
    await auth_service.save_oauth_state(state, ttl=600)

    # Google OAuth URL 생성 (state 포함)
    google_auth_url = await auth_service.generate_google_auth_url(state)

    logger.info(
        "Google OAuth 로그인 리다이렉트 생성 (CSRF 방어 state 포함)",
        extra={"state_length": len(state)},
    )

    return RedirectResponse(url=google_auth_url, status_code=302)


@router.get("/callback")
async def google_callback(
    code: str = Query(..., description="Google OAuth authorization code"),
    state: str = Query(..., description="CSRF 방어용 OAuth state parameter"),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
) -> RedirectResponse:
    """
    Google OAuth 2.0 콜백 처리 (CSRF 방어 포함)

    Google OAuth 인증 후 받은 authorization code를 처리하여
    JWT 토큰을 발급하고 HttpOnly Cookie로 전달합니다.

    Args:
        code: Google OAuth authorization code (쿼리 파라미터)
        state: CSRF 방어용 OAuth state parameter (쿼리 파라미터)
        db: 데이터베이스 세션
        auth_service: 인증 서비스

    Returns:
        RedirectResponse: 프론트엔드로 리다이렉트 (HttpOnly Cookie로 토큰 전달)

    Flow:
        1. OAuth State Parameter 검증 (CSRF 방어)
        2. Authorization Code → Access Token 교환
        3. Access Token으로 Google 사용자 정보 조회
        4. PostgreSQL에 관리자 계정 생성/조회
        5. Redis 세션 생성 (1시간 TTL, 이메일 암호화)
        6. JWT 액세스 토큰 + 리프레시 토큰 발급
        7. 프론트엔드 URL 화이트리스트 검증 (Open Redirect 방지)
        8. HttpOnly Cookie로 토큰 전달 (XSS 공격 방지)
        9. 프론트엔드로 리다이렉트

    Security:
        - OAuth State Parameter 검증 (CSRF 공격 방어)
        - 토큰은 HttpOnly Cookie로 전달 (URL 파라미터 대신)
        - 프론트엔드 URL 화이트리스트 검증 (Open Redirect 방지)
        - Redis 세션 데이터 암호화 (이메일)
        - Cookie Secure, SameSite 설정 (CSRF 방어)

    Raises:
        HTTPException: OAuth 인증 실패, 잘못된 state, 또는 잘못된 리다이렉트 URL (400)

    Example:
        GET /api/v1/auth/callback?code=4/0AY0e-...&state=abc123...
        → 302 Redirect to http://localhost:3000/admin
        → Set-Cookie: access_token=...; HttpOnly; Secure; SameSite=lax
        → Set-Cookie: refresh_token=...; HttpOnly; Secure; SameSite=lax
    """
    try:
        # 1. OAuth State Parameter 검증 (CSRF 방어)
        logger.info(f"OAuth 콜백 시작: code={code[:20]}..., state={state[:20]}...")
        is_valid_state = await auth_service.verify_oauth_state(state)

        if not is_valid_state:
            logger.error(
                f"OAuth state 검증 실패: {state[:20]}...",
                extra={"state": state[:20]},
            )
            raise HTTPException(
                status_code=400,
                detail="Invalid OAuth state parameter (possible CSRF attack)",
            )

        logger.info("OAuth state 검증 성공")

        # 2. Authorization Code → Access Token
        token_data = await auth_service.exchange_code_for_token(code)
        access_token = token_data["access_token"]

        # 3. Google 사용자 정보 조회
        user_info = await auth_service.get_user_info_from_google(access_token)
        email = user_info["email"]
        google_id = user_info["id"]

        logger.info(f"Google 사용자 정보 조회 성공: email={email}")

        # 4. PostgreSQL에 관리자 계정 생성/조회
        admin_user = await auth_service.create_or_get_admin_user(db, email, google_id)

        # 5. 데이터베이스 커밋 (관리자 계정 변경사항 저장)
        await db.commit()

        logger.info(f"관리자 계정 처리 완료: user_id={admin_user.id}")

        # 6. Redis 세션 생성 (이메일 암호화 적용)
        session_id = await auth_service.create_session(
            user_id=str(admin_user.id),
            email=admin_user.email,
            role="admin",
            ttl=3600,  # 1시간
        )

        # 7. JWT 토큰 발급
        jwt_access_token = create_access_token(
            {"user_id": str(admin_user.id), "role": "admin"}
        )
        jwt_refresh_token = create_refresh_token(
            {"user_id": str(admin_user.id), "role": "admin"}
        )

        logger.info(
            f"JWT 토큰 발급 완료: user_id={admin_user.id}, session_id={session_id}"
        )

        # 8. 프론트엔드로 리다이렉트 (HttpOnly Cookie로 토큰 전달)
        # 보안 개선: URL 파라미터 대신 HttpOnly Cookie 사용
        frontend_redirect_url = f"{settings.FRONTEND_URL}/admin"

        # 프론트엔드 URL 화이트리스트 검증 (Open Redirect 방지)
        if not any(
            frontend_redirect_url.startswith(allowed_url)
            for allowed_url in settings.ALLOWED_FRONTEND_URLS
        ):
            logger.error(
                f"허용되지 않은 프론트엔드 URL: {frontend_redirect_url}",
                extra={"allowed_urls": settings.ALLOWED_FRONTEND_URLS},
            )
            raise HTTPException(
                status_code=400,
                detail="Invalid redirect URL",
            )

        # 리다이렉트 응답 생성
        response = RedirectResponse(url=frontend_redirect_url, status_code=302)

        # HttpOnly Cookie로 액세스 토큰 설정 (XSS 공격 방지)
        response.set_cookie(
            key="access_token",
            value=jwt_access_token,
            httponly=settings.COOKIE_HTTPONLY,  # JavaScript 접근 불가
            secure=settings.COOKIE_SECURE,  # HTTPS only (프로덕션)
            samesite=settings.COOKIE_SAMESITE,  # CSRF 방어
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # 30분
        )

        # HttpOnly Cookie로 리프레시 토큰 설정
        response.set_cookie(
            key="refresh_token",
            value=jwt_refresh_token,
            httponly=settings.COOKIE_HTTPONLY,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,  # 7일
        )

        logger.info(
            f"OAuth 콜백 완료: user_id={admin_user.id}, "
            f"redirect_url={frontend_redirect_url}"
        )

        return response

    except Exception as e:
        logger.error(f"OAuth callback 실패: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=400, detail=f"OAuth authentication failed: {str(e)}"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    request: RefreshTokenRequest,
) -> TokenResponse:
    """
    JWT 액세스 토큰 갱신

    리프레시 토큰을 검증하고 새로운 액세스 토큰을 발급합니다.

    Args:
        request: 리프레시 토큰 요청 ({"refresh_token": "..."})

    Returns:
        TokenResponse: {"access_token": "...", "token_type": "bearer", "expires_in": 1800}

    Raises:
        HTTPException: 리프레시 토큰이 유효하지 않을 때 (401)

    Example:
        POST /api/v1/auth/refresh
        Body: {"refresh_token": "eyJhbGc..."}
        → 200 OK {"access_token": "eyJhbGc...", "token_type": "bearer", "expires_in": 1800}
    """
    try:
        # 리프레시 토큰 검증
        payload = verify_token(request.refresh_token)

        logger.info(f"리프레시 토큰 검증 성공: user_id={payload.get('user_id')}")

        # 새 액세스 토큰 발급
        new_access_token = create_access_token(
            {"user_id": payload["user_id"], "role": payload.get("role", "user")}
        )

        logger.info(f"새 액세스 토큰 발급: user_id={payload.get('user_id')}")

        return TokenResponse(access_token=new_access_token)

    except JWTError as e:
        logger.warning(f"리프레시 토큰 검증 실패: {str(e)}")
        raise HTTPException(
            status_code=401, detail="Invalid or expired refresh token"
        )


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    admin: SessionData = Depends(get_current_admin),
    auth_service: AuthService = Depends(get_auth_service),
) -> LogoutResponse:
    """
    로그아웃 (Redis 세션 무효화)

    현재 인증된 관리자의 Redis 세션을 삭제하여 JWT 토큰을 무효화합니다.

    Args:
        admin: 현재 인증된 관리자 (SessionData 타입, get_current_admin 의존성)
        auth_service: 인증 서비스

    Returns:
        LogoutResponse: {"message": "Successfully logged out"}

    Security:
        - JWT 토큰 필수 (Authorization: Bearer <token>)
        - Redis 세션 유효성 확인 (복호화 적용)

    Note:
        Redis 세션을 삭제하여 JWT 토큰을 무효화합니다.
        클라이언트는 HttpOnly Cookie를 삭제해야 합니다.

    Example:
        POST /api/v1/auth/logout
        Headers: {"Authorization": "Bearer eyJhbGc..."}
        → 200 OK {"message": "Successfully logged out"}
    """
    user_id = admin["user_id"]

    logger.info(f"로그아웃 요청: user_id={user_id}, email={admin.get('email')}")

    # Redis 세션 무효화
    await auth_service.invalidate_session(user_id)

    logger.info(f"로그아웃 완료: user_id={user_id}")

    return LogoutResponse(message="Successfully logged out")
