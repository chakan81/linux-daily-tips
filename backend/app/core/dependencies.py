"""
FastAPI 의존성 함수들

공통으로 사용되는 FastAPI 의존성 함수를 정의합니다.
인증, 데이터베이스 세션 등의 의존성을 제공합니다.
"""

from typing import Optional

from fastapi import Cookie, Depends, HTTPException, status

from app.core.security import decode_access_token


async def get_current_user(access_token: Optional[str] = Cookie(None)) -> dict:
    """
    현재 로그인한 사용자 정보를 가져옵니다.

    HttpOnly Cookie에서 JWT 토큰을 추출하고 검증하여 사용자 정보를 반환합니다.
    Day 14에서 Redis 블랙리스트 확인 기능이 추가될 예정입니다.

    Args:
        access_token: HttpOnly Cookie에서 추출한 JWT 토큰

    Returns:
        dict: 사용자 정보 페이로드 (sub, email 등)

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


async def get_db():
    """
    데이터베이스 세션 의존성을 제공합니다.

    SQLAlchemy 비동기 세션을 생성하고 요청 종료 시 자동으로 닫습니다.
    Day 10-11에서 SQLAlchemy 비동기 세션과 함께 구현될 예정입니다.

    Yields:
        AsyncSession: SQLAlchemy 비동기 데이터베이스 세션

    Example:
        ```python
        @router.get("/tips/")
        async def get_tips(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Tip))
            return result.scalars().all()
        ```

    Note:
        - 각 요청마다 독립적인 세션 생성
        - 요청 종료 시 자동으로 세션 종료
        - 트랜잭션 롤백은 예외 발생 시 자동 처리
    """
    # TODO: Day 10-11에서 구현 예정
    # async with AsyncSessionLocal() as session:
    #     try:
    #         yield session
    #         await session.commit()
    #     except Exception:
    #         await session.rollback()
    #         raise
    #     finally:
    #         await session.close()
    pass


# TODO: Day 14에서 Redis 의존성 추가 예정
# async def get_redis():
#     """
#     Redis 클라이언트 의존성을 제공합니다.
#
#     캐싱 및 세션 관리를 위한 Redis 클라이언트를 반환합니다.
#
#     Yields:
#         Redis: Redis 클라이언트 인스턴스
#     """
#     redis_client = await get_redis_client()
#     try:
#         yield redis_client
#     finally:
#         await redis_client.close()
