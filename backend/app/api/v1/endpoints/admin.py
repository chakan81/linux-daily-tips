"""
Admin API 엔드포인트

관리자 전용 API 엔드포인트를 제공합니다.
- 관리자 정보 조회 (GET /admin/me)
- 팁 생성/수정/삭제 (POST/PUT/DELETE /admin/tips)

인증이 필요한 엔드포인트로, get_current_admin 의존성을 사용합니다.
"""

from typing import Any

from fastapi import APIRouter, Depends, Request

from app.core.dependencies import get_current_admin
from app.core.rate_limit import limiter
from app.schemas.tip import Tip, TipCreate, TipUpdate

# APIRouter 생성
router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/me", response_model=dict[str, Any])
@limiter.limit("30/minute")
async def get_me(
    request: Request,
    current_admin: dict[str, Any] = Depends(get_current_admin),
) -> dict[str, Any]:
    """
    현재 로그인한 관리자 정보 조회

    JWT 토큰과 Redis 세션을 확인하여 관리자 정보를 반환합니다.

    Returns:
        dict: {"user_id": "...", "email": "...", "role": "admin"}

    Security:
        - JWT 토큰 필수 (Authorization: Bearer <token>)
        - Redis 세션 유효성 확인
        - role="admin" 확인
    """
    return {
        "user_id": current_admin["user_id"],
        "email": current_admin["email"],
        "role": current_admin["role"],
    }


@router.post("/tips", response_model=dict[str, Any], dependencies=[Depends(get_current_admin)])
@limiter.limit("5/minute")
async def create_tip(
    request: Request,
    tip_data: TipCreate,
    admin: dict[str, Any] = Depends(get_current_admin),
) -> dict[str, Any]:
    """
    관리자 전용: 새 팁 생성

    Args:
        tip_data: 팁 생성 데이터
        admin: 현재 인증된 관리자

    Returns:
        생성된 팁 정보

    Note:
        이 엔드포인트는 인증 테스트용 Mock 구현입니다.
        실제 DB 작업은 Day 15 이후 구현 예정.

    Security:
        - JWT 토큰 필수 (Authorization: Bearer <token>)
        - Redis 세션 유효성 확인
        - role="admin" 확인
    """
    # Mock 응답 (테스트용)
    return {
        "id": "tip_mock_123",
        "title": tip_data.title,
        "content": tip_data.content,
        "difficulty": tip_data.difficulty.value,
        "category": tip_data.category,
        "is_active": tip_data.is_active,
        "created_by": admin["email"],
        "message": f"Tip created by {admin['email']}",
    }


@router.put("/tips/{tip_id}", response_model=dict[str, Any], dependencies=[Depends(get_current_admin)])
@limiter.limit("10/minute")
async def update_tip(
    request: Request,
    tip_id: str,
    tip_data: TipUpdate,
    admin: dict[str, Any] = Depends(get_current_admin),
) -> dict[str, Any]:
    """
    관리자 전용: 팁 수정

    Args:
        tip_id: 팁 ID
        tip_data: 팁 수정 데이터
        admin: 현재 인증된 관리자

    Returns:
        수정된 팁 정보

    Note:
        이 엔드포인트는 인증 테스트용 Mock 구현입니다.
        실제 DB 작업은 Day 15 이후 구현 예정.

    Security:
        - JWT 토큰 필수 (Authorization: Bearer <token>)
        - Redis 세션 유효성 확인
        - role="admin" 확인
    """
    # Mock 응답 (테스트용)
    return {
        "id": tip_id,
        "title": tip_data.title or "Updated Title",
        "content": tip_data.content or "Updated content",
        "difficulty": tip_data.difficulty.value if tip_data.difficulty else "beginner",
        "category": tip_data.category or [],
        "updated_by": admin["email"],
        "message": f"Tip {tip_id} updated by {admin['email']}",
    }


@router.delete("/tips/{tip_id}", dependencies=[Depends(get_current_admin)])
@limiter.limit("5/minute")
async def delete_tip(
    request: Request,
    tip_id: str,
    admin: dict[str, Any] = Depends(get_current_admin),
) -> dict[str, str]:
    """
    관리자 전용: 팁 삭제

    Args:
        tip_id: 팁 ID
        admin: 현재 인증된 관리자

    Returns:
        삭제 확인 메시지

    Note:
        이 엔드포인트는 인증 테스트용 Mock 구현입니다.
        실제 DB 작업은 Day 15 이후 구현 예정.

    Security:
        - JWT 토큰 필수 (Authorization: Bearer <token>)
        - Redis 세션 유효성 확인
        - role="admin" 확인
    """
    # Mock 응답 (테스트용)
    return {
        "message": f"Tip {tip_id} deleted by {admin['email']}",
        "deleted_id": tip_id,
    }
