"""
TerminalService 비즈니스 로직 테스트 (TDD - RED 단계)

터미널 세션 관리 및 비즈니스 로직을 테스트합니다:
- 세션 생성 (DB 저장 + Docker 컨테이너 생성)
- 세션 조회 (ID로 조회, 만료 여부 확인)
- 세션 종료 (DB 업데이트 + 컨테이너 삭제)
- 자동 만료 세션 정리 (백그라운드 작업)
- 명령어 실행 (보안 검증 + Docker 실행)
- 에러 처리 (컨테이너 생성 실패, 네트워크 오류 등)

주의: TerminalService가 구현되지 않았으므로 이 테스트들은 실패해야 합니다!
"""

from datetime import datetime, timedelta, timezone
from ipaddress import IPv4Address
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.models.terminal import TerminalSession, TerminalStatus
from app.models.tip import Tip
from app.schemas.terminal import TerminalSessionCreate


@pytest.fixture
def mock_docker_service() -> MagicMock:
    """
    Mock DockerService

    실제 Docker 컨테이너를 생성하지 않고 테스트할 수 있도록
    DockerService를 모킹합니다.
    """
    service = MagicMock()
    service.create_container = AsyncMock(return_value="abc123def456")
    service.execute_command = AsyncMock(
        return_value={"exit_code": 0, "output": "test output", "error": ""}
    )
    service.remove_container = AsyncMock()
    service.is_command_safe = MagicMock(return_value=True)
    return service


@pytest.mark.asyncio
@pytest.mark.unit
class TestTerminalServiceSessionCreation:
    """터미널 세션 생성 테스트"""

    async def test_create_session_with_valid_tip_id(
        self,
        async_db_session: AsyncSession,
        tip_instance: Tip,
        mock_docker_service: MagicMock,
    ) -> None:
        """
        유효한 tip_id로 세션 생성

        Given: 활성화된 Tip이 존재
        When: create_session(tip_id, ip_address, user_agent) 호출
        Then: DB에 세션 저장 + Docker 컨테이너 생성
        """
        # Arrange
        from app.services.terminal import TerminalService

        service = TerminalService(docker_service=mock_docker_service)
        session_data = TerminalSessionCreate(
            tip_id=tip_instance.id,
            ip_address=IPv4Address("192.168.1.1"),
            user_agent="Mozilla/5.0",
            session_data={"terminal_size": {"rows": 24, "cols": 80}},
        )

        # Act
        session = await service.create_session(async_db_session, session_data)

        # Assert
        assert session.id.startswith("session_"), "세션 ID는 'session_' 프리픽스를 가져야 함"
        assert session.tip_id == tip_instance.id
        assert session.container_id == "abc123def456"
        assert session.status == TerminalStatus.ACTIVE
        assert session.ip_address == IPv4Address("192.168.1.1")
        assert session.user_agent == "Mozilla/5.0"
        assert session.session_data == {"terminal_size": {"rows": 24, "cols": 80}}

        # Docker 컨테이너 생성 호출 확인
        mock_docker_service.create_container.assert_called_once()

        # DB에 저장되었는지 확인
        result = await async_db_session.execute(
            select(TerminalSession).where(TerminalSession.id == session.id)
        )
        saved_session = result.scalar_one_or_none()
        assert saved_session is not None, "세션이 DB에 저장되어야 함"

    async def test_create_session_without_tip_id(
        self,
        async_db_session: AsyncSession,
        mock_docker_service: MagicMock,
    ) -> None:
        """
        tip_id 없이 익명 세션 생성

        Given: tip_id가 없음
        When: create_session(ip_address, user_agent) 호출
        Then: 익명 세션 생성 (tip_id=None)
        """
        # Arrange
        from app.services.terminal import TerminalService

        service = TerminalService(docker_service=mock_docker_service)
        session_data = TerminalSessionCreate(
            tip_id=None,
            ip_address=IPv4Address("192.168.1.100"),
            user_agent="Chrome/120.0",
        )

        # Act
        session = await service.create_session(async_db_session, session_data)

        # Assert
        assert session.tip_id is None, "익명 세션은 tip_id가 None이어야 함"
        assert session.container_id == "abc123def456"
        assert session.status == TerminalStatus.ACTIVE

    async def test_create_session_fails_when_tip_not_found(
        self,
        async_db_session: AsyncSession,
        mock_docker_service: MagicMock,
    ) -> None:
        """
        존재하지 않는 tip_id로 세션 생성 시도

        Given: tip_id가 존재하지 않음
        When: create_session(invalid_tip_id) 호출
        Then: AppException 발생
        """
        # Arrange
        from app.services.terminal import TerminalService

        service = TerminalService(docker_service=mock_docker_service)
        session_data = TerminalSessionCreate(
            tip_id="tip_invalid_id_not_exists",
            ip_address=IPv4Address("192.168.1.1"),
            user_agent="Mozilla/5.0",
        )

        # Act & Assert
        with pytest.raises(AppException) as exc_info:
            await service.create_session(async_db_session, session_data)

        assert "팁을 찾을 수 없습니다" in str(exc_info.value.message)
        assert exc_info.value.status_code == 404

    async def test_create_session_fails_when_tip_inactive(
        self,
        async_db_session: AsyncSession,
        mock_docker_service: MagicMock,
    ) -> None:
        """
        비활성화된 팁으로 세션 생성 시도

        Given: is_active=False인 Tip이 존재
        When: create_session(tip_id) 호출
        Then: AppException 발생
        """
        # Arrange
        from app.services.terminal import TerminalService

        # 비활성화된 팁 생성
        inactive_tip = Tip(
            title="비활성화 팁",
            content="비활성화된 팁입니다. 최소 20자 이상.",
            is_active=False,
        )
        async_db_session.add(inactive_tip)
        await async_db_session.flush()

        service = TerminalService(docker_service=mock_docker_service)
        session_data = TerminalSessionCreate(
            tip_id=inactive_tip.id,
            ip_address=IPv4Address("192.168.1.1"),
            user_agent="Mozilla/5.0",
        )

        # Act & Assert
        with pytest.raises(AppException) as exc_info:
            await service.create_session(async_db_session, session_data)

        assert "활성화되지 않은 팁" in str(exc_info.value.message)
        assert exc_info.value.status_code == 400

    async def test_create_session_fails_when_docker_error(
        self,
        async_db_session: AsyncSession,
        tip_instance: Tip,
        mock_docker_service: MagicMock,
    ) -> None:
        """
        Docker 컨테이너 생성 실패 시 에러 처리

        Given: Docker 서비스가 에러 반환
        When: create_session() 호출
        Then: AppException 발생, DB 롤백
        """
        # Arrange
        from app.services.terminal import TerminalService

        mock_docker_service.create_container.side_effect = AppException(
            message="Docker 데몬 오류", status_code=500
        )

        service = TerminalService(docker_service=mock_docker_service)
        session_data = TerminalSessionCreate(
            tip_id=tip_instance.id,
            ip_address=IPv4Address("192.168.1.1"),
            user_agent="Mozilla/5.0",
        )

        # Act & Assert
        with pytest.raises(AppException) as exc_info:
            await service.create_session(async_db_session, session_data)

        assert "Docker 데몬 오류" in str(exc_info.value.message)

        # DB에 저장되지 않았는지 확인 (롤백됨)
        result = await async_db_session.execute(
            select(TerminalSession).where(TerminalSession.tip_id == tip_instance.id)
        )
        sessions = result.scalars().all()
        assert len(sessions) == 0, "에러 발생 시 세션이 DB에 저장되지 않아야 함"

    async def test_create_session_sets_expires_at_30_minutes(
        self,
        async_db_session: AsyncSession,
        tip_instance: Tip,
        mock_docker_service: MagicMock,
    ) -> None:
        """
        세션 만료 시간이 30분으로 설정되는지 확인

        Given: 정상적인 세션 생성 요청
        When: create_session() 호출
        Then: expires_at = 생성 시각 + 30분
        """
        # Arrange
        from app.services.terminal import TerminalService

        service = TerminalService(docker_service=mock_docker_service)
        session_data = TerminalSessionCreate(
            tip_id=tip_instance.id,
            ip_address=IPv4Address("192.168.1.1"),
            user_agent="Mozilla/5.0",
        )

        # Act
        session = await service.create_session(async_db_session, session_data)

        # Assert
        expected_expiry = session.created_at + timedelta(minutes=30)
        time_diff = abs((session.expires_at - expected_expiry).total_seconds())
        assert time_diff < 1, "만료 시간은 생성 시각 + 30분이어야 함 (1초 오차 허용)"


@pytest.mark.asyncio
@pytest.mark.unit
class TestTerminalServiceSessionRetrieval:
    """터미널 세션 조회 테스트"""

    async def test_get_session_by_id_returns_session(
        self,
        async_db_session: AsyncSession,
        terminal_session_instance: TerminalSession,
    ) -> None:
        """
        ID로 세션 조회 성공

        Given: 활성 세션이 존재
        When: get_session_by_id(session_id) 호출
        Then: 세션 반환
        """
        # Arrange
        from app.services.terminal import TerminalService

        service = TerminalService()

        # Act
        session = await service.get_session_by_id(
            async_db_session, terminal_session_instance.id
        )

        # Assert
        assert session is not None
        assert session.id == terminal_session_instance.id
        assert session.status == TerminalStatus.ACTIVE

    async def test_get_session_by_id_returns_none_when_not_found(
        self,
        async_db_session: AsyncSession,
    ) -> None:
        """
        존재하지 않는 세션 ID로 조회

        Given: 세션이 존재하지 않음
        When: get_session_by_id(invalid_id) 호출
        Then: None 반환
        """
        # Arrange
        from app.services.terminal import TerminalService

        service = TerminalService()

        # Act
        session = await service.get_session_by_id(
            async_db_session, "session_invalid_not_exists"
        )

        # Assert
        assert session is None

    async def test_get_active_sessions_returns_only_active(
        self,
        async_db_session: AsyncSession,
        tip_instance: Tip,
    ) -> None:
        """
        활성 세션만 조회

        Given: 활성/종료/만료된 세션이 혼재
        When: get_active_sessions() 호출
        Then: 활성 세션만 반환
        """
        # Arrange
        from app.services.terminal import TerminalService

        # 활성 세션
        active_session = TerminalSession(
            tip_id=tip_instance.id,
            container_id="active123",
            status=TerminalStatus.ACTIVE,
            ip_address=IPv4Address("192.168.1.1"),
        )
        async_db_session.add(active_session)

        # 종료된 세션
        terminated_session = TerminalSession(
            tip_id=tip_instance.id,
            container_id="terminated456",
            status=TerminalStatus.TERMINATED,
            ip_address=IPv4Address("192.168.1.2"),
        )
        async_db_session.add(terminated_session)

        # 만료된 세션
        expired_session = TerminalSession(
            tip_id=tip_instance.id,
            container_id="expired789",
            status=TerminalStatus.EXPIRED,
            ip_address=IPv4Address("192.168.1.3"),
        )
        async_db_session.add(expired_session)

        await async_db_session.flush()

        service = TerminalService()

        # Act
        sessions = await service.get_active_sessions(async_db_session)

        # Assert
        assert len(sessions) == 1, "활성 세션만 반환되어야 함"
        assert sessions[0].id == active_session.id
        assert sessions[0].status == TerminalStatus.ACTIVE

    async def test_is_session_expired_returns_true_when_expired(
        self,
        async_db_session: AsyncSession,
        tip_instance: Tip,
    ) -> None:
        """
        만료된 세션 확인

        Given: expires_at이 현재 시각보다 과거인 세션
        When: is_session_expired(session) 호출
        Then: True 반환
        """
        # Arrange
        from app.services.terminal import TerminalService

        # 이미 만료된 세션 생성 (1시간 전 만료)
        expired_session = TerminalSession(
            tip_id=tip_instance.id,
            container_id="expired123",
            status=TerminalStatus.ACTIVE,
            ip_address=IPv4Address("192.168.1.1"),
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        async_db_session.add(expired_session)
        await async_db_session.flush()

        service = TerminalService()

        # Act
        is_expired = service.is_session_expired(expired_session)

        # Assert
        assert is_expired is True, "만료된 세션은 True를 반환해야 함"

    async def test_is_session_expired_returns_false_when_valid(
        self,
        async_db_session: AsyncSession,
        terminal_session_instance: TerminalSession,
    ) -> None:
        """
        유효한 세션 확인

        Given: expires_at이 현재 시각보다 미래인 세션
        When: is_session_expired(session) 호출
        Then: False 반환
        """
        # Arrange
        from app.services.terminal import TerminalService

        service = TerminalService()

        # Act
        is_expired = service.is_session_expired(terminal_session_instance)

        # Assert
        assert is_expired is False, "유효한 세션은 False를 반환해야 함"

    async def test_get_session_remaining_time(
        self,
        async_db_session: AsyncSession,
        terminal_session_instance: TerminalSession,
    ) -> None:
        """
        세션 남은 시간 계산

        Given: 활성 세션이 존재
        When: get_session_remaining_time(session) 호출
        Then: 남은 시간(초) 반환
        """
        # Arrange
        from app.services.terminal import TerminalService

        service = TerminalService()

        # Act
        remaining_seconds = service.get_session_remaining_time(
            terminal_session_instance
        )

        # Assert
        assert remaining_seconds > 0, "유효한 세션은 양수의 남은 시간을 가져야 함"
        assert (
            remaining_seconds <= 30 * 60
        ), "남은 시간은 최대 30분(1800초)을 초과할 수 없음"


@pytest.mark.asyncio
@pytest.mark.unit
class TestTerminalServiceSessionTermination:
    """터미널 세션 종료 테스트"""

    async def test_terminate_session_updates_status_and_time(
        self,
        async_db_session: AsyncSession,
        terminal_session_instance: TerminalSession,
        mock_docker_service: MagicMock,
    ) -> None:
        """
        세션 수동 종료

        Given: 활성 세션이 존재
        When: terminate_session(session_id) 호출
        Then: status=TERMINATED, terminated_at 설정, 컨테이너 삭제
        """
        # Arrange
        from app.services.terminal import TerminalService

        service = TerminalService(docker_service=mock_docker_service)

        # Act
        session = await service.terminate_session(
            async_db_session, terminal_session_instance.id
        )

        # Assert
        assert session.status == TerminalStatus.TERMINATED
        assert session.terminated_at is not None
        assert (
            datetime.now(timezone.utc) - session.terminated_at
        ).total_seconds() < 1

        # Docker 컨테이너 삭제 호출 확인
        mock_docker_service.remove_container.assert_called_once_with(
            terminal_session_instance.container_id, force=True
        )

    async def test_terminate_session_fails_when_not_found(
        self,
        async_db_session: AsyncSession,
        mock_docker_service: MagicMock,
    ) -> None:
        """
        존재하지 않는 세션 종료 시도

        Given: 세션이 존재하지 않음
        When: terminate_session(invalid_id) 호출
        Then: AppException 발생
        """
        # Arrange
        from app.services.terminal import TerminalService

        service = TerminalService(docker_service=mock_docker_service)

        # Act & Assert
        with pytest.raises(AppException) as exc_info:
            await service.terminate_session(
                async_db_session, "session_invalid_not_exists"
            )

        assert "세션을 찾을 수 없습니다" in str(exc_info.value.message)
        assert exc_info.value.status_code == 404

    async def test_terminate_session_idempotent_when_already_terminated(
        self,
        async_db_session: AsyncSession,
        terminal_session_instance: TerminalSession,
        mock_docker_service: MagicMock,
    ) -> None:
        """
        이미 종료된 세션 재종료 시도 (멱등성)

        Given: 이미 종료된 세션
        When: terminate_session(session_id) 호출
        Then: 에러 없이 반환, Docker 삭제는 재호출하지 않음
        """
        # Arrange
        from app.services.terminal import TerminalService

        service = TerminalService(docker_service=mock_docker_service)

        # 첫 번째 종료
        await service.terminate_session(async_db_session, terminal_session_instance.id)
        first_terminated_at = (
            await service.get_session_by_id(
                async_db_session, terminal_session_instance.id
            )
        ).terminated_at

        # Act: 두 번째 종료 시도
        session = await service.terminate_session(
            async_db_session, terminal_session_instance.id
        )

        # Assert
        assert session.status == TerminalStatus.TERMINATED
        assert (
            session.terminated_at == first_terminated_at
        ), "종료 시각은 변경되지 않아야 함"

        # Docker 삭제는 첫 번째만 호출되어야 함
        assert mock_docker_service.remove_container.call_count == 1

    async def test_terminate_session_handles_docker_error_gracefully(
        self,
        async_db_session: AsyncSession,
        terminal_session_instance: TerminalSession,
        mock_docker_service: MagicMock,
    ) -> None:
        """
        Docker 컨테이너 삭제 실패 시에도 세션 종료 처리

        Given: Docker 컨테이너 삭제가 실패
        When: terminate_session() 호출
        Then: 세션은 종료 상태로 변경, 에러 로깅만 수행
        """
        # Arrange
        from app.services.terminal import TerminalService

        mock_docker_service.remove_container.side_effect = AppException(
            message="컨테이너를 찾을 수 없습니다", status_code=404
        )

        service = TerminalService(docker_service=mock_docker_service)

        # Act
        session = await service.terminate_session(
            async_db_session, terminal_session_instance.id
        )

        # Assert
        assert (
            session.status == TerminalStatus.TERMINATED
        ), "Docker 에러에도 세션은 종료되어야 함"
        assert session.terminated_at is not None


@pytest.mark.asyncio
@pytest.mark.unit
class TestTerminalServiceCommandExecution:
    """터미널 명령어 실행 테스트"""

    async def test_execute_command_succeeds(
        self,
        async_db_session: AsyncSession,
        terminal_session_instance: TerminalSession,
        mock_docker_service: MagicMock,
    ) -> None:
        """
        명령어 실행 성공

        Given: 활성 세션이 존재
        When: execute_command(session_id, "ls -la") 호출
        Then: 명령어 실행 결과 반환
        """
        # Arrange
        from app.services.terminal import TerminalService

        mock_docker_service.execute_command.return_value = {
            "exit_code": 0,
            "output": "total 8\ndrwxr-xr-x 2 root root 4096 Oct 28 12:00 .\n",
            "error": "",
        }

        service = TerminalService(docker_service=mock_docker_service)

        # Act
        result = await service.execute_command(
            async_db_session, terminal_session_instance.id, "ls -la"
        )

        # Assert
        assert result["exit_code"] == 0
        assert "total 8" in result["output"]
        assert result["error"] == ""

        # Docker 실행 호출 확인
        mock_docker_service.execute_command.assert_called_once_with(
            terminal_session_instance.container_id, "ls -la", timeout=5
        )

    async def test_execute_command_fails_when_session_not_found(
        self,
        async_db_session: AsyncSession,
        mock_docker_service: MagicMock,
    ) -> None:
        """
        존재하지 않는 세션에 명령어 실행 시도

        Given: 세션이 존재하지 않음
        When: execute_command(invalid_id, "ls") 호출
        Then: AppException 발생
        """
        # Arrange
        from app.services.terminal import TerminalService

        service = TerminalService(docker_service=mock_docker_service)

        # Act & Assert
        with pytest.raises(AppException) as exc_info:
            await service.execute_command(
                async_db_session, "session_invalid_not_exists", "ls"
            )

        assert "세션을 찾을 수 없습니다" in str(exc_info.value.message)
        assert exc_info.value.status_code == 404

    async def test_execute_command_fails_when_session_expired(
        self,
        async_db_session: AsyncSession,
        tip_instance: Tip,
        mock_docker_service: MagicMock,
    ) -> None:
        """
        만료된 세션에 명령어 실행 시도

        Given: 만료된 세션이 존재
        When: execute_command(session_id, "ls") 호출
        Then: AppException 발생
        """
        # Arrange
        from app.services.terminal import TerminalService

        # 만료된 세션 생성
        expired_session = TerminalSession(
            tip_id=tip_instance.id,
            container_id="expired123",
            status=TerminalStatus.ACTIVE,
            ip_address=IPv4Address("192.168.1.1"),
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        async_db_session.add(expired_session)
        await async_db_session.flush()

        service = TerminalService(docker_service=mock_docker_service)

        # Act & Assert
        with pytest.raises(AppException) as exc_info:
            await service.execute_command(async_db_session, expired_session.id, "ls")

        assert "세션이 만료되었습니다" in str(exc_info.value.message)
        assert exc_info.value.status_code == 403

    async def test_execute_command_fails_when_session_terminated(
        self,
        async_db_session: AsyncSession,
        tip_instance: Tip,
        mock_docker_service: MagicMock,
    ) -> None:
        """
        종료된 세션에 명령어 실행 시도

        Given: 종료된 세션이 존재
        When: execute_command(session_id, "ls") 호출
        Then: AppException 발생
        """
        # Arrange
        from app.services.terminal import TerminalService

        # 종료된 세션 생성
        terminated_session = TerminalSession(
            tip_id=tip_instance.id,
            container_id="terminated123",
            status=TerminalStatus.TERMINATED,
            ip_address=IPv4Address("192.168.1.1"),
            terminated_at=datetime.now(timezone.utc),
        )
        async_db_session.add(terminated_session)
        await async_db_session.flush()

        service = TerminalService(docker_service=mock_docker_service)

        # Act & Assert
        with pytest.raises(AppException) as exc_info:
            await service.execute_command(
                async_db_session, terminated_session.id, "ls"
            )

        assert "세션이 종료되었습니다" in str(exc_info.value.message)
        assert exc_info.value.status_code == 403

    async def test_execute_command_blocks_dangerous_command(
        self,
        async_db_session: AsyncSession,
        terminal_session_instance: TerminalSession,
        mock_docker_service: MagicMock,
    ) -> None:
        """
        위험한 명령어 실행 차단

        Given: 활성 세션이 존재
        When: execute_command(session_id, "rm -rf /") 호출
        Then: AppException 발생
        """
        # Arrange
        from app.services.terminal import TerminalService

        mock_docker_service.is_command_safe.return_value = False

        service = TerminalService(docker_service=mock_docker_service)

        # Act & Assert
        with pytest.raises(AppException) as exc_info:
            await service.execute_command(
                async_db_session, terminal_session_instance.id, "rm -rf /"
            )

        assert "위험한 명령어" in str(exc_info.value.message)
        assert exc_info.value.status_code == 403

        # Docker 실행되지 않았는지 확인
        mock_docker_service.execute_command.assert_not_called()

    async def test_execute_command_with_custom_timeout(
        self,
        async_db_session: AsyncSession,
        terminal_session_instance: TerminalSession,
        mock_docker_service: MagicMock,
    ) -> None:
        """
        커스텀 타임아웃으로 명령어 실행

        Given: 활성 세션이 존재
        When: execute_command(session_id, "sleep 10", timeout=10) 호출
        Then: 10초 타임아웃 적용
        """
        # Arrange
        from app.services.terminal import TerminalService

        service = TerminalService(docker_service=mock_docker_service)

        # Act
        await service.execute_command(
            async_db_session, terminal_session_instance.id, "sleep 10", timeout=10
        )

        # Assert
        mock_docker_service.execute_command.assert_called_once_with(
            terminal_session_instance.container_id, "sleep 10", timeout=10
        )


@pytest.mark.asyncio
@pytest.mark.unit
class TestTerminalServiceCleanupTasks:
    """터미널 세션 정리 작업 테스트"""

    async def test_cleanup_expired_sessions_marks_expired(
        self,
        async_db_session: AsyncSession,
        tip_instance: Tip,
        mock_docker_service: MagicMock,
    ) -> None:
        """
        만료된 세션 자동 정리

        Given: 만료된 활성 세션들이 존재
        When: cleanup_expired_sessions() 호출
        Then: status=EXPIRED로 변경, 컨테이너 삭제
        """
        # Arrange
        from app.services.terminal import TerminalService

        # 만료된 세션 3개 생성
        expired_sessions = []
        for i in range(3):
            session = TerminalSession(
                tip_id=tip_instance.id,
                container_id=f"expired{i}",
                status=TerminalStatus.ACTIVE,
                ip_address=IPv4Address("192.168.1.1"),
                expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
            )
            async_db_session.add(session)
            expired_sessions.append(session)

        # 유효한 세션 1개
        valid_session = TerminalSession(
            tip_id=tip_instance.id,
            container_id="valid123",
            status=TerminalStatus.ACTIVE,
            ip_address=IPv4Address("192.168.1.1"),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
        )
        async_db_session.add(valid_session)

        await async_db_session.flush()

        service = TerminalService(docker_service=mock_docker_service)

        # Act
        cleaned_count = await service.cleanup_expired_sessions(async_db_session)

        # Assert
        assert cleaned_count == 3, "만료된 세션 3개가 정리되어야 함"

        # 만료된 세션들 상태 확인
        for session in expired_sessions:
            await async_db_session.refresh(session)
            assert session.status == TerminalStatus.EXPIRED
            assert session.terminated_at is not None

        # 유효한 세션은 변경되지 않음
        await async_db_session.refresh(valid_session)
        assert valid_session.status == TerminalStatus.ACTIVE
        assert valid_session.terminated_at is None

        # Docker 삭제 호출 확인 (3번 호출되어야 함)
        assert mock_docker_service.remove_container.call_count == 3

    async def test_cleanup_expired_sessions_handles_docker_errors(
        self,
        async_db_session: AsyncSession,
        tip_instance: Tip,
        mock_docker_service: MagicMock,
    ) -> None:
        """
        컨테이너 삭제 실패 시에도 정리 작업 계속 진행

        Given: 만료된 세션이 존재, Docker 삭제 실패
        When: cleanup_expired_sessions() 호출
        Then: 세션은 EXPIRED로 변경, 에러 로깅만 수행
        """
        # Arrange
        from app.services.terminal import TerminalService

        expired_session = TerminalSession(
            tip_id=tip_instance.id,
            container_id="expired123",
            status=TerminalStatus.ACTIVE,
            ip_address=IPv4Address("192.168.1.1"),
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        async_db_session.add(expired_session)
        await async_db_session.flush()

        # Docker 삭제 실패 모킹
        mock_docker_service.remove_container.side_effect = AppException(
            message="컨테이너를 찾을 수 없습니다", status_code=404
        )

        service = TerminalService(docker_service=mock_docker_service)

        # Act
        cleaned_count = await service.cleanup_expired_sessions(async_db_session)

        # Assert
        assert cleaned_count == 1, "Docker 에러에도 정리 작업은 완료되어야 함"

        await async_db_session.refresh(expired_session)
        assert expired_session.status == TerminalStatus.EXPIRED

    async def test_get_sessions_count_by_status(
        self,
        async_db_session: AsyncSession,
        tip_instance: Tip,
    ) -> None:
        """
        상태별 세션 개수 조회

        Given: 다양한 상태의 세션들이 존재
        When: get_sessions_count_by_status() 호출
        Then: 상태별 개수 반환
        """
        # Arrange
        from app.services.terminal import TerminalService

        # 활성 세션 3개
        for i in range(3):
            session = TerminalSession(
                tip_id=tip_instance.id,
                container_id=f"active{i}",
                status=TerminalStatus.ACTIVE,
                ip_address=IPv4Address("192.168.1.1"),
            )
            async_db_session.add(session)

        # 종료된 세션 2개
        for i in range(2):
            session = TerminalSession(
                tip_id=tip_instance.id,
                container_id=f"terminated{i}",
                status=TerminalStatus.TERMINATED,
                ip_address=IPv4Address("192.168.1.1"),
            )
            async_db_session.add(session)

        # 만료된 세션 1개
        session = TerminalSession(
            tip_id=tip_instance.id,
            container_id="expired",
            status=TerminalStatus.EXPIRED,
            ip_address=IPv4Address("192.168.1.1"),
        )
        async_db_session.add(session)

        await async_db_session.flush()

        service = TerminalService()

        # Act
        counts = await service.get_sessions_count_by_status(async_db_session)

        # Assert
        assert counts[TerminalStatus.ACTIVE] == 3
        assert counts[TerminalStatus.TERMINATED] == 2
        assert counts[TerminalStatus.EXPIRED] == 1
