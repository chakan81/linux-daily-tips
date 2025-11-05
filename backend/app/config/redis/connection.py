"""
Redis Connection Management Module

This module handles Redis connection pool creation, client management,
and health check operations.
"""

import logging
from typing import Any, Dict, Optional
from functools import lru_cache

from redis.asyncio import ConnectionPool, Redis

from ..settings import get_settings

logger = logging.getLogger(__name__)


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
            logger.error(f"Redis ping failed: {e}", exc_info=True)
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
            logger.error(f"Redis flush failed: {e}", exc_info=True)
            return False

    async def close(self) -> None:
        """Close Redis connections."""
        if self._redis_client:
            await self._redis_client.close()
        if self._connection_pool:
            await self._connection_pool.disconnect()


# =============================================================================
# GLOBAL REDIS CONFIG INSTANCE
# =============================================================================

@lru_cache()
def get_redis_config() -> RedisConfig:
    """Get cached Redis configuration instance."""
    return RedisConfig()


# =============================================================================
# INITIALIZATION AND CLEANUP
# =============================================================================

async def init_redis() -> None:
    """Initialize Redis connection."""
    config = get_redis_config()

    logger.info("Initializing Redis connection...")

    if not await config.ping():
        raise Exception("Failed to connect to Redis")

    info = await config.get_info()
    logger.info(f"Redis connected successfully - Version: {info.get('redis_version', 'Unknown')}")


async def cleanup_redis() -> None:
    """Cleanup Redis connections."""
    config = get_redis_config()
    await config.close()
    logger.info("Redis connections closed")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "RedisConfig",
    "get_redis_config",
    "init_redis",
    "cleanup_redis",
]
