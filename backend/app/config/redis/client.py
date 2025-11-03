"""
Redis Client Operations Module

This module provides a wrapper around Redis client with enhanced utilities
for basic operations, JSON handling, hash operations, list operations, and set operations.
"""

import json
import logging
from typing import Any, Optional, Dict, List

from redis.asyncio import Redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


# =============================================================================
# REDIS CLIENT WRAPPER
# =============================================================================

class RedisClient:
    """Enhanced Redis client with additional utilities."""

    def __init__(self, redis_instance: Redis):
        """Initialize Redis client wrapper."""
        self.redis = redis_instance

    # =============================================================================
    # BASIC OPERATIONS
    # =============================================================================

    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from Redis with optional default."""
        try:
            value = await self.redis.get(key)
            return value if value is not None else default
        except RedisError as e:
            logger.error(f"Redis GET error for key '{key}': {e}")
            return default

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        nx: bool = False,
        xx: bool = False
    ) -> bool:
        """
        Set value in Redis with optional TTL and conditions.

        Args:
            key: Redis key
            value: Value to store
            ttl: Time to live in seconds
            nx: Only set if key doesn't exist
            xx: Only set if key exists

        Returns:
            True if set successfully, False otherwise
        """
        try:
            return await self.redis.set(key, value, ex=ttl, nx=nx, xx=xx)
        except RedisError as e:
            logger.error(f"Redis SET error for key '{key}': {e}")
            return False

    async def delete(self, *keys: str) -> int:
        """Delete one or more keys from Redis."""
        try:
            return await self.redis.delete(*keys)
        except RedisError as e:
            logger.error(f"Redis DELETE error for keys {keys}: {e}")
            return 0

    async def exists(self, *keys: str) -> int:
        """Check if keys exist in Redis."""
        try:
            return await self.redis.exists(*keys)
        except RedisError as e:
            logger.error(f"Redis EXISTS error for keys {keys}: {e}")
            return 0

    async def expire(self, key: str, ttl: int) -> bool:
        """Set TTL for a key."""
        try:
            return await self.redis.expire(key, ttl)
        except RedisError as e:
            logger.error(f"Redis EXPIRE error for key '{key}': {e}")
            return False

    async def ttl(self, key: str) -> int:
        """Get TTL for a key."""
        try:
            return await self.redis.ttl(key)
        except RedisError as e:
            logger.error(f"Redis TTL error for key '{key}': {e}")
            return -1

    # =============================================================================
    # JSON OPERATIONS
    # =============================================================================

    async def get_json(self, key: str, default: Any = None) -> Any:
        """Get JSON value from Redis."""
        try:
            value = await self.redis.get(key)
            if value is not None:
                return json.loads(value)
            return default
        except (RedisError, json.JSONDecodeError) as e:
            logger.error(f"Redis GET_JSON error for key '{key}': {e}")
            return default

    async def set_json(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        nx: bool = False,
        xx: bool = False
    ) -> bool:
        """Set JSON value in Redis."""
        try:
            json_value = json.dumps(value, ensure_ascii=False)
            return await self.redis.set(key, json_value, ex=ttl, nx=nx, xx=xx)
        except (RedisError, json.JSONEncodeError) as e:
            logger.error(f"Redis SET_JSON error for key '{key}': {e}")
            return False

    # =============================================================================
    # HASH OPERATIONS
    # =============================================================================

    async def hget(self, key: str, field: str, default: Any = None) -> Any:
        """Get hash field value."""
        try:
            value = await self.redis.hget(key, field)
            return value if value is not None else default
        except RedisError as e:
            logger.error(f"Redis HGET error for key '{key}', field '{field}': {e}")
            return default

    async def hset(self, key: str, field: str, value: Any) -> bool:
        """Set hash field value."""
        try:
            result = await self.redis.hset(key, field, value)
            return result >= 0
        except RedisError as e:
            logger.error(f"Redis HSET error for key '{key}', field '{field}': {e}")
            return False

    async def hgetall(self, key: str) -> Dict[str, str]:
        """Get all hash fields and values."""
        try:
            return await self.redis.hgetall(key)
        except RedisError as e:
            logger.error(f"Redis HGETALL error for key '{key}': {e}")
            return {}

    async def hmset(self, key: str, mapping: Dict[str, Any]) -> bool:
        """Set multiple hash fields."""
        try:
            await self.redis.hmset(key, mapping)
            return True
        except RedisError as e:
            logger.error(f"Redis HMSET error for key '{key}': {e}")
            return False

    # =============================================================================
    # LIST OPERATIONS
    # =============================================================================

    async def lpush(self, key: str, *values: Any) -> int:
        """Push values to left of list."""
        try:
            return await self.redis.lpush(key, *values)
        except RedisError as e:
            logger.error(f"Redis LPUSH error for key '{key}': {e}")
            return 0

    async def rpush(self, key: str, *values: Any) -> int:
        """Push values to right of list."""
        try:
            return await self.redis.rpush(key, *values)
        except RedisError as e:
            logger.error(f"Redis RPUSH error for key '{key}': {e}")
            return 0

    async def lpop(self, key: str) -> Optional[str]:
        """Pop value from left of list."""
        try:
            return await self.redis.lpop(key)
        except RedisError as e:
            logger.error(f"Redis LPOP error for key '{key}': {e}")
            return None

    async def rpop(self, key: str) -> Optional[str]:
        """Pop value from right of list."""
        try:
            return await self.redis.rpop(key)
        except RedisError as e:
            logger.error(f"Redis RPOP error for key '{key}': {e}")
            return None

    async def lrange(self, key: str, start: int = 0, end: int = -1) -> List[str]:
        """Get list range."""
        try:
            return await self.redis.lrange(key, start, end)
        except RedisError as e:
            logger.error(f"Redis LRANGE error for key '{key}': {e}")
            return []

    async def llen(self, key: str) -> int:
        """Get list length."""
        try:
            return await self.redis.llen(key)
        except RedisError as e:
            logger.error(f"Redis LLEN error for key '{key}': {e}")
            return 0

    # =============================================================================
    # SET OPERATIONS
    # =============================================================================

    async def sadd(self, key: str, *members: Any) -> int:
        """Add members to set."""
        try:
            return await self.redis.sadd(key, *members)
        except RedisError as e:
            logger.error(f"Redis SADD error for key '{key}': {e}")
            return 0

    async def srem(self, key: str, *members: Any) -> int:
        """Remove members from set."""
        try:
            return await self.redis.srem(key, *members)
        except RedisError as e:
            logger.error(f"Redis SREM error for key '{key}': {e}")
            return 0

    async def smembers(self, key: str) -> set:
        """Get all set members."""
        try:
            return await self.redis.smembers(key)
        except RedisError as e:
            logger.error(f"Redis SMEMBERS error for key '{key}': {e}")
            return set()

    async def sismember(self, key: str, member: Any) -> bool:
        """Check if member is in set."""
        try:
            return await self.redis.sismember(key, member)
        except RedisError as e:
            logger.error(f"Redis SISMEMBER error for key '{key}': {e}")
            return False

    # =============================================================================
    # RATE LIMITING (Backward Compatibility)
    # =============================================================================

    async def rate_limit_check(
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
            logger.error(f"Rate limit check error: {e}")
            # Fail open - allow request if Redis is down
            return True, limit, current_time + window


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "RedisClient",
]
