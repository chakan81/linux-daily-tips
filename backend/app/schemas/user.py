"""
AdminUser Pydantic 스키마

관리자 사용자 API 요청/응답 스키마입니다.
- UserBase: 공통 필드
- UserCreate: 생성 요청 (비밀번호 평문)
- UserUpdate: 수정 요청
- UserInDB: 데이터베이스 내부 표현 (password_hash 포함)
- User: 응답 스키마 (비밀번호 제외)
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """
    User 공통 필드

    모든 User 스키마가 상속받는 베이스 클래스입니다.
    """

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern="^[a-zA-Z0-9_-]+$",
        description="사용자명 (3~50자, 영문/숫자/언더스코어/하이픈만 허용)",
        examples=["admin"],
    )

    email: EmailStr = Field(
        ...,
        description="이메일 주소",
        examples=["admin@example.com"],
    )

    is_active: bool = Field(
        default=True,
        description="계정 활성화 여부",
    )

    is_superuser: bool = Field(
        default=False,
        description="슈퍼유저 권한",
    )


class UserCreate(UserBase):
    """
    User 생성 요청 스키마

    새로운 관리자 계정을 생성할 때 사용합니다.
    비밀번호는 평문으로 전송되며, 서버에서 bcrypt로 해싱합니다.
    """

    password: str = Field(
        ...,
        max_length=100,
        description="비밀번호 (8~100자, 최소 1개의 대문자, 소문자, 숫자 포함 권장)",
        examples=["SecurePassword123!"],
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        비밀번호 강도 검증

        최소 8자 이상이며, 대문자, 소문자, 숫자를 포함해야 합니다.
        """
        if len(v) < 8:
            raise ValueError("비밀번호는 최소 8자 이상이어야 합니다")

        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)

        if not (has_upper and has_lower and has_digit):
            raise ValueError(
                "비밀번호는 최소 1개의 대문자, 소문자, 숫자를 포함해야 합니다"
            )

        return v


class UserUpdate(BaseModel):
    """
    User 수정 요청 스키마

    모든 필드가 선택적(Optional)이며, 제공된 필드만 업데이트됩니다.
    """

    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=50,
        pattern="^[a-zA-Z0-9_-]+$",
        description="사용자명",
    )

    email: EmailStr | None = Field(
        default=None,
        description="이메일 주소",
    )

    password: str | None = Field(
        default=None,
        max_length=100,
        description="새 비밀번호",
    )

    is_active: bool | None = Field(
        default=None,
        description="계정 활성화 여부",
    )

    is_superuser: bool | None = Field(
        default=None,
        description="슈퍼유저 권한",
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str | None) -> str | None:
        """비밀번호 강도 검증 (UserCreate와 동일)"""
        if v is None:
            return None

        if len(v) < 8:
            raise ValueError("비밀번호는 최소 8자 이상이어야 합니다")

        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)

        if not (has_upper and has_lower and has_digit):
            raise ValueError(
                "비밀번호는 최소 1개의 대문자, 소문자, 숫자를 포함해야 합니다"
            )

        return v


class UserInDB(UserBase):
    """
    데이터베이스 내부 표현

    SQLAlchemy 모델과 직접 매핑되는 스키마입니다.
    password_hash를 포함하지만, 절대 클라이언트에 반환하지 않습니다.
    """

    id: str = Field(
        ...,
        description="ULID 기반 ID (user_01JCAW0V1QQ9KZ2F3XHBP8TGNY)",
        examples=["user_01JCAW0V1QQ9KZ2F3XHBP8TGNY"],
    )

    password_hash: str = Field(
        ...,
        description="bcrypt 해시된 비밀번호",
    )

    last_login: datetime | None = Field(
        default=None,
        description="마지막 로그인 시각 (UTC)",
    )

    created_at: datetime = Field(
        ...,
        description="생성 시각 (UTC)",
    )

    updated_at: datetime = Field(
        ...,
        description="수정 시각 (UTC)",
    )

    model_config = ConfigDict(
        from_attributes=True,  # SQLAlchemy 모델에서 직접 변환 허용
    )


class User(UserBase):
    """
    User 응답 스키마 (클라이언트 반환용)

    API 응답으로 클라이언트에게 반환되는 스키마입니다.
    password_hash는 제외되어 보안을 유지합니다.
    UserBase의 공통 필드(username, email, is_active, is_superuser)를 상속받습니다.
    """

    id: str = Field(
        ...,
        description="ULID 기반 ID",
        examples=["user_01JCAW0V1QQ9KZ2F3XHBP8TGNY"],
    )

    last_login: datetime | None = Field(
        default=None,
        description="마지막 로그인 시각 (UTC)",
    )

    created_at: datetime = Field(
        ...,
        description="생성 시각 (UTC)",
    )

    updated_at: datetime = Field(
        ...,
        description="수정 시각 (UTC)",
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "user_01JCAW0V1QQ9KZ2F3XHBP8TGNY",
                "username": "admin",
                "email": "admin@example.com",
                "is_active": True,
                "is_superuser": True,
                "last_login": "2024-01-15T10:00:00Z",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-15T10:00:00Z",
            }
        },
    )


class UserLogin(BaseModel):
    """
    로그인 요청 스키마

    사용자명(또는 이메일)과 비밀번호로 로그인합니다.
    """

    username_or_email: str = Field(
        ...,
        description="사용자명 또는 이메일 주소",
        examples=["admin", "admin@example.com"],
    )

    password: str = Field(
        ...,
        description="비밀번호",
        examples=["SecurePassword123!"],
    )


class Token(BaseModel):
    """
    JWT 토큰 응답 스키마

    로그인 성공 시 반환되는 액세스 토큰과 리프레시 토큰입니다.
    """

    access_token: str = Field(
        ...,
        description="JWT 액세스 토큰",
    )

    refresh_token: str | None = Field(
        default=None,
        description="JWT 리프레시 토큰 (선택적)",
    )

    token_type: str = Field(
        default="bearer",
        description="토큰 타입",
    )

    expires_in: int = Field(
        ...,
        description="액세스 토큰 만료 시간 (초)",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
            }
        },
    )


class TokenPayload(BaseModel):
    """
    JWT 토큰 페이로드 스키마

    토큰 내부에 저장되는 사용자 정보입니다.
    """

    sub: str = Field(
        ...,
        description="사용자 ID (subject)",
    )

    exp: int = Field(
        ...,
        description="만료 시각 (Unix timestamp)",
    )

    iat: int = Field(
        ...,
        description="발급 시각 (Unix timestamp)",
    )

    type: str = Field(
        default="access",
        description="토큰 타입 (access/refresh)",
    )
