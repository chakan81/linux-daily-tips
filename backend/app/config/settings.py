"""
Linux Daily Tips Backend - Application Settings Configuration

This module defines the configuration settings for the FastAPI application,
including environment variables, database settings, security configurations,
and third-party service integrations.
"""

import os
from typing import List, Optional, Any, Dict
from pydantic import BaseSettings, validator, Field
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
    app_name: str = Field(default="Linux Daily Tips API", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    description: str = Field(
        default="Backend API for Linux Daily Tips educational platform",
        env="APP_DESCRIPTION"
    )

    # =============================================================================
    # ENVIRONMENT CONFIGURATION
    # =============================================================================
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    log_level: str = Field(default="DEBUG", env="LOG_LEVEL")

    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level is one of the standard levels."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()

    # =============================================================================
    # SERVER CONFIGURATION
    # =============================================================================
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    reload: bool = Field(default=True, env="AUTO_RESTART")
    workers: int = Field(default=1, env="BACKEND_WORKERS")

    @validator("port")
    def validate_port(cls, v):
        """Validate port is in valid range."""
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v

    # =============================================================================
    # DATABASE CONFIGURATION
    # =============================================================================
    database_url: str = Field(..., env="DATABASE_URL")
    postgres_db: str = Field(..., env="POSTGRES_DB")
    postgres_user: str = Field(..., env="POSTGRES_USER")
    postgres_password: str = Field(..., env="POSTGRES_PASSWORD")
    database_host: str = Field(default="localhost", env="DATABASE_HOST")
    database_port: int = Field(default=5432, env="DATABASE_PORT")

    # Database Pool Configuration
    db_pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW")
    db_pool_timeout: int = Field(default=30, env="DB_POOL_TIMEOUT")

    @validator("database_url")
    def validate_database_url(cls, v):
        """Validate database URL format."""
        if not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError("Database URL must be a valid PostgreSQL connection string")
        return v

    # =============================================================================
    # REDIS CONFIGURATION
    # =============================================================================
    redis_url: str = Field(..., env="REDIS_URL")
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    redis_db: int = Field(default=0, env="REDIS_DB")

    # Redis Connection Pool Configuration
    redis_max_connections: int = Field(default=10, env="REDIS_MAX_CONNECTIONS")
    redis_retry_on_timeout: bool = Field(default=True, env="REDIS_RETRY_ON_TIMEOUT")

    @validator("redis_port")
    def validate_redis_port(cls, v):
        """Validate Redis port is in valid range."""
        if not 1 <= v <= 65535:
            raise ValueError("Redis port must be between 1 and 65535")
        return v

    # =============================================================================
    # SECURITY CONFIGURATION
    # =============================================================================
    secret_key: str = Field(..., env="SECRET_KEY")
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(
        default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    jwt_refresh_token_expire_days: int = Field(
        default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS"
    )

    @validator("secret_key", "jwt_secret_key")
    def validate_secrets(cls, v):
        """Validate secrets are not default values in production."""
        if "production" in os.getenv("ENVIRONMENT", "").lower():
            if "dev" in v.lower() or "change" in v.lower() or len(v) < 32:
                raise ValueError("Production secrets must be secure and properly configured")
        return v

    # =============================================================================
    # CORS CONFIGURATION
    # =============================================================================
    cors_origins: List[str] = Field(
        default=["http://localhost:3000"],
        env="CORS_ORIGINS"
    )
    cors_credentials: bool = Field(default=True, env="CORS_CREDENTIALS")
    cors_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        env="CORS_METHODS"
    )
    cors_headers: List[str] = Field(default=["*"], env="CORS_HEADERS")

    @validator("cors_origins", pre=True)
    def validate_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @validator("cors_methods", pre=True)
    def validate_cors_methods(cls, v):
        """Parse CORS methods from string or list."""
        if isinstance(v, str):
            return [method.strip() for method in v.split(",")]
        return v

    @validator("cors_headers", pre=True)
    def validate_cors_headers(cls, v):
        """Parse CORS headers from string or list."""
        if isinstance(v, str):
            return [header.strip() for header in v.split(",")]
        return v

    # =============================================================================
    # LLM API CONFIGURATION
    # =============================================================================
    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4", env="OPENAI_MODEL")
    openai_max_tokens: int = Field(default=2000, env="OPENAI_MAX_TOKENS")
    openai_temperature: float = Field(default=0.7, env="OPENAI_TEMPERATURE")

    # Anthropic Configuration
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(
        default="claude-3-sonnet-20240229", env="ANTHROPIC_MODEL"
    )
    anthropic_max_tokens: int = Field(default=2000, env="ANTHROPIC_MAX_TOKENS")

    @validator("openai_temperature")
    def validate_openai_temperature(cls, v):
        """Validate OpenAI temperature is in valid range."""
        if not 0 <= v <= 2:
            raise ValueError("OpenAI temperature must be between 0 and 2")
        return v

    # =============================================================================
    # TERMINAL EMULATOR CONFIGURATION
    # =============================================================================
    terminal_timeout: int = Field(default=30, env="TERMINAL_TIMEOUT")
    terminal_max_memory: str = Field(default="512m", env="TERMINAL_MAX_MEMORY")
    terminal_max_cpu: str = Field(default="0.5", env="TERMINAL_MAX_CPU")
    terminal_max_sessions: int = Field(default=100, env="TERMINAL_MAX_SESSIONS")
    terminal_container_prefix: str = Field(
        default="linuxtips_terminal_", env="TERMINAL_CONTAINER_PREFIX"
    )
    docker_host: str = Field(
        default="unix:///var/run/docker.sock", env="DOCKER_HOST"
    )

    # =============================================================================
    # RATE LIMITING CONFIGURATION
    # =============================================================================
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_period: int = Field(default=60, env="RATE_LIMIT_PERIOD")
    rate_limit_redis_key_prefix: str = Field(
        default="ratelimit:", env="RATE_LIMIT_REDIS_KEY_PREFIX"
    )

    # =============================================================================
    # ADMIN CONFIGURATION
    # =============================================================================
    admin_email: str = Field(default="admin@linuxtips.dev", env="ADMIN_EMAIL")
    admin_password: str = Field(..., env="ADMIN_PASSWORD")
    admin_username: str = Field(default="admin", env="ADMIN_USERNAME")

    # =============================================================================
    # EMAIL CONFIGURATION
    # =============================================================================
    smtp_host: str = Field(default="localhost", env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    smtp_use_tls: bool = Field(default=True, env="SMTP_USE_TLS")
    smtp_from: str = Field(default="noreply@linuxtips.dev", env="SMTP_FROM")

    # =============================================================================
    # GOOGLE ADSENSE CONFIGURATION
    # =============================================================================
    google_adsense_client_id: Optional[str] = Field(
        default=None, env="GOOGLE_ADSENSE_CLIENT_ID"
    )
    google_adsense_publisher_id: Optional[str] = Field(
        default=None, env="GOOGLE_ADSENSE_PUBLISHER_ID"
    )
    adsense_enabled: bool = Field(default=False, env="ADSENSE_ENABLED")

    # =============================================================================
    # MONITORING & ANALYTICS CONFIGURATION
    # =============================================================================
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    sentry_environment: str = Field(default="development", env="SENTRY_ENVIRONMENT")
    posthog_api_key: Optional[str] = Field(default=None, env="POSTHOG_API_KEY")
    posthog_host: str = Field(default="https://app.posthog.com", env="POSTHOG_HOST")

    # =============================================================================
    # FILE UPLOAD CONFIGURATION
    # =============================================================================
    max_file_size: int = Field(default=10485760, env="MAX_FILE_SIZE")  # 10MB
    allowed_file_types: List[str] = Field(
        default=[".txt", ".md", ".json", ".yaml", ".yml"],
        env="ALLOWED_FILE_TYPES"
    )
    upload_dir: str = Field(default="uploads/", env="UPLOAD_DIR")

    @validator("allowed_file_types", pre=True)
    def validate_allowed_file_types(cls, v):
        """Parse allowed file types from string or list."""
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v

    # =============================================================================
    # CACHE CONFIGURATION
    # =============================================================================
    cache_enabled: bool = Field(default=True, env="CACHE_ENABLED")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")  # 1 hour
    cache_max_size: int = Field(default=1000, env="CACHE_MAX_SIZE")

    # =============================================================================
    # LOGGING CONFIGURATION
    # =============================================================================
    log_file: str = Field(default="logs/app.log", env="LOG_FILE")
    log_rotation: str = Field(default="daily", env="LOG_ROTATION")
    log_retention_days: int = Field(default=30, env="LOG_RETENTION_DAYS")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
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
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

        # Allow arbitrary types for complex configurations
        arbitrary_types_allowed = True

        # Validate assignment to catch configuration changes
        validate_assignment = True

        # Use enum values instead of names
        use_enum_values = True


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