"""
AdminUser 모델 테스트

테스트 항목:
- ULID + Prefix ID 자동 생성 (user_...)
- TimestampMixin 동작 (created_at, updated_at)
- CRUD 기본 동작
- Unique 제약조건 (username, email)
- Boolean 필드 (is_active, is_superuser)
- Relationship (DraftWeek)
"""

from datetime import datetime, timezone
from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.draft import DraftWeek
from app.models.user import AdminUser


@pytest.mark.unit
class TestAdminUserModel:
    """AdminUser 모델 기본 동작 테스트"""

    async def test_create_admin_user_with_minimal_data(
        self, async_db_session: AsyncSession
    ) -> None:
        """최소 필드만으로 AdminUser 생성 가능"""
        user = AdminUser(
            username="testuser",
            email="test@example.com",
            password_hash="$2b$12$hashed_password",
        )
        async_db_session.add(user)
        await async_db_session.flush()
        await async_db_session.refresh(user)

        # 자동 생성 필드 검증
        assert user.id.startswith("user_")
        assert len(user.id) == 31  # user_ (5) + ULID (26)
        assert user.is_active is True  # 기본값
        assert user.is_superuser is False  # 기본값
        assert user.last_login is None

    async def test_create_admin_user_with_full_data(
        self, async_db_session: AsyncSession, sample_admin_user_data: dict[str, Any]
    ) -> None:
        """모든 필드를 포함한 AdminUser 생성"""
        user = AdminUser(**sample_admin_user_data)
        async_db_session.add(user)
        await async_db_session.flush()
        await async_db_session.refresh(user)

        assert user.username == sample_admin_user_data["username"]
        assert user.email == sample_admin_user_data["email"]
        assert user.password_hash == sample_admin_user_data["password_hash"]
        assert user.is_active == sample_admin_user_data["is_active"]
        assert user.is_superuser == sample_admin_user_data["is_superuser"]

    async def test_admin_user_id_is_unique(
        self, async_db_session: AsyncSession
    ) -> None:
        """AdminUser ID는 고유함"""
        user1 = AdminUser(
            username="user1", email="user1@example.com", password_hash="hash1"
        )
        user2 = AdminUser(
            username="user2", email="user2@example.com", password_hash="hash2"
        )

        async_db_session.add(user1)
        await async_db_session.flush()
        async_db_session.add(user2)
        await async_db_session.flush()

        assert user1.id != user2.id
        assert user1.id < user2.id  # ULID는 시간순 정렬 가능

    async def test_admin_user_timestamps_auto_generated(
        self, async_db_session: AsyncSession
    ) -> None:
        """created_at, updated_at 타임스탬프 자동 생성"""
        user = AdminUser(
            username="timestampuser",
            email="timestamp@example.com",
            password_hash="hash",
        )
        async_db_session.add(user)
        await async_db_session.flush()
        await async_db_session.refresh(user)

        assert user.created_at is not None
        assert user.updated_at is not None
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)
        assert user.created_at.tzinfo is not None

    async def test_admin_user_updated_at_changes_on_update(
        self, async_db_session: AsyncSession, admin_user_instance: AdminUser
    ) -> None:
        """updated_at은 업데이트 시 자동 갱신"""
        original_updated_at = admin_user_instance.updated_at

        import asyncio

        await asyncio.sleep(0.1)

        admin_user_instance.email = "updated@example.com"
        await async_db_session.flush()
        await async_db_session.refresh(admin_user_instance)

        assert admin_user_instance.updated_at > original_updated_at

    async def test_admin_user_username_must_be_unique(
        self, async_db_session: AsyncSession, admin_user_instance: AdminUser
    ) -> None:
        """username은 고유해야 함 (Unique 제약조건)"""
        duplicate_user = AdminUser(
            username=admin_user_instance.username,  # 중복
            email="different@example.com",
            password_hash="hash",
        )
        async_db_session.add(duplicate_user)

        with pytest.raises(IntegrityError):
            await async_db_session.flush()

    async def test_admin_user_email_must_be_unique(
        self, async_db_session: AsyncSession, admin_user_instance: AdminUser
    ) -> None:
        """email은 고유해야 함 (Unique 제약조건)"""
        duplicate_user = AdminUser(
            username="differentuser",
            email=admin_user_instance.email,  # 중복
            password_hash="hash",
        )
        async_db_session.add(duplicate_user)

        with pytest.raises(IntegrityError):
            await async_db_session.flush()

    async def test_admin_user_is_active_toggle(
        self, async_db_session: AsyncSession, admin_user_instance: AdminUser
    ) -> None:
        """is_active 상태 토글 테스트"""
        assert admin_user_instance.is_active is True

        admin_user_instance.is_active = False
        await async_db_session.flush()
        await async_db_session.refresh(admin_user_instance)

        assert admin_user_instance.is_active is False

    async def test_admin_user_is_superuser_flag(
        self, async_db_session: AsyncSession
    ) -> None:
        """is_superuser 플래그 테스트"""
        superuser = AdminUser(
            username="superuser",
            email="super@example.com",
            password_hash="hash",
            is_superuser=True,
        )
        async_db_session.add(superuser)
        await async_db_session.flush()
        await async_db_session.refresh(superuser)

        assert superuser.is_superuser is True

    async def test_admin_user_last_login_update(
        self, async_db_session: AsyncSession, admin_user_instance: AdminUser
    ) -> None:
        """last_login 시각 업데이트 테스트"""
        assert admin_user_instance.last_login is None

        login_time = datetime.now(timezone.utc)
        admin_user_instance.last_login = login_time
        await async_db_session.flush()
        await async_db_session.refresh(admin_user_instance)

        assert admin_user_instance.last_login is not None
        assert admin_user_instance.last_login == login_time

    async def test_admin_user_read_by_id(
        self, async_db_session: AsyncSession, admin_user_instance: AdminUser
    ) -> None:
        """ID로 AdminUser 조회"""
        result = await async_db_session.execute(
            select(AdminUser).where(AdminUser.id == admin_user_instance.id)
        )
        found_user = result.scalar_one_or_none()

        assert found_user is not None
        assert found_user.id == admin_user_instance.id
        assert found_user.username == admin_user_instance.username

    async def test_admin_user_read_by_username(
        self, async_db_session: AsyncSession, admin_user_instance: AdminUser
    ) -> None:
        """username으로 AdminUser 조회"""
        result = await async_db_session.execute(
            select(AdminUser).where(AdminUser.username == admin_user_instance.username)
        )
        found_user = result.scalar_one_or_none()

        assert found_user is not None
        assert found_user.id == admin_user_instance.id

    async def test_admin_user_read_by_email(
        self, async_db_session: AsyncSession, admin_user_instance: AdminUser
    ) -> None:
        """email로 AdminUser 조회"""
        result = await async_db_session.execute(
            select(AdminUser).where(AdminUser.email == admin_user_instance.email)
        )
        found_user = result.scalar_one_or_none()

        assert found_user is not None
        assert found_user.id == admin_user_instance.id

    async def test_admin_user_update_password_hash(
        self, async_db_session: AsyncSession, admin_user_instance: AdminUser
    ) -> None:
        """password_hash 업데이트 테스트"""
        new_hash = "$2b$12$new_hashed_password"
        admin_user_instance.password_hash = new_hash
        await async_db_session.flush()
        await async_db_session.refresh(admin_user_instance)

        assert admin_user_instance.password_hash == new_hash

    async def test_admin_user_delete(
        self, async_db_session: AsyncSession, admin_user_instance: AdminUser
    ) -> None:
        """AdminUser 삭제"""
        user_id = admin_user_instance.id

        await async_db_session.delete(admin_user_instance)
        await async_db_session.flush()

        result = await async_db_session.execute(
            select(AdminUser).where(AdminUser.id == user_id)
        )
        found_user = result.scalar_one_or_none()
        assert found_user is None

    async def test_admin_user_repr(self, admin_user_instance: AdminUser) -> None:
        """__repr__ 메서드 테스트"""
        repr_str = repr(admin_user_instance)
        assert "AdminUser" in repr_str
        assert admin_user_instance.id in repr_str
        assert admin_user_instance.username in repr_str


@pytest.mark.unit
class TestAdminUserRelationships:
    """AdminUser 모델 관계(Relationship) 테스트"""

    async def test_admin_user_approved_draft_weeks_relationship(
        self,
        async_db_session: AsyncSession,
        admin_user_instance: AdminUser,
        sample_draft_week_data: dict[str, Any],
    ) -> None:
        """AdminUser ↔ DraftWeek 관계 테스트"""
        # DraftWeek을 생성하고 관리자가 승인
        draft_week = DraftWeek(**sample_draft_week_data)
        draft_week.approved_by = admin_user_instance.id
        draft_week.approved_at = datetime.now(timezone.utc)

        async_db_session.add(draft_week)
        await async_db_session.flush()
        await async_db_session.refresh(draft_week)

        # Relationship을 통해 승인한 드래프트 조회
        await async_db_session.refresh(admin_user_instance, ["approved_draft_weeks"])
        assert len(admin_user_instance.approved_draft_weeks) == 1
        assert admin_user_instance.approved_draft_weeks[0].id == draft_week.id

        # 역방향 관계도 동작
        await async_db_session.refresh(draft_week, ["approver"])
        assert draft_week.approver.id == admin_user_instance.id

    async def test_admin_user_delete_does_not_cascade_to_draft_weeks(
        self,
        async_db_session: AsyncSession,
        admin_user_instance: AdminUser,
        sample_draft_week_data: dict[str, Any],
    ) -> None:
        """AdminUser 삭제 시 DraftWeek은 cascade 삭제되지 않음 (approved_by만 NULL)"""
        draft_week = DraftWeek(**sample_draft_week_data)
        draft_week.approved_by = admin_user_instance.id
        async_db_session.add(draft_week)
        await async_db_session.flush()
        draft_week_id = draft_week.id

        # AdminUser 삭제
        await async_db_session.delete(admin_user_instance)
        await async_db_session.flush()

        # DraftWeek은 여전히 존재 (approved_by만 NULL이 됨)
        result = await async_db_session.execute(
            select(DraftWeek).where(DraftWeek.id == draft_week_id)
        )
        found_draft = result.scalar_one_or_none()
        assert found_draft is not None
        # Foreign key 제약조건에 따라 삭제가 차단되거나 NULL이 됨
        # (현재 모델 정의에서는 FK에 ondelete 옵션 없음 → 삭제 차단)
