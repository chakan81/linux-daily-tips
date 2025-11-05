"""
애플리케이션 설정 관리 모듈

Pydantic Settings V2를 사용하여 환경 변수를 타입 안전하게 관리합니다.
.env 파일에서 자동으로 환경 변수를 로드하고 검증합니다.
"""

import json
import logging
import secrets
from typing import Any, Literal

from cryptography.fernet import Fernet
from pydantic import Field, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# 로거 인스턴스
logger = logging.getLogger(__name__)


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
    LOG_LEVEL: str = Field(
        default="INFO",
        description="로그 레벨 (DEBUG/INFO/WARNING/ERROR/CRITICAL)",
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
    REDIS_ENCRYPTION_KEY: str = Field(
        default="",
        description="Redis 세션 데이터 암호화 키 (Fernet 키, 44자 Base64 인코딩)",
    )

    # 보안 설정
    SECRET_KEY: str = Field(
        default="",  # 빈 문자열로 설정하여 validator에서 처리
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
        description="CORS 허용 origin 목록 (개발 환경 기본값)",
    )

    # 프로덕션 전용 CORS Origins (환경 변수로 설정 필수)
    CORS_ORIGINS_PRODUCTION: list[str] = Field(
        default=[],
        description="프로덕션 CORS 허용 origin 목록 (예: https://yourdomain.com)",
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
    COOKIE_SAMESITE: Literal["lax", "strict", "none"] = Field(
        default="lax",
        description="Cookie SameSite 정책 (CSRF 방어)",
    )

    # Google OAuth 2.0 설정
    GOOGLE_CLIENT_ID: str = Field(
        default="",
        description="Google OAuth 2.0 Client ID",
    )
    GOOGLE_CLIENT_SECRET: str = Field(
        default="",
        description="Google OAuth 2.0 Client Secret",
    )
    GOOGLE_REDIRECT_URI: str = Field(
        default="http://localhost:8000/api/v1/auth/callback",
        description="Google OAuth 2.0 Redirect URI",
    )

    # HTTP 클라이언트 설정
    HTTP_TIMEOUT: int = Field(
        default=10,
        description="HTTP 요청 타임아웃 (초)",
    )
    HTTP_CONNECT_TIMEOUT: int = Field(
        default=5,
        description="HTTP 연결 타임아웃 (초)",
    )

    # 세션 설정
    SESSION_TTL: int = Field(
        default=3600,
        description="세션 만료 시간 (초, 기본 1시간)",
    )
    OAUTH_STATE_TTL: int = Field(
        default=600,
        description="OAuth State 만료 시간 (초, 기본 10분)",
    )

    # 프론트엔드 URL 설정
    FRONTEND_URL: str = Field(
        default="http://localhost:3000",
        description="프론트엔드 애플리케이션 URL (OAuth 리다이렉트용)",
    )
    ALLOWED_FRONTEND_URLS: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        description="허용된 프론트엔드 URL 화이트리스트 (보안: Open Redirect 방지)",
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

    @field_validator("CORS_ORIGINS", "CORS_ORIGINS_PRODUCTION", mode="before")
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
            # 빈 문자열은 빈 리스트로 변환
            if not v.strip():
                return []
            try:
                # JSON 문자열을 리스트로 파싱
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                # JSON이 아닌 경우 쉼표로 구분된 문자열로 간주
                return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v if v else []

    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def validate_secret_key(cls, v: str, info: ValidationInfo) -> str:
        """
        시크릿 키 검증 및 자동 생성

        - 프로덕션 환경: 환경 변수 필수, 최소 32자 이상
        - 개발 환경: 환경 변수 없으면 자동 생성 (보안 경고)

        Args:
            v: 시크릿 키
            info: ValidationInfo (환경 변수 접근용)

        Returns:
            검증된 또는 생성된 시크릿 키

        Raises:
            ValueError: 프로덕션에서 SECRET_KEY 미설정 또는 길이 부족
        """
        # 환경 변수 확인 (프로덕션 감지용)
        environment = info.data.get("ENVIRONMENT", "development").lower()
        is_production = environment == "production"

        # SECRET_KEY가 없거나 빈 문자열인 경우
        if not v or v == "":
            if is_production:
                raise ValueError(
                    "🚨 프로덕션 환경에서는 SECRET_KEY 환경 변수가 필수입니다. "
                    "최소 32자 이상의 강력한 시크릿 키를 설정하세요."
                )
            else:
                # 개발 환경: 안전한 랜덤 키 자동 생성
                generated_key = secrets.token_urlsafe(32)  # 43자 생성 (Base64 인코딩)
                logger.warning(
                    "SECRET_KEY 환경 변수 미설정. 개발용 임시 키 생성: %s... "
                    "프로덕션 배포 전 필수 설정!",
                    generated_key[:20]
                )
                return generated_key

        # SECRET_KEY가 제공된 경우 길이 검증
        if len(v) < 32:
            if is_production:
                raise ValueError(
                    "🚨 SECRET_KEY는 최소 32자 이상이어야 합니다. "
                    "현재 길이: {}자".format(len(v))
                )
            else:
                logger.warning(
                    "SECRET_KEY가 32자 미만입니다 (현재: %d자). "
                    "보안을 위해 최소 32자 이상의 키를 사용하세요.",
                    len(v)
                )
                # 개발 환경에서는 경고만 출력하고 진행

        return v

    @field_validator("REDIS_ENCRYPTION_KEY", mode="before")
    @classmethod
    def validate_encryption_key(cls, v: str, info: ValidationInfo) -> str:
        """
        Redis 암호화 키 검증 및 자동 생성

        - 프로덕션 환경: 환경 변수 필수 (Fernet 키 형식)
        - 개발 환경: 환경 변수 없으면 자동 생성

        Args:
            v: 암호화 키
            info: ValidationInfo (환경 변수 접근용)

        Returns:
            검증된 또는 생성된 Fernet 키

        Raises:
            ValueError: 프로덕션에서 REDIS_ENCRYPTION_KEY 미설정
        """
        environment = info.data.get("ENVIRONMENT", "development").lower()
        is_production = environment == "production"

        # 키가 없거나 빈 문자열인 경우
        if not v or v == "":
            if is_production:
                raise ValueError(
                    "🚨 프로덕션 환경에서는 REDIS_ENCRYPTION_KEY 환경 변수가 필수입니다. "
                    "Fernet.generate_key()로 생성한 키를 설정하세요."
                )
            else:
                # 개발 환경: Fernet 키 자동 생성
                generated_key = Fernet.generate_key().decode()
                logger.warning(
                    "REDIS_ENCRYPTION_KEY 환경 변수 미설정. "
                    "개발용 임시 암호화 키 생성: %s... "
                    "프로덕션 배포 전 필수 설정!",
                    generated_key[:20]
                )
                return generated_key

        # 키가 제공된 경우 Fernet 키 형식 검증
        try:
            Fernet(v.encode())  # 유효한 Fernet 키인지 확인
        except Exception:
            if is_production:
                raise ValueError(
                    "🚨 REDIS_ENCRYPTION_KEY가 유효하지 않습니다. "
                    "Fernet.generate_key()로 생성한 올바른 키를 설정하세요."
                )
            else:
                logger.warning(
                    "REDIS_ENCRYPTION_KEY가 유효하지 않습니다. "
                    "새로운 키를 자동 생성합니다."
                )
                return Fernet.generate_key().decode()

        return v

    @field_validator("ALLOWED_FRONTEND_URLS", mode="before")
    @classmethod
    def parse_allowed_frontend_urls(cls, v: Any) -> list[str]:
        """
        허용된 프론트엔드 URL 목록 파싱

        환경 변수가 JSON 문자열 형태인 경우 파싱하여 리스트로 변환합니다.

        Args:
            v: 프론트엔드 URL 목록 (문자열 또는 리스트)

        Returns:
            파싱된 URL 리스트
        """
        if isinstance(v, str):
            if not v.strip():
                return []
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                return [url.strip() for url in v.split(",") if url.strip()]
        return v if v else []

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
    def cors_origins_list(self) -> list[str]:
        """
        환경에 따른 CORS origins를 반환합니다.

        - 프로덕션: CORS_ORIGINS_PRODUCTION 사용 (환경 변수 필수)
        - 개발: CORS_ORIGINS 사용 (기본값 허용)

        Returns:
            list[str]: CORS 허용 origin 리스트

        Raises:
            ValueError: 프로덕션에서 CORS_ORIGINS_PRODUCTION 미설정
        """
        if self.is_production:
            if not self.CORS_ORIGINS_PRODUCTION:
                raise ValueError(
                    "🚨 프로덕션 환경에서는 CORS_ORIGINS_PRODUCTION 환경 변수가 필수입니다. "
                    "예: CORS_ORIGINS_PRODUCTION='[\"https://yourdomain.com\"]'"
                )
            return self.CORS_ORIGINS_PRODUCTION
        else:
            return self.CORS_ORIGINS

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
