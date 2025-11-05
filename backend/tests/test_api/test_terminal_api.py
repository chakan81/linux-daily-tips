"""
Terminal WebSocket API 테스트 (TDD - RED 단계)

WebSocket 터미널 엔드포인트 /ws/terminal/{session_id}를 테스트합니다:
- WebSocket 연결 성공/실패
- 메시지 프로토콜 (command, output, error, ping/pong)
- 세션 ID 검증 (존재하지 않는 세션)
- 만료된 세션 거부
- 동시 연결 처리
- 연결 끊김 처리

주의: Terminal WebSocket API가 구현되지 않았으므로 이 테스트들은 실패해야 합니다!
"""

import asyncio
import json
from datetime import datetime, timedelta, timezone
from ipaddress import IPv4Address
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import WebSocket
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.models.terminal import TerminalSession, TerminalStatus
from app.models.tip import Tip


@pytest.fixture
async def test_client() -> AsyncClient:
    """
    테스트용 AsyncClient

    FastAPI 앱에 연결된 HTTP 클라이언트를 제공합니다.
    """
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def sync_test_client() -> TestClient:
    """
    WebSocket 테스트용 동기 TestClient

    starlette.testclient.TestClient는 WebSocket 테스트를 지원합니다.
    """
    from app.main import app

    return TestClient(app)


@pytest.fixture
def mock_terminal_service() -> MagicMock:
    """
    Mock TerminalService

    실제 터미널 서비스를 호출하지 않고 테스트할 수 있도록
    TerminalService를 모킹합니다.
    """
    service = MagicMock()
    service.get_session_by_id = AsyncMock(return_value=None)
    service.is_session_expired = MagicMock(return_value=False)
    service.execute_command = AsyncMock(
        return_value={"exit_code": 0, "output": "test output", "error": ""}
    )
    return service


@pytest.mark.asyncio
@pytest.mark.integration
class TestTerminalWebSocketConnection:
    """WebSocket 연결 테스트"""

    async def test_websocket_connection_succeeds_with_valid_session(
        self,
        sync_test_client: TestClient,
        async_db_session: AsyncSession,
        terminal_session_instance: TerminalSession,
    ) -> None:
        """
        유효한 세션 ID로 WebSocket 연결 성공

        Given: 활성 세션이 존재
        When: /ws/terminal/{session_id} 연결 시도
        Then: 연결 성공, 초기 환영 메시지 수신
        """
        # Arrange
        session_id = terminal_session_instance.id

        # Act
        with sync_test_client.websocket_connect(
            f"/ws/terminal/{session_id}"
        ) as websocket:
            # Assert: 연결 성공
            assert websocket is not None

            # 초기 환영 메시지 수신 확인
            data = websocket.receive_json()
            assert data["type"] == "output"
            assert "Welcome" in data["data"]

    async def test_websocket_connection_fails_with_invalid_session(
        self,
        sync_test_client: TestClient,
    ) -> None:
        """
        존재하지 않는 세션 ID로 연결 시도

        Given: 세션이 존재하지 않음
        When: /ws/terminal/invalid_session_id 연결 시도
        Then: 연결 거부 (403 또는 404)
        """
        # Act & Assert
        with pytest.raises(WebSocketDisconnect) as exc_info:
            with sync_test_client.websocket_connect("/ws/terminal/invalid_session"):
                pass

        # WebSocket 거부 코드 확인
        assert exc_info.value.code in [403, 404, 1008]

    async def test_websocket_connection_fails_with_expired_session(
        self,
        sync_test_client: TestClient,
        async_db_session: AsyncSession,
        tip_instance: Tip,
    ) -> None:
        """
        만료된 세션으로 연결 시도

        Given: 만료된 세션이 존재
        When: /ws/terminal/{expired_session_id} 연결 시도
        Then: 연결 거부
        """
        # Arrange: 만료된 세션 생성
        expired_session = TerminalSession(
            tip_id=tip_instance.id,
            container_id="expired123",
            status=TerminalStatus.ACTIVE,
            ip_address=IPv4Address("192.168.1.1"),
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        async_db_session.add(expired_session)
        await async_db_session.flush()

        # Act & Assert
        with pytest.raises(WebSocketDisconnect) as exc_info:
            with sync_test_client.websocket_connect(
                f"/ws/terminal/{expired_session.id}"
            ):
                pass

        assert exc_info.value.code in [403, 1008]

    async def test_websocket_connection_fails_with_terminated_session(
        self,
        sync_test_client: TestClient,
        async_db_session: AsyncSession,
        tip_instance: Tip,
    ) -> None:
        """
        종료된 세션으로 연결 시도

        Given: 종료된 세션이 존재
        When: /ws/terminal/{terminated_session_id} 연결 시도
        Then: 연결 거부
        """
        # Arrange: 종료된 세션 생성
        terminated_session = TerminalSession(
            tip_id=tip_instance.id,
            container_id="terminated123",
            status=TerminalStatus.TERMINATED,
            ip_address=IPv4Address("192.168.1.1"),
            terminated_at=datetime.now(timezone.utc),
        )
        async_db_session.add(terminated_session)
        await async_db_session.flush()

        # Act & Assert
        with pytest.raises(WebSocketDisconnect) as exc_info:
            with sync_test_client.websocket_connect(
                f"/ws/terminal/{terminated_session.id}"
            ):
                pass

        assert exc_info.value.code in [403, 1008]


@pytest.mark.asyncio
@pytest.mark.integration
class TestTerminalWebSocketMessageProtocol:
    """WebSocket 메시지 프로토콜 테스트"""

    async def test_send_command_receives_output(
        self,
        sync_test_client: TestClient,
        async_db_session: AsyncSession,
        terminal_session_instance: TerminalSession,
    ) -> None:
        """
        명령어 전송 및 출력 수신

        Given: WebSocket 연결이 활성화됨
        When: {"type": "command", "data": "ls -la"} 전송
        Then: {"type": "output", "data": "...", "exit_code": 0} 수신
        """
        # Arrange
        session_id = terminal_session_instance.id

        with sync_test_client.websocket_connect(
            f"/ws/terminal/{session_id}"
        ) as websocket:
            # 초기 환영 메시지 수신
            welcome_msg = websocket.receive_json()
            assert welcome_msg["type"] == "output"

            # Act: 명령어 전송
            websocket.send_json({"type": "command", "data": "ls -la"})

            # Assert: 출력 수신
            response = websocket.receive_json()
            assert response["type"] == "output"
            assert "data" in response
            assert "exit_code" in response
            assert response["exit_code"] == 0

    async def test_send_invalid_command_receives_error(
        self,
        sync_test_client: TestClient,
        async_db_session: AsyncSession,
        terminal_session_instance: TerminalSession,
    ) -> None:
        """
        잘못된 명령어 전송 시 에러 수신

        Given: WebSocket 연결이 활성화됨
        When: {"type": "command", "data": "invalidcommand"} 전송
        Then: stderr 출력 또는 exit_code != 0
        """
        # Arrange
        session_id = terminal_session_instance.id

        with sync_test_client.websocket_connect(
            f"/ws/terminal/{session_id}"
        ) as websocket:
            # 초기 환영 메시지 수신
            websocket.receive_json()

            # Act: 잘못된 명령어 전송
            websocket.send_json({"type": "command", "data": "invalidcommand"})

            # Assert: 에러 수신
            response = websocket.receive_json()
            assert response["type"] == "output"
            assert response["exit_code"] != 0 or "not found" in response.get(
                "error", ""
            )

    async def test_send_dangerous_command_receives_error(
        self,
        sync_test_client: TestClient,
        async_db_session: AsyncSession,
        terminal_session_instance: TerminalSession,
    ) -> None:
        """
        위험한 명령어 전송 시 차단

        Given: WebSocket 연결이 활성화됨
        When: {"type": "command", "data": "rm -rf /"} 전송
        Then: {"type": "error", "code": "DANGEROUS_COMMAND"} 수신
        """
        # Arrange
        session_id = terminal_session_instance.id

        with sync_test_client.websocket_connect(
            f"/ws/terminal/{session_id}"
        ) as websocket:
            # 초기 환영 메시지 수신
            websocket.receive_json()

            # Act: 위험한 명령어 전송
            websocket.send_json({"type": "command", "data": "rm -rf /"})

            # Assert: 에러 수신
            response = websocket.receive_json()
            assert response["type"] == "error"
            assert "위험한 명령어" in response["message"]
            assert response["code"] == "DANGEROUS_COMMAND"

    async def test_ping_pong_mechanism(
        self,
        sync_test_client: TestClient,
        async_db_session: AsyncSession,
        terminal_session_instance: TerminalSession,
    ) -> None:
        """
        핑-퐁 연결 유지 메커니즘

        Given: WebSocket 연결이 활성화됨
        When: {"type": "ping"} 전송
        Then: {"type": "pong"} 수신
        """
        # Arrange
        session_id = terminal_session_instance.id

        with sync_test_client.websocket_connect(
            f"/ws/terminal/{session_id}"
        ) as websocket:
            # 초기 환영 메시지 수신
            websocket.receive_json()

            # Act: 핑 전송
            websocket.send_json({"type": "ping"})

            # Assert: 퐁 수신
            response = websocket.receive_json()
            assert response["type"] == "pong"
            assert "timestamp" in response

    async def test_send_malformed_message_receives_error(
        self,
        sync_test_client: TestClient,
        async_db_session: AsyncSession,
        terminal_session_instance: TerminalSession,
    ) -> None:
        """
        잘못된 형식의 메시지 전송 시 에러 수신

        Given: WebSocket 연결이 활성화됨
        When: {"invalid": "message"} 전송 (type 필드 없음)
        Then: {"type": "error", "code": "INVALID_MESSAGE"} 수신
        """
        # Arrange
        session_id = terminal_session_instance.id

        with sync_test_client.websocket_connect(
            f"/ws/terminal/{session_id}"
        ) as websocket:
            # 초기 환영 메시지 수신
            websocket.receive_json()

            # Act: 잘못된 메시지 전송
            websocket.send_json({"invalid": "message"})

            # Assert: 에러 수신
            response = websocket.receive_json()
            assert response["type"] == "error"
            assert "INVALID_MESSAGE" in response["code"]

    async def test_send_empty_command_receives_error(
        self,
        sync_test_client: TestClient,
        async_db_session: AsyncSession,
        terminal_session_instance: TerminalSession,
    ) -> None:
        """
        빈 명령어 전송 시 에러 수신

        Given: WebSocket 연결이 활성화됨
        When: {"type": "command", "data": ""} 전송
        Then: {"type": "error", "code": "EMPTY_COMMAND"} 수신
        """
        # Arrange
        session_id = terminal_session_instance.id

        with sync_test_client.websocket_connect(
            f"/ws/terminal/{session_id}"
        ) as websocket:
            # 초기 환영 메시지 수신
            websocket.receive_json()

            # Act: 빈 명령어 전송
            websocket.send_json({"type": "command", "data": ""})

            # Assert: 에러 수신
            response = websocket.receive_json()
            assert response["type"] == "error"
            assert "EMPTY_COMMAND" in response["code"]


@pytest.mark.asyncio
@pytest.mark.integration
class TestTerminalWebSocketSessionTimeout:
    """WebSocket 세션 타임아웃 테스트"""

    async def test_session_timeout_warning_sent(
        self,
        sync_test_client: TestClient,
        async_db_session: AsyncSession,
        tip_instance: Tip,
    ) -> None:
        """
        세션 만료 경고 메시지 전송

        Given: 세션이 10초 후 만료 예정
        When: WebSocket 연결 유지
        Then: {"type": "warning", "message": "세션이 10초 후 만료됩니다"} 수신
        """
        # Arrange: 20초 후 만료되는 세션 생성
        short_session = TerminalSession(
            tip_id=tip_instance.id,
            container_id="short123",
            status=TerminalStatus.ACTIVE,
            ip_address=IPv4Address("192.168.1.1"),
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=20),
        )
        async_db_session.add(short_session)
        await async_db_session.flush()

        with sync_test_client.websocket_connect(
            f"/ws/terminal/{short_session.id}"
        ) as websocket:
            # 초기 환영 메시지 수신
            websocket.receive_json()

            # Act: 10초 대기 (만료 10초 전)
            # 실제 구현에서는 백그라운드 태스크가 경고 전송
            # 테스트에서는 타임아웃 설정하여 메시지 수신 대기
            websocket.send_json({"type": "ping"})  # 연결 유지

            # Assert: 경고 메시지 수신 (타임아웃 내)
            # 실제로는 백그라운드 작업이 필요하므로 이 테스트는 모킹 필요
            pass

    async def test_websocket_closes_on_session_expiry(
        self,
        sync_test_client: TestClient,
        async_db_session: AsyncSession,
        tip_instance: Tip,
    ) -> None:
        """
        세션 만료 시 WebSocket 자동 종료

        Given: 세션이 만료됨
        When: WebSocket 연결 유지 중
        Then: 연결 자동 종료
        """
        # Arrange: 2초 후 만료되는 세션 생성
        expiring_session = TerminalSession(
            tip_id=tip_instance.id,
            container_id="expiring123",
            status=TerminalStatus.ACTIVE,
            ip_address=IPv4Address("192.168.1.1"),
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=2),
        )
        async_db_session.add(expiring_session)
        await async_db_session.flush()

        with pytest.raises(WebSocketDisconnect):
            with sync_test_client.websocket_connect(
                f"/ws/terminal/{expiring_session.id}"
            ) as websocket:
                # 초기 환영 메시지 수신
                websocket.receive_json()

                # Act: 3초 대기 (만료 시간 초과)
                import time

                time.sleep(3)

                # 메시지 전송 시도 (연결 끊김 확인)
                websocket.send_json({"type": "ping"})

                # Assert: WebSocketDisconnect 예외 발생


@pytest.mark.asyncio
@pytest.mark.integration
class TestTerminalWebSocketConcurrency:
    """WebSocket 동시 연결 테스트"""

    async def test_multiple_sessions_independent(
        self,
        sync_test_client: TestClient,
        async_db_session: AsyncSession,
        tip_instance: Tip,
    ) -> None:
        """
        여러 세션 독립적 실행

        Given: 여러 활성 세션이 존재
        When: 각 세션에 동시 WebSocket 연결
        Then: 각 세션은 독립적으로 동작
        """
        # Arrange: 2개 세션 생성
        session1 = TerminalSession(
            tip_id=tip_instance.id,
            container_id="session1",
            status=TerminalStatus.ACTIVE,
            ip_address=IPv4Address("192.168.1.1"),
        )
        session2 = TerminalSession(
            tip_id=tip_instance.id,
            container_id="session2",
            status=TerminalStatus.ACTIVE,
            ip_address=IPv4Address("192.168.1.2"),
        )
        async_db_session.add_all([session1, session2])
        await async_db_session.flush()

        # Act: 2개 WebSocket 동시 연결
        with sync_test_client.websocket_connect(
            f"/ws/terminal/{session1.id}"
        ) as ws1, sync_test_client.websocket_connect(
            f"/ws/terminal/{session2.id}"
        ) as ws2:
            # 초기 환영 메시지 수신
            ws1.receive_json()
            ws2.receive_json()

            # 각 세션에 다른 명령어 전송
            ws1.send_json({"type": "command", "data": "echo session1"})
            ws2.send_json({"type": "command", "data": "echo session2"})

            # Assert: 각 세션은 독립적으로 응답
            response1 = ws1.receive_json()
            response2 = ws2.receive_json()

            assert "session1" in response1["data"]
            assert "session2" in response2["data"]

    async def test_same_session_multiple_connections_last_wins(
        self,
        sync_test_client: TestClient,
        async_db_session: AsyncSession,
        terminal_session_instance: TerminalSession,
    ) -> None:
        """
        동일 세션에 여러 연결 시도 시 마지막 연결만 유효

        Given: 하나의 활성 세션이 존재
        When: 동일 세션에 2개 WebSocket 연결 시도
        Then: 첫 번째 연결은 끊김, 두 번째 연결만 유효
        """
        # Arrange
        session_id = terminal_session_instance.id

        # Act: 첫 번째 연결
        ws1 = sync_test_client.websocket_connect(f"/ws/terminal/{session_id}")
        ws1.__enter__()
        ws1.receive_json()  # 환영 메시지

        # 두 번째 연결 (첫 번째 연결 강제 종료 예상)
        with pytest.raises(WebSocketDisconnect):
            ws2 = sync_test_client.websocket_connect(f"/ws/terminal/{session_id}")
            ws2.__enter__()

            # Assert: 첫 번째 연결 끊김
            ws1.send_json({"type": "ping"})  # 연결 끊김 확인


@pytest.mark.asyncio
@pytest.mark.integration
class TestTerminalWebSocketDisconnection:
    """WebSocket 연결 끊김 처리 테스트"""

    async def test_client_disconnect_cleans_up_session(
        self,
        sync_test_client: TestClient,
        async_db_session: AsyncSession,
        terminal_session_instance: TerminalSession,
    ) -> None:
        """
        클라이언트 연결 종료 시 세션 정리

        Given: WebSocket 연결이 활성화됨
        When: 클라이언트가 연결 종료
        Then: 세션 상태 TERMINATED로 변경
        """
        # Arrange
        session_id = terminal_session_instance.id

        # Act: WebSocket 연결 후 종료
        with sync_test_client.websocket_connect(
            f"/ws/terminal/{session_id}"
        ) as websocket:
            websocket.receive_json()  # 환영 메시지
            # 연결 종료 (with 블록 종료 시 자동)

        # Assert: 세션 상태 확인
        await async_db_session.refresh(terminal_session_instance)
        assert terminal_session_instance.status == TerminalStatus.TERMINATED
        assert terminal_session_instance.terminated_at is not None

    async def test_server_disconnect_on_error(
        self,
        sync_test_client: TestClient,
        async_db_session: AsyncSession,
        terminal_session_instance: TerminalSession,
    ) -> None:
        """
        서버 에러 발생 시 연결 종료

        Given: WebSocket 연결이 활성화됨
        When: 서버에서 처리 불가능한 에러 발생
        Then: 연결 종료, 에러 메시지 전송
        """
        # Arrange
        session_id = terminal_session_instance.id

        with pytest.raises(WebSocketDisconnect):
            with sync_test_client.websocket_connect(
                f"/ws/terminal/{session_id}"
            ) as websocket:
                websocket.receive_json()  # 환영 메시지

                # Act: 서버 에러 유발 (예: 컨테이너 삭제 후 명령어 실행)
                # 실제 구현에서는 컨테이너가 없을 때 에러 발생
                websocket.send_json({"type": "command", "data": "ls"})

                # Assert: 에러 메시지 수신 후 연결 종료
                # 실제로는 컨테이너 에러 시뮬레이션 필요


@pytest.mark.asyncio
@pytest.mark.integration
class TestTerminalWebSocketEdgeCases:
    """WebSocket 엣지 케이스 테스트"""

    async def test_send_very_long_command(
        self,
        sync_test_client: TestClient,
        async_db_session: AsyncSession,
        terminal_session_instance: TerminalSession,
    ) -> None:
        """
        매우 긴 명령어 전송 시 제한

        Given: WebSocket 연결이 활성화됨
        When: 1000자 초과 명령어 전송
        Then: {"type": "error", "code": "COMMAND_TOO_LONG"} 수신
        """
        # Arrange
        session_id = terminal_session_instance.id

        with sync_test_client.websocket_connect(
            f"/ws/terminal/{session_id}"
        ) as websocket:
            websocket.receive_json()  # 환영 메시지

            # Act: 1001자 명령어 전송
            long_command = "echo " + "X" * 1000
            websocket.send_json({"type": "command", "data": long_command})

            # Assert: 에러 수신
            response = websocket.receive_json()
            assert response["type"] == "error"
            assert "COMMAND_TOO_LONG" in response["code"]

    async def test_rapid_message_sending(
        self,
        sync_test_client: TestClient,
        async_db_session: AsyncSession,
        terminal_session_instance: TerminalSession,
    ) -> None:
        """
        빠른 메시지 연속 전송 처리

        Given: WebSocket 연결이 활성화됨
        When: 10개 명령어를 빠르게 연속 전송
        Then: 모든 명령어 순차 처리, 응답 수신
        """
        # Arrange
        session_id = terminal_session_instance.id

        with sync_test_client.websocket_connect(
            f"/ws/terminal/{session_id}"
        ) as websocket:
            websocket.receive_json()  # 환영 메시지

            # Act: 10개 명령어 연속 전송
            for i in range(10):
                websocket.send_json({"type": "command", "data": f"echo {i}"})

            # Assert: 10개 응답 수신
            for i in range(10):
                response = websocket.receive_json()
                assert response["type"] == "output"
                # 순서 보장 확인 (선택적)

    async def test_unicode_command_handling(
        self,
        sync_test_client: TestClient,
        async_db_session: AsyncSession,
        terminal_session_instance: TerminalSession,
    ) -> None:
        """
        유니코드 명령어 처리

        Given: WebSocket 연결이 활성화됨
        When: 유니코드 문자가 포함된 명령어 전송
        Then: 정상 처리 및 응답
        """
        # Arrange
        session_id = terminal_session_instance.id

        with sync_test_client.websocket_connect(
            f"/ws/terminal/{session_id}"
        ) as websocket:
            websocket.receive_json()  # 환영 메시지

            # Act: 유니코드 명령어 전송
            websocket.send_json({"type": "command", "data": "echo '안녕하세요 🚀'"})

            # Assert: 응답 수신
            response = websocket.receive_json()
            assert response["type"] == "output"
            assert response["exit_code"] == 0

    async def test_json_injection_prevention(
        self,
        sync_test_client: TestClient,
        async_db_session: AsyncSession,
        terminal_session_instance: TerminalSession,
    ) -> None:
        """
        JSON 인젝션 공격 방지

        Given: WebSocket 연결이 활성화됨
        When: JSON 특수 문자가 포함된 명령어 전송
        Then: 이스케이핑 처리되어 안전하게 실행
        """
        # Arrange
        session_id = terminal_session_instance.id

        with sync_test_client.websocket_connect(
            f"/ws/terminal/{session_id}"
        ) as websocket:
            websocket.receive_json()  # 환영 메시지

            # Act: JSON 특수 문자 포함 명령어
            websocket.send_json(
                {"type": "command", "data": 'echo "{\\"test\\": \\"value\\"}"\n'}
            )

            # Assert: 정상 처리
            response = websocket.receive_json()
            assert response["type"] == "output"
            assert response["exit_code"] == 0
