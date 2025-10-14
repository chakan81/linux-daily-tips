"""
Draft 모델 테스트 (DraftWeek, DraftTip)

테스트 항목:
- ULID + Prefix ID 자동 생성 (draft_...)
- DraftStatus Enum 검증
- DraftWeek ↔ DraftTip 관계
- DraftWeek ↔ AdminUser 관계
- Cascade 삭제 동작
- JSON 필드 (category, terminal_setup)
"""

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.draft import DraftStatus, DraftTip, DraftWeek
from app.models.user import AdminUser


@pytest.mark.unit
class TestDraftWeekModel:
    """DraftWeek 모델 기본 동작 테스트"""

    async def test_create_draft_week_with_minimal_data(
        self, async_db_session: AsyncSession
    ) -> None:
        """최소 필드만으로 DraftWeek 생성 가능"""
        draft_week = DraftWeek(week_start_date=date(2024, 1, 1))
        async_db_session.add(draft_week)
        await async_db_session.flush()
        await async_db_session.refresh(draft_week)

        # 자동 생성 필드 검증
        assert draft_week.id.startswith("draft_")
        assert len(draft_week.id) == 32  # draft_ (6) + ULID (26)
        assert draft_week.status == DraftStatus.DRAFT  # 기본값
        assert draft_week.generated_by == "llm"  # 기본값
        assert draft_week.approved_by is None
        assert draft_week.approval_notes is None
        assert draft_week.approved_at is None

    async def test_create_draft_week_with_full_data(
        self, async_db_session: AsyncSession, sample_draft_week_data: dict[str, Any]
    ) -> None:
        """모든 필드를 포함한 DraftWeek 생성"""
        draft_week = DraftWeek(**sample_draft_week_data)
        async_db_session.add(draft_week)
        await async_db_session.flush()
        await async_db_session.refresh(draft_week)

        assert draft_week.week_start_date == sample_draft_week_data["week_start_date"]
        assert draft_week.status == sample_draft_week_data["status"]
        assert draft_week.generated_by == sample_draft_week_data["generated_by"]

    async def test_draft_week_id_is_unique(
        self, async_db_session: AsyncSession
    ) -> None:
        """DraftWeek ID는 고유함"""
        draft1 = DraftWeek(week_start_date=date(2024, 1, 1))
        draft2 = DraftWeek(week_start_date=date(2024, 1, 8))

        async_db_session.add(draft1)
        await async_db_session.flush()
        async_db_session.add(draft2)
        await async_db_session.flush()

        assert draft1.id != draft2.id
        assert draft1.id < draft2.id  # ULID 시간순 정렬

    async def test_draft_week_timestamps_auto_generated(
        self, async_db_session: AsyncSession
    ) -> None:
        """created_at 타임스탬프 자동 생성 (updated_at 없음 - 드래프트는 수정 안 됨)"""
        draft_week = DraftWeek(week_start_date=date(2024, 1, 1))
        async_db_session.add(draft_week)
        await async_db_session.flush()
        await async_db_session.refresh(draft_week)

        assert draft_week.created_at is not None
        assert isinstance(draft_week.created_at, datetime)
        # DraftWeek은 updated_at이 없음 (수정되지 않는 모델)

    async def test_draft_week_status_enum_validation(
        self, async_db_session: AsyncSession
    ) -> None:
        """DraftStatus Enum 타입 검증"""
        draft_draft = DraftWeek(
            week_start_date=date(2024, 1, 1), status=DraftStatus.DRAFT
        )
        draft_approved = DraftWeek(
            week_start_date=date(2024, 1, 8), status=DraftStatus.APPROVED
        )
        draft_rejected = DraftWeek(
            week_start_date=date(2024, 1, 15), status=DraftStatus.REJECTED
        )

        async_db_session.add_all([draft_draft, draft_approved, draft_rejected])
        await async_db_session.flush()

        assert draft_draft.status == DraftStatus.DRAFT
        assert draft_approved.status == DraftStatus.APPROVED
        assert draft_rejected.status == DraftStatus.REJECTED

    async def test_draft_week_approval_workflow(
        self,
        async_db_session: AsyncSession,
        draft_week_instance: DraftWeek,
        admin_user_instance: AdminUser,
    ) -> None:
        """드래프트 승인 워크플로우 테스트"""
        # 초기 상태: draft
        assert draft_week_instance.status == DraftStatus.DRAFT
        assert draft_week_instance.approved_by is None

        # 승인 처리
        draft_week_instance.status = DraftStatus.APPROVED
        draft_week_instance.approved_by = admin_user_instance.id
        draft_week_instance.approval_notes = "승인되었습니다."
        draft_week_instance.approved_at = datetime.now(timezone.utc)

        await async_db_session.flush()
        await async_db_session.refresh(draft_week_instance)

        assert draft_week_instance.status == DraftStatus.APPROVED
        assert draft_week_instance.approved_by == admin_user_instance.id
        assert draft_week_instance.approval_notes == "승인되었습니다."
        assert draft_week_instance.approved_at is not None

    async def test_draft_week_delete(
        self, async_db_session: AsyncSession, draft_week_instance: DraftWeek
    ) -> None:
        """DraftWeek 삭제"""
        draft_id = draft_week_instance.id

        await async_db_session.delete(draft_week_instance)
        await async_db_session.flush()

        result = await async_db_session.execute(
            select(DraftWeek).where(DraftWeek.id == draft_id)
        )
        found_draft = result.scalar_one_or_none()
        assert found_draft is None

    async def test_draft_week_repr(self, draft_week_instance: DraftWeek) -> None:
        """__repr__ 메서드 테스트"""
        repr_str = repr(draft_week_instance)
        assert "DraftWeek" in repr_str
        assert draft_week_instance.id in repr_str
        assert draft_week_instance.status.value in repr_str


@pytest.mark.unit
class TestDraftTipModel:
    """DraftTip 모델 기본 동작 테스트"""

    async def test_create_draft_tip(
        self,
        async_db_session: AsyncSession,
        draft_week_instance: DraftWeek,
        sample_draft_tip_data: dict[str, Any],
    ) -> None:
        """DraftTip 생성"""
        draft_tip_data = sample_draft_tip_data.copy()
        draft_tip_data["draft_week_id"] = draft_week_instance.id

        draft_tip = DraftTip(**draft_tip_data)
        async_db_session.add(draft_tip)
        await async_db_session.flush()
        await async_db_session.refresh(draft_tip)

        # 자동 생성 필드 검증
        assert draft_tip.id.startswith("draft_")
        assert len(draft_tip.id) == 32
        assert draft_tip.draft_week_id == draft_week_instance.id
        assert draft_tip.day_of_week == sample_draft_tip_data["day_of_week"]
        assert draft_tip.title == sample_draft_tip_data["title"]

    async def test_draft_tip_json_fields(
        self,
        async_db_session: AsyncSession,
        draft_week_instance: DraftWeek,
        sample_draft_tip_data: dict[str, Any],
    ) -> None:
        """DraftTip JSONB 필드 (category, terminal_setup) 테스트"""
        draft_tip_data = sample_draft_tip_data.copy()
        draft_tip_data["draft_week_id"] = draft_week_instance.id

        draft_tip = DraftTip(**draft_tip_data)
        async_db_session.add(draft_tip)
        await async_db_session.flush()
        await async_db_session.refresh(draft_tip)

        # JSONB 필드 정상 저장 및 조회
        assert draft_tip.category == sample_draft_tip_data["category"]
        assert draft_tip.terminal_setup == sample_draft_tip_data["terminal_setup"]
        assert isinstance(draft_tip.category, list)
        assert isinstance(draft_tip.terminal_setup, dict)

    async def test_draft_tip_llm_confidence_score(
        self,
        async_db_session: AsyncSession,
        draft_week_instance: DraftWeek,
        sample_draft_tip_data: dict[str, Any],
    ) -> None:
        """LLM 신뢰도 점수 저장 테스트"""
        draft_tip_data = sample_draft_tip_data.copy()
        draft_tip_data["draft_week_id"] = draft_week_instance.id

        draft_tip = DraftTip(**draft_tip_data)
        async_db_session.add(draft_tip)
        await async_db_session.flush()
        await async_db_session.refresh(draft_tip)

        assert draft_tip.llm_confidence_score == Decimal("0.95")
        assert isinstance(draft_tip.llm_confidence_score, Decimal)

    async def test_draft_tip_created_at_auto_generated(
        self,
        async_db_session: AsyncSession,
        draft_week_instance: DraftWeek,
        sample_draft_tip_data: dict[str, Any],
    ) -> None:
        """created_at 타임스탬프 자동 생성 (updated_at 없음)"""
        draft_tip_data = sample_draft_tip_data.copy()
        draft_tip_data["draft_week_id"] = draft_week_instance.id

        draft_tip = DraftTip(**draft_tip_data)
        async_db_session.add(draft_tip)
        await async_db_session.flush()
        await async_db_session.refresh(draft_tip)

        assert draft_tip.created_at is not None
        assert isinstance(draft_tip.created_at, datetime)
        # DraftTip은 updated_at 없음 (TimestampMixin 사용 안 함)

    async def test_draft_tip_delete(
        self,
        async_db_session: AsyncSession,
        draft_week_instance: DraftWeek,
        sample_draft_tip_data: dict[str, Any],
    ) -> None:
        """DraftTip 삭제"""
        draft_tip_data = sample_draft_tip_data.copy()
        draft_tip_data["draft_week_id"] = draft_week_instance.id

        draft_tip = DraftTip(**draft_tip_data)
        async_db_session.add(draft_tip)
        await async_db_session.flush()
        draft_tip_id = draft_tip.id

        await async_db_session.delete(draft_tip)
        await async_db_session.flush()

        result = await async_db_session.execute(
            select(DraftTip).where(DraftTip.id == draft_tip_id)
        )
        found_tip = result.scalar_one_or_none()
        assert found_tip is None

    async def test_draft_tip_repr(
        self,
        async_db_session: AsyncSession,
        draft_week_instance: DraftWeek,
        sample_draft_tip_data: dict[str, Any],
    ) -> None:
        """__repr__ 메서드 테스트"""
        draft_tip_data = sample_draft_tip_data.copy()
        draft_tip_data["draft_week_id"] = draft_week_instance.id

        draft_tip = DraftTip(**draft_tip_data)
        async_db_session.add(draft_tip)
        await async_db_session.flush()

        repr_str = repr(draft_tip)
        assert "DraftTip" in repr_str
        assert draft_tip.id in repr_str
        assert str(draft_tip.day_of_week) in repr_str


@pytest.mark.unit
class TestDraftRelationships:
    """Draft 모델 관계(Relationship) 테스트"""

    async def test_draft_week_draft_tips_relationship(
        self,
        async_db_session: AsyncSession,
        draft_week_instance: DraftWeek,
        sample_draft_tip_data: dict[str, Any],
    ) -> None:
        """DraftWeek ↔ DraftTip 관계 테스트"""
        # 여러 개의 DraftTip 생성 (7개)
        for day in range(1, 8):
            draft_tip_data = sample_draft_tip_data.copy()
            draft_tip_data["draft_week_id"] = draft_week_instance.id
            draft_tip_data["day_of_week"] = day
            draft_tip_data["title"] = f"Day {day} Tip"

            draft_tip = DraftTip(**draft_tip_data)
            async_db_session.add(draft_tip)

        await async_db_session.flush()

        # Relationship을 통해 DraftTip 조회
        await async_db_session.refresh(draft_week_instance, ["draft_tips"])
        assert len(draft_week_instance.draft_tips) == 7

        # 역방향 관계도 동작
        first_tip = draft_week_instance.draft_tips[0]
        await async_db_session.refresh(first_tip, ["draft_week"])
        assert first_tip.draft_week.id == draft_week_instance.id

    async def test_draft_week_cascade_delete_draft_tips(
        self,
        async_db_session: AsyncSession,
        draft_week_instance: DraftWeek,
        sample_draft_tip_data: dict[str, Any],
    ) -> None:
        """DraftWeek 삭제 시 연결된 DraftTip도 cascade 삭제"""
        # DraftTip 생성
        draft_tip_data = sample_draft_tip_data.copy()
        draft_tip_data["draft_week_id"] = draft_week_instance.id
        draft_tip = DraftTip(**draft_tip_data)
        async_db_session.add(draft_tip)
        await async_db_session.flush()
        draft_tip_id = draft_tip.id

        # DraftWeek 삭제
        await async_db_session.delete(draft_week_instance)
        await async_db_session.flush()

        # 연결된 DraftTip도 삭제됨
        result = await async_db_session.execute(
            select(DraftTip).where(DraftTip.id == draft_tip_id)
        )
        found_tip = result.scalar_one_or_none()
        assert found_tip is None

    async def test_draft_week_approver_relationship(
        self,
        async_db_session: AsyncSession,
        draft_week_instance: DraftWeek,
        admin_user_instance: AdminUser,
    ) -> None:
        """DraftWeek ↔ AdminUser (approver) 관계 테스트"""
        draft_week_instance.approved_by = admin_user_instance.id
        draft_week_instance.approved_at = datetime.now(timezone.utc)
        await async_db_session.flush()

        # Relationship을 통해 approver 조회
        await async_db_session.refresh(draft_week_instance, ["approver"])
        assert draft_week_instance.approver is not None
        assert draft_week_instance.approver.id == admin_user_instance.id
        assert draft_week_instance.approver.username == admin_user_instance.username
