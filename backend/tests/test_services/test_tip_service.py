"""
TipService 비즈니스 로직 테스트 (TDD - RED 단계)

테스트 항목:
- get_daily_tip: 오늘 날짜 팁 조회
- get_tip_by_id: ID로 팁 조회
- get_tips: 팁 목록 조회 (필터링 + 페이지네이션)
- create_tip: 팁 생성
- update_tip: 팁 수정
- delete_tip: 팁 삭제 (soft delete)
- increment_view_count: 조회수 증가

주의: 이 테스트는 TipService가 구현되지 않았으므로 실패해야 합니다!
"""

from datetime import date, timedelta
from typing import Any

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tip import DifficultyLevel, Tip
from app.schemas.tip import TipCreate, TipUpdate
from app.services.tip import TipService


@pytest.mark.asyncio
@pytest.mark.unit
class TestTipServiceGetMethods:
    """TipService 조회(GET) 메서드 테스트"""

    async def test_get_daily_tip_returns_tip_for_today(
        self, async_db_session: AsyncSession
    ) -> None:
        """오늘 날짜의 팁이 존재하면 반환"""
        # Arrange: 오늘 날짜로 팁 생성
        today = date.today()
        tip = Tip(
            title="오늘의 팁",
            content="오늘의 팁 내용입니다. 최소 20자 이상.",
            publish_date=today,
            is_active=True,
        )
        async_db_session.add(tip)
        await async_db_session.flush()

        # Act: 오늘 날짜 팁 조회 (캐시 없이)
        service = TipService()  # 캐시 없이 인스턴스화
        result = await service.get_daily_tip(async_db_session, today)

        # Assert: 팁이 반환되어야 함
        assert result is not None, "오늘 날짜 팁이 반환되어야 합니다"
        assert result.id == tip.id
        assert result.title == "오늘의 팁"
        assert result.publish_date == today

    async def test_get_daily_tip_returns_none_when_no_tip(
        self, async_db_session: AsyncSession
    ) -> None:
        """해당 날짜에 팁이 없으면 None 반환"""
        # Arrange: 과거 날짜로 팁 생성
        past_date = date.today() - timedelta(days=10)
        tip = Tip(
            title="과거 팁",
            content="과거 팁 내용입니다. 최소 20자 이상.",
            publish_date=past_date,
        )
        async_db_session.add(tip)
        await async_db_session.flush()

        # Act: 오늘 날짜 팁 조회 (존재하지 않음)
        service = TipService()
        result = await service.get_daily_tip(async_db_session, date.today())

        # Assert: None 반환
        assert result is None, "팁이 없는 날짜는 None을 반환해야 합니다"

    async def test_get_daily_tip_returns_active_tip_only(
        self, async_db_session: AsyncSession
    ) -> None:
        """is_active=False인 팁은 조회되지 않음"""
        # Arrange: 비활성화된 팁 생성
        today = date.today()
        inactive_tip = Tip(
            title="비활성화 팁",
            content="비활성화된 팁입니다. 최소 20자 이상.",
            publish_date=today,
            is_active=False,  # 비활성화
        )
        async_db_session.add(inactive_tip)
        await async_db_session.flush()

        # Act: 오늘 날짜 팁 조회
        service = TipService()
        result = await service.get_daily_tip(async_db_session, today)

        # Assert: 비활성화 팁은 반환되지 않음
        assert result is None, "비활성화된 팁은 조회되지 않아야 합니다"

    async def test_get_tip_by_id_returns_tip(
        self, async_db_session: AsyncSession
    ) -> None:
        """ID로 팁 조회 성공"""
        # Arrange: 팁 생성
        tip = Tip(
            title="ID 조회 테스트",
            content="ID 조회 테스트입니다. 최소 20자 이상.",
        )
        async_db_session.add(tip)
        await async_db_session.flush()
        await async_db_session.refresh(tip)

        # Act: ID로 팁 조회
        service = TipService()
        result = await service.get_tip_by_id(async_db_session, tip.id)

        # Assert: 정확한 팁 반환
        assert result is not None
        assert result.id == tip.id
        assert result.title == "ID 조회 테스트"

    async def test_get_tip_by_id_raises_not_found(
        self, async_db_session: AsyncSession
    ) -> None:
        """존재하지 않는 ID 조회 시 에러 발생"""
        # Arrange: 존재하지 않는 ID
        non_existent_id = "tip_99999999999999999999999999"

        # Act & Assert: AppException(404) 발생 예상
        from app.core.exceptions import AppException

        service = TipService()
        with pytest.raises(AppException) as exc_info:
            await service.get_tip_by_id(async_db_session, non_existent_id)

        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail).lower()

    async def test_get_tips_returns_all_tips(
        self, async_db_session: AsyncSession
    ) -> None:
        """전체 팁 목록 반환 (페이지네이션 없음)"""
        # Arrange: 여러 팁 생성
        tips_data = [
            ("팁 1", "팁 1 내용입니다. 최소 20자 이상."),
            ("팁 2", "팁 2 내용입니다. 최소 20자 이상."),
            ("팁 3", "팁 3 내용입니다. 최소 20자 이상."),
        ]
        for title, content in tips_data:
            tip = Tip(title=title, content=content)
            async_db_session.add(tip)
        await async_db_session.flush()

        # Act: 전체 팁 조회 (skip=0, limit=10)
        service = TipService()
        result_tips, total_count = await service.get_tips(
            async_db_session, skip=0, limit=10
        )

        # Assert: 3개의 팁 반환
        assert len(result_tips) == 3, "3개의 팁이 반환되어야 합니다"
        assert total_count == 3, "총 개수는 3이어야 합니다"

    async def test_get_tips_with_difficulty_filter(
        self, async_db_session: AsyncSession
    ) -> None:
        """난이도 필터링 동작 확인"""
        # Arrange: 난이도별 팁 생성
        beginner_tip = Tip(
            title="초급 팁",
            content="초급 팁입니다. 최소 20자 이상.",
            difficulty=DifficultyLevel.BEGINNER,
        )
        advanced_tip = Tip(
            title="고급 팁",
            content="고급 팁입니다. 최소 20자 이상.",
            difficulty=DifficultyLevel.ADVANCED,
        )
        async_db_session.add_all([beginner_tip, advanced_tip])
        await async_db_session.flush()

        # Act: 초급 난이도만 필터링
        service = TipService()
        result_tips, total_count = await service.get_tips(
            async_db_session, skip=0, limit=10, difficulty="beginner"
        )

        # Assert: 초급 팁만 반환
        assert len(result_tips) == 1, "초급 팁 1개만 반환되어야 합니다"
        assert result_tips[0].difficulty == DifficultyLevel.BEGINNER

    async def test_get_tips_with_category_filter(
        self, async_db_session: AsyncSession
    ) -> None:
        """카테고리 필터링 동작 확인"""
        # Arrange: 카테고리별 팁 생성
        file_tip = Tip(
            title="파일 시스템 팁",
            content="파일 시스템 팁입니다. 최소 20자 이상.",
            category=["file-system"],
        )
        network_tip = Tip(
            title="네트워크 팁",
            content="네트워크 팁입니다. 최소 20자 이상.",
            category=["network"],
        )
        async_db_session.add_all([file_tip, network_tip])
        await async_db_session.flush()

        # Act: file-system 카테고리만 필터링
        service = TipService()
        result_tips, total_count = await service.get_tips(
            async_db_session, skip=0, limit=10, category="file-system"
        )

        # Assert: file-system 팁만 반환
        assert len(result_tips) == 1, "file-system 팁 1개만 반환되어야 합니다"
        assert "file-system" in result_tips[0].category

    async def test_get_tips_with_pagination(
        self, async_db_session: AsyncSession
    ) -> None:
        """페이지네이션 동작 확인"""
        # Arrange: 5개 팁 생성
        for i in range(5):
            tip = Tip(
                title=f"팁 {i+1}",
                content=f"팁 {i+1} 내용입니다. 최소 20자 이상.",
            )
            async_db_session.add(tip)
        await async_db_session.flush()

        # Act: skip=2, limit=2로 조회 (3번째, 4번째 팁)
        service = TipService()
        result_tips, total_count = await service.get_tips(
            async_db_session, skip=2, limit=2
        )

        # Assert: 2개 팁만 반환, 총 개수는 5
        assert len(result_tips) == 2, "2개의 팁만 반환되어야 합니다"
        assert total_count == 5, "전체 팁 개수는 5여야 합니다"


@pytest.mark.asyncio
@pytest.mark.unit
class TestTipServiceCreateMethod:
    """TipService 생성(CREATE) 메서드 테스트"""

    async def test_create_tip_success(self, async_db_session: AsyncSession) -> None:
        """팁 생성 성공"""
        # Arrange: 팁 생성 데이터
        tip_data = TipCreate(
            title="새로운 팁",
            content="새로운 팁 내용입니다. 최소 20자 이상.",
            difficulty=DifficultyLevel.BEGINNER,
            category=["file-system"],
            publish_date=date.today(),
        )

        # Act: 팁 생성
        service = TipService()
        created_tip = await service.create_tip(async_db_session, tip_data)

        # Assert: 팁이 정상 생성됨
        assert created_tip is not None
        assert created_tip.id.startswith("tip_")
        assert created_tip.title == "새로운 팁"
        assert created_tip.difficulty == DifficultyLevel.BEGINNER
        assert created_tip.category == ["file-system"]
        assert created_tip.is_active is True
        assert created_tip.view_count == 0

    async def test_create_tip_with_duplicate_date(
        self, async_db_session: AsyncSession
    ) -> None:
        """같은 날짜에 이미 팁이 존재하면 에러 발생 (비즈니스 규칙)"""
        # Arrange: 오늘 날짜로 팁 이미 존재
        today = date.today()
        existing_tip = Tip(
            title="기존 팁",
            content="기존 팁입니다. 최소 20자 이상.",
            publish_date=today,
        )
        async_db_session.add(existing_tip)
        await async_db_session.flush()

        # Arrange: 같은 날짜로 새 팁 생성 시도
        tip_data = TipCreate(
            title="중복 날짜 팁",
            content="중복 날짜 팁입니다. 최소 20자 이상.",
            publish_date=today,
        )

        # Act & Assert: AppException(409 Conflict) 발생 예상
        from app.core.exceptions import AppException

        with pytest.raises(AppException) as exc_info:
            service = TipService()
            await service.create_tip(async_db_session, tip_data)

        assert exc_info.value.status_code == 409
        assert "이미 존재" in str(exc_info.value.detail)

    async def test_create_tip_with_default_publish_date(
        self, async_db_session: AsyncSession
    ) -> None:
        """publish_date가 None이면 오늘 날짜로 자동 설정"""
        # Arrange: publish_date 미지정
        tip_data = TipCreate(
            title="자동 날짜 팁",
            content="자동 날짜 팁입니다. 최소 20자 이상.",
            publish_date=None,  # 명시적으로 None
        )

        # Act: 팁 생성
        service = TipService()
        created_tip = await service.create_tip(async_db_session, tip_data)

        # Assert: 오늘 날짜로 설정됨
        assert created_tip.publish_date == date.today()


@pytest.mark.asyncio
@pytest.mark.unit
class TestTipServiceUpdateMethod:
    """TipService 수정(UPDATE) 메서드 테스트"""

    async def test_update_tip_success(self, async_db_session: AsyncSession) -> None:
        """팁 수정 성공"""
        # Arrange: 기존 팁 생성
        tip = Tip(
            title="원본 제목",
            content="원본 내용입니다. 최소 20자 이상.",
            difficulty=DifficultyLevel.BEGINNER,
        )
        async_db_session.add(tip)
        await async_db_session.flush()
        await async_db_session.refresh(tip)
        tip_id = tip.id

        # Arrange: 수정 데이터
        update_data = TipUpdate(
            title="수정된 제목",
            difficulty=DifficultyLevel.ADVANCED,
        )

        # Act: 팁 수정
        service = TipService()
        updated_tip = await service.update_tip(
            async_db_session, tip_id, update_data
        )

        # Assert: 수정된 필드만 변경됨
        assert updated_tip.title == "수정된 제목"
        assert updated_tip.difficulty == DifficultyLevel.ADVANCED
        assert updated_tip.content == "원본 내용입니다. 최소 20자 이상."  # 변경 안됨

    async def test_update_tip_not_found(self, async_db_session: AsyncSession) -> None:
        """존재하지 않는 팁 수정 시 에러 발생"""
        # Arrange: 존재하지 않는 ID
        non_existent_id = "tip_99999999999999999999999999"
        update_data = TipUpdate(title="수정할 제목")

        # Act & Assert: AppException(404) 발생
        from app.core.exceptions import AppException

        with pytest.raises(AppException) as exc_info:
            service = TipService()
            await service.update_tip(
                async_db_session, non_existent_id, update_data
            )

        assert exc_info.value.status_code == 404

    async def test_update_tip_partial_update(
        self, async_db_session: AsyncSession
    ) -> None:
        """부분 업데이트 동작 확인 (None이 아닌 필드만 업데이트)"""
        # Arrange: 기존 팁
        tip = Tip(
            title="원본 제목",
            content="원본 내용입니다. 최소 20자 이상.",
            difficulty=DifficultyLevel.BEGINNER,
            category=["file-system"],
        )
        async_db_session.add(tip)
        await async_db_session.flush()
        await async_db_session.refresh(tip)

        # Arrange: category만 수정
        update_data = TipUpdate(category=["network", "security"])

        # Act: 팁 수정
        service = TipService()
        updated_tip = await service.update_tip(
            async_db_session, tip.id, update_data
        )

        # Assert: category만 변경, 나머지 유지
        assert updated_tip.category == ["network", "security"]
        assert updated_tip.title == "원본 제목"  # 변경 안됨
        assert updated_tip.difficulty == DifficultyLevel.BEGINNER  # 변경 안됨


@pytest.mark.asyncio
@pytest.mark.unit
class TestTipServiceDeleteMethod:
    """TipService 삭제(DELETE) 메서드 테스트"""

    async def test_delete_tip_success(self, async_db_session: AsyncSession) -> None:
        """팁 삭제 성공 (soft delete: is_active=False)"""
        # Arrange: 팁 생성
        tip = Tip(
            title="삭제할 팁",
            content="삭제할 팁입니다. 최소 20자 이상.",
            is_active=True,
        )
        async_db_session.add(tip)
        await async_db_session.flush()
        await async_db_session.refresh(tip)
        tip_id = tip.id

        # Act: 팁 삭제 (soft delete)
        service = TipService()
        result = await service.delete_tip(async_db_session, tip_id)

        # Assert: 삭제 성공 (is_active=False로 변경)
        assert result is True
        # 데이터베이스에서 다시 조회하여 확인
        service = TipService()
        deleted_tip = await service.get_tip_by_id(async_db_session, tip_id)
        assert deleted_tip.is_active is False, "Soft delete는 is_active를 False로 설정합니다"

    async def test_delete_tip_not_found(self, async_db_session: AsyncSession) -> None:
        """존재하지 않는 팁 삭제 시 에러 발생"""
        # Arrange: 존재하지 않는 ID
        non_existent_id = "tip_99999999999999999999999999"

        # Act & Assert: AppException(404) 발생
        from app.core.exceptions import AppException

        with pytest.raises(AppException) as exc_info:
            service = TipService()
            await service.delete_tip(async_db_session, non_existent_id)

        assert exc_info.value.status_code == 404

    async def test_delete_tip_already_deleted(
        self, async_db_session: AsyncSession
    ) -> None:
        """이미 삭제된 팁 재삭제 시도 (멱등성 확인)"""
        # Arrange: 이미 비활성화된 팁
        tip = Tip(
            title="이미 삭제된 팁",
            content="이미 삭제된 팁입니다. 최소 20자 이상.",
            is_active=False,  # 이미 비활성화
        )
        async_db_session.add(tip)
        await async_db_session.flush()
        await async_db_session.refresh(tip)

        # Act: 재삭제 시도
        service = TipService()
        result = await service.delete_tip(async_db_session, tip.id)

        # Assert: 성공 반환 (멱등성)
        assert result is True


@pytest.mark.asyncio
@pytest.mark.unit
class TestTipServiceIncrementViewCount:
    """TipService 조회수 증가 테스트"""

    async def test_increment_view_count_success(
        self, async_db_session: AsyncSession
    ) -> None:
        """조회수 증가 성공"""
        # Arrange: 팁 생성
        tip = Tip(
            title="조회수 테스트",
            content="조회수 테스트입니다. 최소 20자 이상.",
            view_count=0,
        )
        async_db_session.add(tip)
        await async_db_session.flush()
        await async_db_session.refresh(tip)
        initial_count = tip.view_count

        # Act: 조회수 증가
        service = TipService()
        updated_tip = await service.increment_view_count(
            async_db_session, tip.id
        )

        # Assert: 조회수 1 증가
        assert updated_tip.view_count == initial_count + 1

    async def test_increment_view_count_multiple_times(
        self, async_db_session: AsyncSession
    ) -> None:
        """여러 번 조회수 증가 동작 확인"""
        # Arrange: 팁 생성
        tip = Tip(
            title="다중 조회 테스트",
            content="다중 조회 테스트입니다. 최소 20자 이상.",
            view_count=0,
        )
        async_db_session.add(tip)
        await async_db_session.flush()
        await async_db_session.refresh(tip)

        # Act: 3번 조회
        for _ in range(3):
            service = TipService()
            updated_tip = await service.increment_view_count(
                async_db_session, tip.id
            )

        # Assert: 조회수 3 증가
        assert updated_tip.view_count == 3

    async def test_increment_view_count_not_found(
        self, async_db_session: AsyncSession
    ) -> None:
        """존재하지 않는 팁의 조회수 증가 시 에러 발생"""
        # Arrange: 존재하지 않는 ID
        non_existent_id = "tip_99999999999999999999999999"

        # Act & Assert: AppException(404) 발생
        from app.core.exceptions import AppException

        with pytest.raises(AppException) as exc_info:
            service = TipService()
            await service.increment_view_count(async_db_session, non_existent_id)

        assert exc_info.value.status_code == 404
