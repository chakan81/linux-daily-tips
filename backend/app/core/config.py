"""
애플리케이션 설정 관리 모듈

Pydantic Settings V2를 사용하여 환경 변수를 타입 안전하게 관리합니다.
.env 파일에서 자동으로 환경 변수를 로드하고 검증합니다.
"""

import json
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    애플리케이션 전역 설정

    환경 변수는 .env 파일 또는 시스템 환경 변수에서 로드됩니다.
    우선순위: 시스템 환경 변수 > .env 파일 > 기본값
    """

    # 기본 애플리케이션 설정
    PROJECT_NAME: str = Field(
        default="Linux Daily Tips API",
        description="프로젝트 이름",
    )
    VERSION: str = Field(
        default="0.1.0",
        description="API 버전",
    )
    API_V1_STR: str = Field(
        default="/api/v1",
        description="API v1 URL 접두사",
    )
    ENVIRONMENT: str = Field(
        default="development",
        description="실행 환경 (development/staging/production)",
    )
    DEBUG: bool = Field(
        default=True,
        description="디버그 모드 활성화 여부",
    )

    # 데이터베이스 설정
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/linux_daily_tips",
        description="PostgreSQL 비동기 연결 URL",
    )

    # Redis 설정
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis 연결 URL",
    )

    # 보안 설정
    SECRET_KEY: str = Field(
        default="your-secret-key-here-change-in-production",
        description="JWT 토큰 서명용 시크릿 키 (최소 32자 이상)",
    )
    ALGORITHM: str = Field(
        default="HS256",
        description="JWT 토큰 암호화 알고리즘",
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="액세스 토큰 만료 시간 (분)",
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        description="리프레시 토큰 만료 시간 (일)",
    )

    # CORS 설정
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="CORS 허용 origin 목록",
    )

    # Cookie 보안 설정
    COOKIE_SECURE: bool = Field(
        default=False,
        description="Cookie Secure 플래그 (HTTPS only, 프로덕션에서 True)",
    )
    COOKIE_HTTPONLY: bool = Field(
        default=True,
        description="Cookie HttpOnly 플래그 (XSS 방어)",
    )
    COOKIE_SAMESITE: str = Field(
        default="lax",
        description="Cookie SameSite 정책 (CSRF 방어)",
    )

    # 데이터베이스 연결 풀 설정
    MAX_CONNECTIONS_COUNT: int = Field(
        default=10,
        description="데이터베이스 최대 연결 수",
    )
    MIN_CONNECTIONS_COUNT: int = Field(
        default=10,
        description="데이터베이스 최소 연결 수",
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        """
        CORS origins를 파싱합니다.

        환경 변수가 JSON 문자열 형태인 경우 파싱하여 리스트로 변환합니다.
        예: '["http://localhost:3000","http://localhost:8000"]'

        Args:
            v: CORS origins 값 (문자열 또는 리스트)

        Returns:
            파싱된 origin 리스트
        """
        if isinstance(v, str):
            try:
                # JSON 문자열을 리스트로 파싱
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                # JSON이 아닌 경우 쉼표로 구분된 문자열로 간주
                return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """
        시크릿 키 길이를 검증합니다.

        프로덕션 환경에서는 최소 32자 이상의 강력한 시크릿 키가 필요합니다.

        Args:
            v: 시크릿 키

        Returns:
            검증된 시크릿 키

        Raises:
            ValueError: 시크릿 키가 32자 미만인 경우
        """
        if len(v) < 32:
            raise ValueError("SECRET_KEY는 최소 32자 이상이어야 합니다.")
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # 정의되지 않은 환경 변수는 무시
    )

    @property
    def is_production(self) -> bool:
        """프로덕션 환경 여부를 반환합니다."""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_development(self) -> bool:
        """개발 환경 여부를 반환합니다."""
        return self.ENVIRONMENT.lower() == "development"

    @property
    def fastapi_kwargs(self) -> dict[str, Any]:
        """
        FastAPI 앱 초기화에 사용할 설정을 반환합니다.

        Returns:
            FastAPI 생성자에 전달할 키워드 인자 딕셔너리
        """
        return {
            "title": self.PROJECT_NAME,
            "version": self.VERSION,
            "docs_url": "/docs" if not self.is_production else None,
            "redoc_url": "/redoc" if not self.is_production else None,
            "openapi_url": f"{self.API_V1_STR}/openapi.json"
            if not self.is_production
            else None,
        }


# 전역 설정 인스턴스 생성
settings = Settings()
