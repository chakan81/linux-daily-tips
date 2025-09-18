"""
Linux Daily Tips Backend - Configuration Module

This module provides centralized configuration management for the FastAPI application,
including settings, database connections, Redis caching, and other infrastructure components.
"""

from .settings import Settings, get_settings, get_config
from .database import (
    Base,
    metadata,
    DatabaseConfig,
    get_database,
    get_async_session,
    get_sync_session,
    get_session_context,
    transaction,
    init_database,
    cleanup_database
)
from .redis import (
    RedisConfig,
    RedisClient,
    RedisCache,
    get_redis_config,
    get_redis_client,
    get_redis_cache,
    get_redis,
    get_cache,
    init_redis,
    cleanup_redis,
    redis_transaction
)

# =============================================================================
# CENTRALIZED INITIALIZATION AND CLEANUP
# =============================================================================

async def init_all() -> None:
    """Initialize all configuration components."""
    print("Initializing application configuration...")

    # Initialize database
    await init_database()

    # Initialize Redis
    await init_redis()

    print("All configuration components initialized successfully")


async def cleanup_all() -> None:
    """Cleanup all configuration components."""
    print("Cleaning up application configuration...")

    # Cleanup database connections
    await cleanup_database()

    # Cleanup Redis connections
    await cleanup_redis()

    print("All configuration components cleaned up successfully")


# =============================================================================
# HEALTH CHECK UTILITIES
# =============================================================================

async def check_health() -> dict:
    """Check health of all configuration components."""
    health_status = {
        "status": "healthy",
        "components": {}
    }

    # Check database health
    try:
        db = get_database()
        db_healthy = await db.check_connection()
        db_info = await db.get_database_info()

        health_status["components"]["database"] = {
            "status": "healthy" if db_healthy else "unhealthy",
            "info": db_info if db_healthy else {"error": "Connection failed"}
        }
    except Exception as e:
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "info": {"error": str(e)}
        }

    # Check Redis health
    try:
        redis_config = get_redis_config()
        redis_healthy = await redis_config.ping()
        redis_info = await redis_config.get_info() if redis_healthy else {}

        health_status["components"]["redis"] = {
            "status": "healthy" if redis_healthy else "unhealthy",
            "info": redis_info if redis_healthy else {"error": "Connection failed"}
        }
    except Exception as e:
        health_status["components"]["redis"] = {
            "status": "unhealthy",
            "info": {"error": str(e)}
        }

    # Update overall status
    component_statuses = [
        comp["status"] for comp in health_status["components"].values()
    ]
    if any(status == "unhealthy" for status in component_statuses):
        health_status["status"] = "unhealthy"

    return health_status


# =============================================================================
# CONFIGURATION SUMMARY
# =============================================================================

def get_config_summary() -> dict:
    """Get a summary of current configuration settings."""
    settings = get_settings()

    return {
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "environment": settings.environment,
        "debug": settings.debug,
        "log_level": settings.log_level,
        "database": {
            "host": settings.database_host,
            "port": settings.database_port,
            "database": settings.postgres_db,
        },
        "redis": {
            "host": settings.redis_host,
            "port": settings.redis_port,
            "db": settings.redis_db,
        },
        "security": {
            "jwt_algorithm": settings.jwt_algorithm,
            "jwt_access_token_expire_minutes": settings.jwt_access_token_expire_minutes,
        },
        "cors": {
            "origins": settings.cors_origins,
            "credentials": settings.cors_credentials,
        },
        "features": {
            "cache_enabled": settings.cache_enabled,
            "adsense_enabled": settings.adsense_enabled,
        }
    }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Settings
    "Settings",
    "get_settings",
    "get_config",

    # Database
    "Base",
    "metadata",
    "DatabaseConfig",
    "get_database",
    "get_async_session",
    "get_sync_session",
    "get_session_context",
    "transaction",
    "init_database",
    "cleanup_database",

    # Redis
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
    "redis_transaction",

    # Centralized functions
    "init_all",
    "cleanup_all",
    "check_health",
    "get_config_summary",
]