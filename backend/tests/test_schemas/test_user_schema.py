"""
User (AdminUser) Pydantic 스키마 테스트

테스트 항목:
- UserCreate, UserUpdate 필드 검증
- 비밀번호 강도 검증 validator
- 이메일 형식 검증 (EmailStr)
- username 패턴 검증 (영문/숫자/언더스코어/하이픈만 허용)
- from_attributes=True 동작 (ORM → Pydantic 변환)
- 보안: password_hash는 응답 스키마에서 제외
"""

import pytest
from pydantic import ValidationError

from app.models.user import AdminUser
from app.schemas.user import (
    User,
    UserCreate,
    UserInDB,
    UserLogin,
    UserUpdate,
)


@pytest.mark.unit
class TestUserBaseSchema:
    """UserBase 스키마 기본 검증 테스트"""

    def test_user_create_with_valid_data(self) -> None:
        """유효한 데이터로 UserCreate 생성"""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123",
        }
        user = UserCreate(**data)

        assert user.username == data["username"]
        assert user.email == data["email"]
        assert user.password == data["password"]
        assert user.is_active is True  # 기본값
        assert user.is_superuser is False  # 기본값

    def test_user_create_username_too_short(self) -> None:
        """username이 3자 미만일 경우 검증 실패"""
        data = {
            "username": "ab",  # 2자
            "email": "test@example.com",
            "password": "SecurePass123",
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**data)

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("username",) for e in errors)

    def test_user_create_username_invalid_pattern(self) -> None:
        """username에 허용되지 않는 문자 포함 시 검증 실패"""
        invalid_usernames = [
            "user name",  # 공백
            "user@name",  # @
            "user.name",  # 점
            "사용자",  # 한글
        ]

        for username in invalid_usernames:
            data = {
                "username": username,
                "email": "test@example.com",
                "password": "SecurePass123",
            }
            with pytest.raises(ValidationError):
                UserCreate(**data)

    def test_user_create_username_valid_patterns(self) -> None:
        """username에 허용되는 문자들"""
        valid_usernames = [
            "user123",
            "test-user",
            "test_user",
            "User-Name_123",
        ]

        for username in valid_usernames:
            data = {
                "username": username,
                "email": "test@example.com",
                "password": "SecurePass123",
            }
            user = UserCreate(**data)
            assert user.username == username

    def test_user_create_email_validation(self) -> None:
        """이메일 형식 검증 (EmailStr)"""
        invalid_emails = [
            "not-an-email",
            "missing@domain",
            "@example.com",
            "user@",
        ]

        for email in invalid_emails:
            data = {
                "username": "testuser",
                "email": email,
                "password": "SecurePass123",
            }
            with pytest.raises(ValidationError) as exc_info:
                UserCreate(**data)

            errors = exc_info.value.errors()
            assert any(e["loc"] == ("email",) for e in errors)


@pytest.mark.unit
class TestUserPasswordValidator:
    """비밀번호 강도 검증 validator 테스트"""

    def test_password_too_short(self) -> None:
        """비밀번호가 8자 미만일 경우 검증 실패"""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Short1",  # 6자
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**data)

        errors = exc_info.value.errors()
        assert any("최소 8자" in str(e["msg"]) for e in errors)

    def test_password_missing_uppercase(self) -> None:
        """대문자가 없을 경우 검증 실패"""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "lowercase123",  # 대문자 없음
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**data)

        errors = exc_info.value.errors()
        assert any("대문자" in str(e["msg"]) for e in errors)

    def test_password_missing_lowercase(self) -> None:
        """소문자가 없을 경우 검증 실패"""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "UPPERCASE123",  # 소문자 없음
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**data)

        errors = exc_info.value.errors()
        assert any("소문자" in str(e["msg"]) for e in errors)

    def test_password_missing_digit(self) -> None:
        """숫자가 없을 경우 검증 실패"""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "NoDigitsHere",  # 숫자 없음
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**data)

        errors = exc_info.value.errors()
        assert any("숫자" in str(e["msg"]) for e in errors)

    def test_password_valid_strength(self) -> None:
        """유효한 강도의 비밀번호"""
        valid_passwords = [
            "SecurePass123",
            "MyP@ssw0rd",
            "Test1234",
            "Abcdefg1",
        ]

        for password in valid_passwords:
            data = {
                "username": "testuser",
                "email": "test@example.com",
                "password": password,
            }
            user = UserCreate(**data)
            assert user.password == password

    def test_password_with_special_characters_allowed(self) -> None:
        """특수문자 포함 비밀번호도 허용"""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Secure!Pass@123#",
        }
        user = UserCreate(**data)
        assert user.password == data["password"]


@pytest.mark.unit
class TestUserUpdateSchema:
    """UserUpdate 스키마 테스트 (모든 필드 Optional)"""

    def test_user_update_all_fields_optional(self) -> None:
        """UserUpdate는 모든 필드가 선택적"""
        user_update = UserUpdate()

        assert user_update.username is None
        assert user_update.email is None
        assert user_update.password is None
        assert user_update.is_active is None
        assert user_update.is_superuser is None

    def test_user_update_partial_update(self) -> None:
        """일부 필드만 업데이트 가능"""
        data = {"email": "newemail@example.com"}
        user_update = UserUpdate(**data)

        assert user_update.email == "newemail@example.com"
        assert user_update.username is None
        assert user_update.password is None

    def test_user_update_password_validation(self) -> None:
        """UserUpdate의 password도 동일한 강도 검증 적용"""
        data = {"password": "weak"}
        with pytest.raises(ValidationError) as exc_info:
            UserUpdate(**data)

        errors = exc_info.value.errors()
        assert any("최소 8자" in str(e["msg"]) for e in errors)


@pytest.mark.unit
class TestUserInDBSchema:
    """UserInDB 스키마 테스트 (ORM 변환)"""

    def test_user_indb_from_orm(self, admin_user_instance: AdminUser) -> None:
        """SQLAlchemy ORM 모델에서 Pydantic 스키마로 변환"""
        user_schema = UserInDB.model_validate(admin_user_instance)

        assert user_schema.id == admin_user_instance.id
        assert user_schema.username == admin_user_instance.username
        assert user_schema.email == admin_user_instance.email
        assert user_schema.password_hash == admin_user_instance.password_hash
        assert user_schema.is_active == admin_user_instance.is_active
        assert user_schema.is_superuser == admin_user_instance.is_superuser

    def test_user_indb_contains_password_hash(
        self, admin_user_instance: AdminUser
    ) -> None:
        """UserInDB는 password_hash를 포함 (내부 사용)"""
        user_schema = UserInDB.model_validate(admin_user_instance)
        data = user_schema.model_dump()

        assert "password_hash" in data
        assert data["password_hash"] == admin_user_instance.password_hash


@pytest.mark.unit
class TestUserResponseSchema:
    """User 응답 스키마 테스트 (보안: password_hash 제외)"""

    def test_user_response_from_orm(self, admin_user_instance: AdminUser) -> None:
        """ORM 모델에서 응답 스키마로 변환"""
        user_schema = User.model_validate(admin_user_instance)

        assert user_schema.id == admin_user_instance.id
        assert user_schema.username == admin_user_instance.username
        assert user_schema.email == admin_user_instance.email
        assert user_schema.is_active == admin_user_instance.is_active

    def test_user_response_excludes_password_hash(
        self, admin_user_instance: AdminUser
    ) -> None:
        """User 응답 스키마는 password_hash를 제외 (보안)"""
        user_schema = User.model_validate(admin_user_instance)
        data = user_schema.model_dump()

        assert "password_hash" not in data
        # User 스키마에는 password_hash 필드가 정의되지 않음

    def test_user_response_json_serialization(
        self, admin_user_instance: AdminUser
    ) -> None:
        """JSON 직렬화 테스트"""
        user_schema = User.model_validate(admin_user_instance)
        json_data = user_schema.model_dump_json()

        assert isinstance(json_data, str)
        assert admin_user_instance.username in json_data
        assert admin_user_instance.email in json_data
        # password_hash는 JSON에 포함되지 않음
        assert admin_user_instance.password_hash not in json_data


@pytest.mark.unit
class TestUserLoginSchema:
    """UserLogin 스키마 테스트"""

    def test_user_login_valid_data(self) -> None:
        """유효한 로그인 데이터"""
        data = {
            "username_or_email": "testuser",
            "password": "SecurePass123",
        }
        login = UserLogin(**data)

        assert login.username_or_email == data["username_or_email"]
        assert login.password == data["password"]

    def test_user_login_with_email(self) -> None:
        """이메일로 로그인"""
        data = {
            "username_or_email": "test@example.com",
            "password": "SecurePass123",
        }
        login = UserLogin(**data)

        assert login.username_or_email == data["username_or_email"]

    def test_user_login_required_fields(self) -> None:
        """로그인 필수 필드 검증"""
        with pytest.raises(ValidationError):
            UserLogin(username_or_email="testuser")  # password 누락

        with pytest.raises(ValidationError):
            UserLogin(password="SecurePass123")  # username_or_email 누락
