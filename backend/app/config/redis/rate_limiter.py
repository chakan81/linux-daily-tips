"""
Redis Rate Limiter Module

This module provides rate limiting functionality using sliding window algorithm.
"""

import logging
from redis.asyncio import Redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


# =============================================================================
# RATE LIMITER
# =============================================================================

class RedisRateLimiter:
    """Rate limiter using Redis sorted sets and sliding window algorithm."""

    def __init__(self, redis_instance: Redis):
        """Initialize rate limiter with Redis instance."""
        self.redis = redis_instance

    async def check_rate_limit(
        self,
        key: str,
        limit: int,
        window: int,
        identifier: str = "default"
    ) -> tuple[bool, int, int]:
        """
        Check rate limit using sliding window.

        Args:
            key: Rate limit key prefix
            limit: Maximum requests allowed
            window: Time window in seconds
            identifier: Unique identifier (IP, user ID, etc.)

        Returns:
            Tuple of (allowed, remaining, reset_time)

        Fail-Open Policy:
            Redis 오류 발생 시 요청을 허용합니다. (가용성 우선)
            보안 우선 정책이 필요하면 False 반환으로 변경하세요.
        """
        import time

        current_time = int(time.time())
        rate_key = f"{key}:{identifier}"
        window_start = current_time - window

        try:
            pipe = self.redis.pipeline()

            # Remove old entries
            pipe.zremrangebyscore(rate_key, 0, window_start)

            # Count current requests
            pipe.zcard(rate_key)

            # Add current request
            pipe.zadd(rate_key, {str(current_time): current_time})

            # Set expiry
            pipe.expire(rate_key, window)

            results = await pipe.execute()
            current_requests = results[1]

            if current_requests < limit:
                remaining = limit - current_requests - 1
                return True, remaining, current_time + window
            else:
                return False, 0, current_time + window

        except RedisError as e:
            logger.error(f"Rate limit check error: {e}", exc_info=True)
            # Fail open - allow request if Redis is down
            return True, limit, current_time + window


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "RedisRateLimiter",
]
