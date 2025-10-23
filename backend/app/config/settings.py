"""
Linux Daily Tips Backend - Application Settings Configuration

This module defines the configuration settings for the FastAPI application,
including environment variables, database settings, security configurations,
and third-party service integrations.
"""

import os
from typing import List, Optional, Any, Dict
from pydantic import field_validator, Field
from pydantic_settings import BaseSettings
from pydantic.networks import AnyHttpUrl
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    This class uses Pydantic BaseSettings to automatically load and validate
    configuration from environment variables with appropriate type conversion
    and validation.
    """

    # =============================================================================
    # APPLICATION INFORMATION
    # =============================================================================
    app_name: str = Field(default="Linux Daily Tips API")
    app_version: str = Field(default="1.0.0")
    description: str = Field(
        default="Backend API for Linux Daily Tips educational platform"
    )

    # =============================================================================
    # ENVIRONMENT CONFIGURATION
    # =============================================================================
    environment: str = Field(default="development")
    debug: bool = Field(default=True)
    log_level: str = Field(default="DEBUG")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level is one of the standard levels."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()

    # =============================================================================
    # SERVER CONFIGURATION
    # =============================================================================
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    reload: bool = Field(default=True)
    workers: int = Field(default=1)

    @field_validator("port")
    @classmethod
    def validate_port(cls, v):
        """Validate port is in valid range."""
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v

    # =============================================================================
    # DATABASE CONFIGURATION
    # =============================================================================
    database_url: str
    postgres_db: str
    postgres_user: str
    postgres_password: str
    database_host: str = Field(default="localhost")
    database_port: int = Field(default=5432)

    # Database Pool Configuration
    db_pool_size: int = Field(default=10)
    db_max_overflow: int = Field(default=20)
    db_pool_timeout: int = Field(default=30)

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v):
        """Validate database URL format."""
        if not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError("Database URL must be a valid PostgreSQL connection string")
        return v

    # =============================================================================
    # REDIS CONFIGURATION
    # =============================================================================
    redis_url: str
    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)
    redis_password: Optional[str] = Field(default=None)
    redis_db: int = Field(default=0)

    # Redis Connection Pool Configuration
    redis_max_connections: int = Field(default=10)
    redis_retry_on_timeout: bool = Field(default=True)

    @field_validator("redis_port")
    @classmethod
    def validate_redis_port(cls, v):
        """Validate Redis port is in valid range."""
        if not 1 <= v <= 65535:
            raise ValueError("Redis port must be between 1 and 65535")
        return v

    # =============================================================================
    # SECURITY CONFIGURATION
    # =============================================================================
    secret_key: str
    jwt_secret_key: str
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_token_expire_minutes: int = Field(default=30)
    jwt_refresh_token_expire_days: int = Field(default=7)

    @field_validator("secret_key", "jwt_secret_key")
    @classmethod
    def validate_secrets(cls, v):
        """Validate secrets are not default values in production."""
        if "production" in os.getenv("ENVIRONMENT", "").lower():
            if "dev" in v.lower() or "change" in v.lower() or len(v) < 32:
                raise ValueError("Production secrets must be secure and properly configured")
        return v

    # =============================================================================
    # CORS CONFIGURATION
    # =============================================================================
    cors_origins: List[str] = Field(default=["http://localhost:3000"])
    cors_credentials: bool = Field(default=True)
    cors_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    )
    cors_headers: List[str] = Field(default=["*"])

    @field_validator("cors_origins", mode="before")
    @classmethod
    def validate_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("cors_methods", mode="before")
    @classmethod
    def validate_cors_methods(cls, v):
        """Parse CORS methods from string or list."""
        if isinstance(v, str):
            return [method.strip() for method in v.split(",")]
        return v

    @field_validator("cors_headers", mode="before")
    @classmethod
    def validate_cors_headers(cls, v):
        """Parse CORS headers from string or list."""
        if isinstance(v, str):
            return [header.strip() for header in v.split(",")]
        return v

    # =============================================================================
    # LLM API CONFIGURATION
    # =============================================================================
    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(default=None)
    openai_model: str = Field(default="gpt-4")
    openai_max_tokens: int = Field(default=2000)
    openai_temperature: float = Field(default=0.7)

    # Anthropic Configuration
    anthropic_api_key: Optional[str] = Field(default=None)
    anthropic_model: str = Field(default="claude-3-sonnet-20240229")
    anthropic_max_tokens: int = Field(default=2000)

    @field_validator("openai_temperature")
    @classmethod
    def validate_openai_temperature(cls, v):
        """Validate OpenAI temperature is in valid range."""
        if not 0 <= v <= 2:
            raise ValueError("OpenAI temperature must be between 0 and 2")
        return v

    # =============================================================================
    # TERMINAL EMULATOR CONFIGURATION
    # =============================================================================
    terminal_timeout: int = Field(default=30)
    terminal_max_memory: str = Field(default="512m")
    terminal_max_cpu: str = Field(default="0.5")
    terminal_max_sessions: int = Field(default=100)
    terminal_container_prefix: str = Field(default="linuxtips_terminal_")
    docker_host: str = Field(default="unix:///var/run/docker.sock")

    # =============================================================================
    # RATE LIMITING CONFIGURATION
    # =============================================================================
    rate_limit_requests: int = Field(default=100)
    rate_limit_period: int = Field(default=60)
    rate_limit_redis_key_prefix: str = Field(default="ratelimit:")

    # =============================================================================
    # ADMIN CONFIGURATION
    # =============================================================================
    admin_email: str = Field(default="admin@linuxtips.dev")
    admin_password: str
    admin_username: str = Field(default="admin")

    # =============================================================================
    # EMAIL CONFIGURATION
    # =============================================================================
    smtp_host: str = Field(default="localhost")
    smtp_port: int = Field(default=587)
    smtp_username: Optional[str] = Field(default=None)
    smtp_password: Optional[str] = Field(default=None)
    smtp_use_tls: bool = Field(default=True)
    smtp_from: str = Field(default="noreply@linuxtips.dev")

    # =============================================================================
    # GOOGLE ADSENSE CONFIGURATION
    # =============================================================================
    google_adsense_client_id: Optional[str] = Field(default=None)
    google_adsense_publisher_id: Optional[str] = Field(default=None)
    adsense_enabled: bool = Field(default=False)

    # =============================================================================
    # MONITORING & ANALYTICS CONFIGURATION
    # =============================================================================
    sentry_dsn: Optional[str] = Field(default=None)
    sentry_environment: str = Field(default="development")
    posthog_api_key: Optional[str] = Field(default=None)
    posthog_host: str = Field(default="https://app.posthog.com")

    # =============================================================================
    # FILE UPLOAD CONFIGURATION
    # =============================================================================
    max_file_size: int = Field(default=10485760)  # 10MB
    allowed_file_types: List[str] = Field(
        default=[".txt", ".md", ".json", ".yaml", ".yml"]
    )
    upload_dir: str = Field(default="uploads/")

    @field_validator("allowed_file_types", mode="before")
    @classmethod
    def validate_allowed_file_types(cls, v):
        """Parse allowed file types from string or list."""
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v

    # =============================================================================
    # CACHE CONFIGURATION
    # =============================================================================
    cache_enabled: bool = Field(default=True)
    cache_ttl: int = Field(default=3600)  # 1 hour
    cache_max_size: int = Field(default=1000)

    # =============================================================================
    # LOGGING CONFIGURATION
    # =============================================================================
    log_file: str = Field(default="logs/app.log")
    log_rotation: str = Field(default="daily")
    log_retention_days: int = Field(default=30)
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # =============================================================================
    # COMPUTED PROPERTIES
    # =============================================================================
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment.lower() in ("test", "testing")

    @property
    def database_config(self) -> Dict[str, Any]:
        """Get database configuration dictionary."""
        return {
            "url": self.database_url,
            "pool_size": self.db_pool_size,
            "max_overflow": self.db_max_overflow,
            "pool_timeout": self.db_pool_timeout,
        }

    @property
    def redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration dictionary."""
        return {
            "url": self.redis_url,
            "host": self.redis_host,
            "port": self.redis_port,
            "password": self.redis_password,
            "db": self.redis_db,
            "max_connections": self.redis_max_connections,
            "retry_on_timeout": self.redis_retry_on_timeout,
        }

    @property
    def jwt_config(self) -> Dict[str, Any]:
        """Get JWT configuration dictionary."""
        return {
            "secret_key": self.jwt_secret_key,
            "algorithm": self.jwt_algorithm,
            "access_token_expire_minutes": self.jwt_access_token_expire_minutes,
            "refresh_token_expire_days": self.jwt_refresh_token_expire_days,
        }

    # =============================================================================
    # PYDANTIC CONFIGURATION
    # =============================================================================
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",  # 정의되지 않은 환경 변수 무시
        "arbitrary_types_allowed": True,
        "validate_assignment": True,
        "use_enum_values": True,
    }


@lru_cache()
def get_settings() -> Settings:
    """
    Create and cache application settings instance.

    This function uses LRU cache to ensure settings are loaded once
    and reused throughout the application lifecycle.

    Returns:
        Settings: The configured settings instance
    """
    return Settings()


# Convenience function for accessing settings
def get_config() -> Settings:
    """
    Get the current application configuration.

    This is an alias for get_settings() to provide a more intuitive API.

    Returns:
        Settings: The configured settings instance
    """
    return get_settings()


# Export commonly used settings
__all__ = [
    "Settings",
    "get_settings",
    "get_config"
]