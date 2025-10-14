"""
Pydantic 스키마 패키지

API 요청/응답 데이터 검증 스키마를 관리합니다.

Available Schemas:
- Tip: 일일 팁 관련 스키마 (TipCreate, TipUpdate, Tip, TipList)
- User: 관리자 사용자 스키마 (UserCreate, UserUpdate, User, UserLogin, Token)
"""

from app.schemas.tip import Tip, TipCreate, TipList, TipUpdate
from app.schemas.user import (
    Token,
    TokenPayload,
    User,
    UserCreate,
    UserLogin,
    UserUpdate,
)

__all__ = [
    # Tip schemas
    "Tip",
    "TipCreate",
    "TipUpdate",
    "TipList",
    # User schemas
    "User",
    "UserCreate",
    "UserUpdate",
    "UserLogin",
    "Token",
    "TokenPayload",
]
