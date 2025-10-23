"""
API Rate Limiting 모듈

slowapi를 사용하여 Redis 기반 API 속도 제한을 구현합니다.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings


def _get_remote_address_or_default(request) -> str:
    """
    클라이언트 IP 주소 추출 (Proxy 헤더 지원)

    우선순위:
    1. X-Forwarded-For 헤더 (Nginx/Load Balancer)
    2. X-Real-IP 헤더 (Nginx)
    3. request.client.host (직접 연결)

    Args:
        request: FastAPI Request 객체

    Returns:
        클라이언트 IP 주소 (문자열)
    """
    # Proxy 헤더에서 IP 추출 (프로덕션 환경)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # X-Forwarded-For: client, proxy1, proxy2
        # 첫 번째 IP가 실제 클라이언트
        return forwarded.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    # 직접 연결 (개발 환경)
    return get_remote_address(request)


# Redis 기반 Rate Limiter 초기화
limiter = Limiter(
    key_func=_get_remote_address_or_default,
    storage_uri=settings.REDIS_URL,
    strategy="fixed-window",  # 고정 윈도우 전략 (간단하고 예측 가능)
    # strategy="moving-window"  # 이동 윈도우 (더 정확하지만 메모리 사용량 증가)
)
