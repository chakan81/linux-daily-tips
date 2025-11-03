"""
Linux Daily Tips Backend - Redis Module

This package provides Redis connection management, client operations,
caching utilities, and rate limiting for the FastAPI application.

The module is organized into sub-modules for better maintainability:
- connection: Connection pool and configuration management
- client: Redis client wrapper with enhanced utilities
- cache: Caching utilities with TTL support
- rate_limiter: Rate limiting using sliding window algorithm
"""

from functools import lru_cache
from contextlib import asynccontextmanager

from .connection import (
    RedisConfig,
    get_redis_config,
    init_redis,
    cleanup_redis,
)
from .client import RedisClient
from .cache import RedisCache
from .rate_limiter import RedisRateLimiter
from ..settings import get_settings


# =============================================================================
# GLOBAL INSTANCES
# =============================================================================

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


@lru_cache()
def get_redis_rate_limiter() -> RedisRateLimiter:
    """Get Redis rate limiter instance."""
    config = get_redis_config()
    return RedisRateLimiter(config.redis_client)


# =============================================================================
# DEPENDENCY FUNCTIONS
# =============================================================================

async def get_redis() -> RedisClient:
    """Dependency function to get Redis client."""
    return get_redis_client()


async def get_cache() -> RedisCache:
    """Dependency function to get Redis cache."""
    return get_redis_cache()


async def get_rate_limiter() -> RedisRateLimiter:
    """Dependency function to get Redis rate limiter."""
    return get_redis_rate_limiter()


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
# BACKWARDS COMPATIBILITY LAYER
# =============================================================================
# This section ensures existing imports from app.config.redis continue to work

# Re-export all classes for backward compatibility
__all__ = [
    # Connection management
    "RedisConfig",
    "get_redis_config",
    "init_redis",
    "cleanup_redis",
    # Client operations
    "RedisClient",
    "get_redis_client",
    # Caching
    "RedisCache",
    "get_redis_cache",
    # Rate limiting
    "RedisRateLimiter",
    "get_redis_rate_limiter",
    # Dependencies
    "get_redis",
    "get_cache",
    "get_rate_limiter",
    # Utilities
    "redis_transaction",
]
