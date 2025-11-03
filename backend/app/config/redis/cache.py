"""
Redis Cache Module

This module provides caching utilities with TTL support and pattern-based clearing.
"""

import logging
from typing import Any, Optional

from redis.exceptions import RedisError

from .client import RedisClient

logger = logging.getLogger(__name__)


# =============================================================================
# CACHE UTILITIES
# =============================================================================

class RedisCache:
    """Redis-based cache with TTL support."""

    def __init__(self, client: RedisClient, default_ttl: int = 3600):
        """Initialize cache with Redis client."""
        self.client = client
        self.default_ttl = default_ttl

    async def get(self, key: str) -> Any:
        """Get cached value."""
        return await self.client.get_json(key)

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set cached value with TTL."""
        ttl = ttl or self.default_ttl
        return await self.client.set_json(key, value, ttl=ttl)

    async def delete(self, key: str) -> bool:
        """Delete cached value."""
        result = await self.client.delete(key)
        return result > 0

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        try:
            keys = []
            async for key in self.client.redis.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                return await self.client.delete(*keys)
            return 0
        except RedisError as e:
            logger.error(f"Cache clear pattern error: {e}", exc_info=True)
            return 0


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "RedisCache",
]
