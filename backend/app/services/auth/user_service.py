"""
사용자 서비스

데이터베이스 사용자 관리 (AdminUser CRUD)를 담당합니다.
"""

import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import AdminUser

# 로거 인스턴스
logger = logging.getLogger(__name__)


__all__ = ["UserService"]


class UserService:
    """
    사용자 서비스

    주요 기능:
    - 관리자 계정 생성/조회
    - last_login 업데이트
    """

    async def create_or_get_admin_user(
        self,
        db: AsyncSession,
        email: str,
        google_id: str,
    ) -> AdminUser:
        """
        관리자 계정 생성 또는 조회

        이메일로 기존 관리자를 찾거나, 없으면 새로 생성합니다.
        Google OAuth를 통한 로그인이므로 password_hash는 빈 문자열로 설정합니다.

        Args:
            db: 데이터베이스 세션
            email: Google 이메일
            google_id: Google 사용자 ID

        Returns:
            AdminUser: 관리자 사용자 모델 인스턴스

        Example:
            >>> service = UserService()
            >>> admin = await service.create_or_get_admin_user(
            ...     db, "admin@example.com", "google_user_123"
            ... )
        """
        try:
            # 1. 기존 관리자 계정 조회
            stmt = select(AdminUser).where(AdminUser.email == email)
            result = await db.execute(stmt)
            admin = result.scalar_one_or_none()

            if admin:
                # 2. 기존 사용자 → last_login 업데이트
                admin.last_login = datetime.now(timezone.utc)
                await db.flush()

                logger.info(
                    f"기존 관리자 로그인: {admin.id}",
                    extra={
                        "email": email,
                        "last_login": admin.last_login.isoformat(),
                    },
                )

                return admin

            # 3. 신규 사용자 → 계정 생성
            # OAuth 사용자는 password_hash 불필요 (빈 문자열)
            admin = AdminUser(
                username=email.split("@")[0],  # 이메일 @ 앞부분을 username으로
                email=email,
                password_hash="",  # OAuth 사용자는 비밀번호 불필요
                is_active=True,
                is_superuser=False,  # 기본 권한은 일반 관리자
                last_login=datetime.now(timezone.utc),
            )

            db.add(admin)
            await db.flush()
            await db.refresh(admin)

            logger.info(
                f"신규 관리자 생성: {admin.id}",
                extra={
                    "email": email,
                    "username": admin.username,
                },
            )

            return admin

        except Exception as e:
            logger.error(
                f"관리자 계정 생성/조회 실패: {str(e)}",
                exc_info=True,
            )
            raise
