"""
Linux Daily Tips Backend - Database Configuration

This module handles database connection setup, session management,
and provides database utilities for the FastAPI application.
Supports both synchronous and asynchronous database operations.
"""

import os
import asyncio
from typing import AsyncGenerator, Optional, Dict, Any
from contextlib import asynccontextmanager
from functools import lru_cache

import asyncpg
from sqlalchemy import create_engine, MetaData, event, pool
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool, QueuePool

from .settings import get_settings


# =============================================================================
# DATABASE METADATA AND BASE MODEL
# =============================================================================

# Create base class for all ORM models
Base = declarative_base()

# Metadata for table creation and migrations
metadata = MetaData()


# =============================================================================
# DATABASE ENGINE CONFIGURATION
# =============================================================================

class DatabaseConfig:
    """Database configuration and connection management."""

    def __init__(self):
        """Initialize database configuration."""
        self.settings = get_settings()
        self._async_engine: Optional[AsyncEngine] = None
        self._sync_engine = None
        self._async_session_factory = None
        self._sync_session_factory = None

    @property
    def async_engine(self) -> AsyncEngine:
        """Get or create async database engine."""
        if self._async_engine is None:
            self._async_engine = self._create_async_engine()
        return self._async_engine

    @property
    def sync_engine(self):
        """Get or create sync database engine."""
        if self._sync_engine is None:
            self._sync_engine = self._create_sync_engine()
        return self._sync_engine

    def _create_async_engine(self) -> AsyncEngine:
        """Create and configure async database engine."""
        settings = self.settings

        # Engine configuration
        engine_config = {
            "url": settings.database_url,
            "echo": settings.debug and settings.log_level == "DEBUG",
            "echo_pool": settings.debug,
            "future": True,  # Use SQLAlchemy 2.0 style
            "pool_size": settings.db_pool_size,
            "max_overflow": settings.db_max_overflow,
            "pool_timeout": settings.db_pool_timeout,
            "pool_pre_ping": True,  # Validate connections before use
            "pool_recycle": 3600,   # Recycle connections every hour
        }

        # Use NullPool for testing to avoid connection issues
        if settings.is_testing:
            engine_config["poolclass"] = NullPool
        else:
            engine_config["poolclass"] = QueuePool

        engine = create_async_engine(**engine_config)

        # Add event listeners for connection handling
        self._setup_engine_events(engine.sync_engine)

        return engine

    def _create_sync_engine(self):
        """Create and configure sync database engine."""
        settings = self.settings

        # Convert async URL to sync URL
        sync_url = settings.database_url.replace(
            "postgresql+asyncpg://", "postgresql+psycopg2://"
        )

        engine_config = {
            "url": sync_url,
            "echo": settings.debug and settings.log_level == "DEBUG",
            "echo_pool": settings.debug,
            "future": True,
            "pool_size": settings.db_pool_size,
            "max_overflow": settings.db_max_overflow,
            "pool_timeout": settings.db_pool_timeout,
            "pool_pre_ping": True,
            "pool_recycle": 3600,
        }

        # Use NullPool for testing
        if settings.is_testing:
            engine_config["poolclass"] = NullPool
        else:
            engine_config["poolclass"] = QueuePool

        engine = create_engine(**engine_config)

        # Add event listeners
        self._setup_engine_events(engine)

        return engine

    def _setup_engine_events(self, engine):
        """Setup database engine event listeners."""

        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """Set database-specific settings on connection."""
            # For PostgreSQL, we can set session parameters here if needed
            if hasattr(dbapi_connection, "execute"):
                # Set timezone to UTC for consistency
                try:
                    cursor = dbapi_connection.cursor()
                    cursor.execute("SET timezone TO 'UTC'")
                    cursor.close()
                except Exception:
                    pass  # Ignore if setting fails

        @event.listens_for(engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            """Log database connection checkout in debug mode."""
            if self.settings.debug and self.settings.log_level == "DEBUG":
                print(f"Connection checked out: {id(dbapi_connection)}")

        @event.listens_for(engine, "checkin")
        def receive_checkin(dbapi_connection, connection_record):
            """Log database connection checkin in debug mode."""
            if self.settings.debug and self.settings.log_level == "DEBUG":
                print(f"Connection checked in: {id(dbapi_connection)}")

    @property
    def async_session_factory(self):
        """Get or create async session factory."""
        if self._async_session_factory is None:
            self._async_session_factory = async_sessionmaker(
                bind=self.async_engine,
                class_=AsyncSession,
                autoflush=True,
                autocommit=False,
                expire_on_commit=False  # Keep objects usable after commit
            )
        return self._async_session_factory

    @property
    def sync_session_factory(self):
        """Get or create sync session factory."""
        if self._sync_session_factory is None:
            self._sync_session_factory = sessionmaker(
                bind=self.sync_engine,
                autoflush=True,
                autocommit=False,
                expire_on_commit=False
            )
        return self._sync_session_factory

    async def create_database(self) -> None:
        """Create database if it doesn't exist."""
        settings = self.settings

        # Extract database name from URL
        db_name = settings.postgres_db

        # Create connection to postgres database (without specific db)
        admin_url = settings.database_url.rsplit('/', 1)[0] + '/postgres'

        try:
            conn = await asyncpg.connect(admin_url)

            # Check if database exists
            exists = await conn.fetchval(
                "SELECT 1 FROM pg_database WHERE datname = $1", db_name
            )

            if not exists:
                # Create database
                await conn.execute(f'CREATE DATABASE "{db_name}"')
                print(f"Database '{db_name}' created successfully")
            else:
                print(f"Database '{db_name}' already exists")

            await conn.close()

        except Exception as e:
            print(f"Error creating database: {e}")
            # Don't raise exception to allow application to continue

    async def create_tables(self) -> None:
        """Create all database tables."""
        async with self.async_engine.begin() as conn:
            # Import all models to ensure they're registered
            # This would typically be done in an __init__.py file
            # from app.models import *  # noqa

            await conn.run_sync(Base.metadata.create_all)
            print("Database tables created successfully")

    async def drop_tables(self) -> None:
        """Drop all database tables (use with caution!)."""
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            print("Database tables dropped successfully")

    async def check_connection(self) -> bool:
        """Check if database connection is working."""
        try:
            async with self.async_session_factory() as session:
                await session.execute("SELECT 1")
                return True
        except Exception as e:
            print(f"Database connection check failed: {e}")
            return False

    async def get_database_info(self) -> Dict[str, Any]:
        """Get database information and statistics."""
        try:
            async with self.async_session_factory() as session:
                # Get PostgreSQL version
                version_result = await session.execute("SELECT version()")
                version = version_result.scalar()

                # Get database size
                size_result = await session.execute(
                    "SELECT pg_size_pretty(pg_database_size(current_database()))"
                )
                size = size_result.scalar()

                # Get connection count
                connections_result = await session.execute(
                    """
                    SELECT count(*)
                    FROM pg_stat_activity
                    WHERE datname = current_database()
                    """
                )
                connections = connections_result.scalar()

                return {
                    "version": version,
                    "size": size,
                    "active_connections": connections,
                    "database_name": self.settings.postgres_db
                }
        except Exception as e:
            return {"error": str(e)}

    async def close(self) -> None:
        """Close database connections."""
        if self._async_engine:
            await self._async_engine.dispose()
        if self._sync_engine:
            self._sync_engine.dispose()


# =============================================================================
# GLOBAL DATABASE INSTANCE
# =============================================================================

@lru_cache()
def get_database() -> DatabaseConfig:
    """Get cached database configuration instance."""
    return DatabaseConfig()


# =============================================================================
# SESSION DEPENDENCY FUNCTIONS
# =============================================================================

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get async database session.

    This function is designed to be used with FastAPI's dependency injection.
    It provides a database session that automatically handles transactions
    and cleanup.
    """
    db = get_database()
    async with db.async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_session() -> Session:
    """
    Dependency function to get sync database session.

    Note: Prefer async sessions in FastAPI applications.
    This is provided for compatibility with synchronous code.
    """
    db = get_database()
    session = db.sync_session_factory()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@asynccontextmanager
async def get_session_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for database sessions.

    This provides an alternative way to get database sessions
    outside of FastAPI's dependency injection system.
    """
    db = get_database()
    async with db.async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


# =============================================================================
# DATABASE INITIALIZATION FUNCTIONS
# =============================================================================

async def init_database() -> None:
    """Initialize database connection and create tables."""
    db = get_database()

    print("Initializing database...")

    # Create database if it doesn't exist
    await db.create_database()

    # Check connection
    if not await db.check_connection():
        raise Exception("Failed to connect to database")

    # Create tables
    await db.create_tables()

    print("Database initialization completed successfully")


async def cleanup_database() -> None:
    """Cleanup database connections."""
    db = get_database()
    await db.close()
    print("Database connections closed")


# =============================================================================
# TRANSACTION UTILITIES
# =============================================================================

@asynccontextmanager
async def transaction() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for database transactions.

    Automatically handles commit/rollback based on whether
    an exception occurs within the context.
    """
    async with get_session_context() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "Base",
    "metadata",
    "DatabaseConfig",
    "get_database",
    "get_async_session",
    "get_sync_session",
    "get_session_context",
    "transaction",
    "init_database",
    "cleanup_database"
]