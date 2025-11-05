"""
캐시 서비스 모듈

CacheService와 CustomJSONEncoder를 재export하여 backward compatibility를 보장합니다.

사용법:
    from app.core.cache import CacheService, CustomJSONEncoder
"""

from app.core.cache.cache_service import CacheService
from app.core.cache.redis_serialization import CustomJSONEncoder

__all__ = ["CacheService", "CustomJSONEncoder"]
