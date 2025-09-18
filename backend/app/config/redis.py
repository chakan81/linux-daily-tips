"""
Linux Daily Tips Backend - Redis Configuration

This module handles Redis connection setup, session management,
and provides Redis utilities for caching, rate limiting, and
session storage in the FastAPI application.
"""

import json
import pickle
from typing import Any, Optional, Union, Dict, List
from functools import lru_cache
from contextlib import asynccontextmanager

import redis.asyncio as redis
from redis.asyncio import ConnectionPool, Redis
from redis.exceptions import (
    RedisError,
    ConnectionError,
    TimeoutError,
    RedisClusterException
)

from .settings import get_settings


# =============================================================================
# REDIS CONNECTION CONFIGURATION
# =============================================================================

class RedisConfig:
    """Redis configuration and connection management."""

    def __init__(self):
        """Initialize Redis configuration."""
        self.settings = get_settings()
        self._connection_pool: Optional[ConnectionPool] = None
        self._redis_client: Optional[Redis] = None

    @property
    def connection_pool(self) -> ConnectionPool:
        """Get or create Redis connection pool."""
        if self._connection_pool is None:
            self._connection_pool = self._create_connection_pool()
        return self._connection_pool

    @property
    def redis_client(self) -> Redis:
        """Get or create Redis client."""
        if self._redis_client is None:
            self._redis_client = Redis(connection_pool=self.connection_pool)
        return self._redis_client

    def _create_connection_pool(self) -> ConnectionPool:
        """Create and configure Redis connection pool."""
        settings = self.settings

        pool_config = {
            "host": settings.redis_host,
            "port": settings.redis_port,
            "db": settings.redis_db,
            "password": settings.redis_password,
            "max_connections": settings.redis_max_connections,
            "retry_on_timeout": settings.redis_retry_on_timeout,
            "decode_responses": True,  # Automatically decode responses to strings
            "encoding": "utf-8",
            "socket_timeout": 30,
            "socket_connect_timeout": 30,
            "socket_keepalive": True,
            "socket_keepalive_options": {},
        }

        # Remove None values
        pool_config = {k: v for k, v in pool_config.items() if v is not None}

        return ConnectionPool(**pool_config)

    async def ping(self) -> bool:
        """Test Redis connection."""
        try:
            response = await self.redis_client.ping()
            return response is True
        except Exception as e:
            print(f"Redis ping failed: {e}")
            return False

    async def get_info(self) -> Dict[str, Any]:
        """Get Redis server information."""
        try:
            info = await self.redis_client.info()
            return {
                "redis_version": info.get("redis_version", "Unknown"),
                "used_memory_human": info.get("used_memory_human", "Unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "total_connections_received": info.get("total_connections_received", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
            }
        except Exception as e:
            return {"error": str(e)}

    async def flush_database(self) -> bool:
        """Flush current Redis database (use with caution!)."""
        try:
            await self.redis_client.flushdb()
            return True
        except Exception as e:
            print(f"Redis flush failed: {e}")
            return False

    async def close(self) -> None:
        """Close Redis connections."""
        if self._redis_client:
            await self._redis_client.close()
        if self._connection_pool:
            await self._connection_pool.disconnect()


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
            print(f"Redis GET error for key '{key}': {e}")
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
            print(f"Redis SET error for key '{key}': {e}")
            return False

    async def delete(self, *keys: str) -> int:
        """Delete one or more keys from Redis."""
        try:
            return await self.redis.delete(*keys)
        except RedisError as e:
            print(f"Redis DELETE error for keys {keys}: {e}")
            return 0

    async def exists(self, *keys: str) -> int:
        """Check if keys exist in Redis."""
        try:
            return await self.redis.exists(*keys)
        except RedisError as e:
            print(f"Redis EXISTS error for keys {keys}: {e}")
            return 0

    async def expire(self, key: str, ttl: int) -> bool:
        """Set TTL for a key."""
        try:
            return await self.redis.expire(key, ttl)
        except RedisError as e:
            print(f"Redis EXPIRE error for key '{key}': {e}")
            return False

    async def ttl(self, key: str) -> int:
        """Get TTL for a key."""
        try:
            return await self.redis.ttl(key)
        except RedisError as e:
            print(f"Redis TTL error for key '{key}': {e}")
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
            print(f"Redis GET_JSON error for key '{key}': {e}")
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
            print(f"Redis SET_JSON error for key '{key}': {e}")
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
            print(f"Redis HGET error for key '{key}', field '{field}': {e}")
            return default

    async def hset(self, key: str, field: str, value: Any) -> bool:
        """Set hash field value."""
        try:
            result = await self.redis.hset(key, field, value)
            return result >= 0
        except RedisError as e:
            print(f"Redis HSET error for key '{key}', field '{field}': {e}")
            return False

    async def hgetall(self, key: str) -> Dict[str, str]:
        """Get all hash fields and values."""
        try:
            return await self.redis.hgetall(key)
        except RedisError as e:
            print(f"Redis HGETALL error for key '{key}': {e}")
            return {}

    async def hmset(self, key: str, mapping: Dict[str, Any]) -> bool:
        """Set multiple hash fields."""
        try:
            await self.redis.hmset(key, mapping)
            return True
        except RedisError as e:
            print(f"Redis HMSET error for key '{key}': {e}")
            return False

    # =============================================================================
    # LIST OPERATIONS
    # =============================================================================

    async def lpush(self, key: str, *values: Any) -> int:
        """Push values to left of list."""
        try:
            return await self.redis.lpush(key, *values)
        except RedisError as e:
            print(f"Redis LPUSH error for key '{key}': {e}")
            return 0

    async def rpush(self, key: str, *values: Any) -> int:
        """Push values to right of list."""
        try:
            return await self.redis.rpush(key, *values)
        except RedisError as e:
            print(f"Redis RPUSH error for key '{key}': {e}")
            return 0

    async def lpop(self, key: str) -> Optional[str]:
        """Pop value from left of list."""
        try:
            return await self.redis.lpop(key)
        except RedisError as e:
            print(f"Redis LPOP error for key '{key}': {e}")
            return None

    async def rpop(self, key: str) -> Optional[str]:
        """Pop value from right of list."""
        try:
            return await self.redis.rpop(key)
        except RedisError as e:
            print(f"Redis RPOP error for key '{key}': {e}")
            return None

    async def lrange(self, key: str, start: int = 0, end: int = -1) -> List[str]:
        """Get list range."""
        try:
            return await self.redis.lrange(key, start, end)
        except RedisError as e:
            print(f"Redis LRANGE error for key '{key}': {e}")
            return []

    async def llen(self, key: str) -> int:
        """Get list length."""
        try:
            return await self.redis.llen(key)
        except RedisError as e:
            print(f"Redis LLEN error for key '{key}': {e}")
            return 0

    # =============================================================================
    # SET OPERATIONS
    # =============================================================================

    async def sadd(self, key: str, *members: Any) -> int:
        """Add members to set."""
        try:
            return await self.redis.sadd(key, *members)
        except RedisError as e:
            print(f"Redis SADD error for key '{key}': {e}")
            return 0

    async def srem(self, key: str, *members: Any) -> int:
        """Remove members from set."""
        try:
            return await self.redis.srem(key, *members)
        except RedisError as e:
            print(f"Redis SREM error for key '{key}': {e}")
            return 0

    async def smembers(self, key: str) -> set:
        """Get all set members."""
        try:
            return await self.redis.smembers(key)
        except RedisError as e:
            print(f"Redis SMEMBERS error for key '{key}': {e}")
            return set()

    async def sismember(self, key: str, member: Any) -> bool:
        """Check if member is in set."""
        try:
            return await self.redis.sismember(key, member)
        except RedisError as e:
            print(f"Redis SISMEMBER error for key '{key}': {e}")
            return False

    # =============================================================================
    # RATE LIMITING
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
            print(f"Rate limit check error: {e}")
            # Fail open - allow request if Redis is down
            return True, limit, current_time + window


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
            print(f"Cache clear pattern error: {e}")
            return 0


# =============================================================================
# GLOBAL REDIS INSTANCE
# =============================================================================

@lru_cache()
def get_redis_config() -> RedisConfig:
    """Get cached Redis configuration instance."""
    return RedisConfig()


@lru_cache()
def get_redis_client() -> RedisClient:
    """Get Redis client instance."""
    config = get_redis_config()
    return RedisClient(config.redis_client)


@lru_cache()
def get_redis_cache() -> RedisCache:
    """Get Redis cache instance."""
    client = get_redis_client()
    settings = get_settings()
    return RedisCache(client, default_ttl=settings.cache_ttl)


# =============================================================================
# DEPENDENCY FUNCTIONS
# =============================================================================

async def get_redis() -> RedisClient:
    """Dependency function to get Redis client."""
    return get_redis_client()


async def get_cache() -> RedisCache:
    """Dependency function to get Redis cache."""
    return get_redis_cache()


# =============================================================================
# INITIALIZATION AND CLEANUP
# =============================================================================

async def init_redis() -> None:
    """Initialize Redis connection."""
    config = get_redis_config()

    print("Initializing Redis connection...")

    if not await config.ping():
        raise Exception("Failed to connect to Redis")

    info = await config.get_info()
    print(f"Redis connected successfully - Version: {info.get('redis_version', 'Unknown')}")


async def cleanup_redis() -> None:
    """Cleanup Redis connections."""
    config = get_redis_config()
    await config.close()
    print("Redis connections closed")


# =============================================================================
# CONTEXT MANAGER
# =============================================================================

@asynccontextmanager
async def redis_transaction():
    """Context manager for Redis transactions."""
    client = get_redis_client()
    pipe = client.redis.pipeline()

    try:
        yield pipe
        await pipe.execute()
    except Exception:
        await pipe.reset()
        raise


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "RedisConfig",
    "RedisClient",
    "RedisCache",
    "get_redis_config",
    "get_redis_client",
    "get_redis_cache",
    "get_redis",
    "get_cache",
    "init_redis",
    "cleanup_redis",
    "redis_transaction"
]