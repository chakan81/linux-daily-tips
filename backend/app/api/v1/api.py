"""
API v1 라우터 통합

모든 v1 엔드포인트를 통합하여 main.py에 등록합니다.
엔드포인트 추가 시 이 파일에서 include_router를 호출하여 등록합니다.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import admin, auth, health, tips

# API v1 메인 라우터
api_router = APIRouter()

# 헬스 체크 엔드포인트 (프리픽스 없음)
# /api/v1/health로 접근
api_router.include_router(health.router, tags=["health"])

# Tips 엔드포인트
# /api/v1/tips/... 로 접근
api_router.include_router(tips.router, prefix="/tips", tags=["tips"])

# Admin 엔드포인트
# /api/v1/admin/... 로 접근
api_router.include_router(admin.router, tags=["admin"])

# Auth 엔드포인트 (Google OAuth 2.0)
# /api/v1/auth/... 로 접근
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# TODO: Day 15+에서 추가될 엔드포인트들
# api_router.include_router(terminal.router, prefix="/terminal", tags=["terminal"])
