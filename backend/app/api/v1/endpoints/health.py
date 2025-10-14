"""
헬스 체크 엔드포인트

서버 상태 및 버전 정보를 제공하는 헬스 체크 API입니다.
모니터링 및 로드밸런서 헬스 체크에 사용됩니다.
"""

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("/health", summary="헬스 체크", tags=["health"])
async def health_check():
    """
    서버 헬스 체크

    서버가 정상적으로 실행 중인지 확인합니다.
    로드밸런서 및 모니터링 시스템에서 사용됩니다.

    Returns:
        dict: 서버 상태 정보
            - status: 서버 상태 (healthy)
            - version: API 버전
            - environment: 실행 환경 (development/staging/production)

    Example:
        ```
        GET /api/v1/health

        Response:
        {
            "status": "healthy",
            "version": "0.1.0",
            "environment": "development"
        }
        ```

    Note:
        - 인증 불필요
        - 항상 200 OK 반환 (서버가 실행 중인 경우)
        - Day 10-11에서 DB 연결 상태 확인 추가 예정
    """
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


# TODO: Day 10-11에서 상세 헬스 체크 추가 예정
# @router.get("/health/detailed", summary="상세 헬스 체크")
# async def detailed_health_check(db: AsyncSession = Depends(get_db)):
#     """
#     상세 헬스 체크 (DB 연결 상태 포함)
#
#     서버뿐만 아니라 데이터베이스 및 Redis 연결 상태까지 확인합니다.
#
#     Returns:
#         dict: 상세 서버 상태 정보
#             - status: 전체 상태
#             - version: API 버전
#             - environment: 실행 환경
#             - database: 데이터베이스 연결 상태
#             - redis: Redis 연결 상태
#     """
#     db_status = "connected"
#     try:
#         await db.execute("SELECT 1")
#     except Exception:
#         db_status = "disconnected"
#
#     return {
#         "status": "healthy" if db_status == "connected" else "unhealthy",
#         "version": settings.VERSION,
#         "environment": settings.ENVIRONMENT,
#         "database": db_status,
#         "redis": "not_implemented",  # Day 14에서 구현
#     }
