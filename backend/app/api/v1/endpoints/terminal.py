"""
Terminal API 엔드포인트

웹 터미널 에뮬레이터를 위한 REST API 및 WebSocket 엔드포인트입니다.
- POST /session: 새 세션 생성
- DELETE /session/{session_id}: 세션 종료
- WS /ws/{session_id}: WebSocket 실시간 통신
"""

import json
import logging
from datetime import datetime
from ipaddress import IPv4Address, IPv6Address, ip_address

from fastapi import APIRouter, Depends, HTTPException, Path, Request, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_async_session as get_db
from app.core.dependencies import get_terminal_service
from app.core.exceptions import AppException
from app.core.id_prefixes import IDPrefix
from app.core.ulid_helper import validate_id_type
from app.schemas.terminal import (
    TerminalSessionCreate,
    TerminalSessionResponse,
    WSCommandMessage,
    WSErrorMessage,
    WSOutputMessage,
    WSPingMessage,
    WSPongMessage,
)
from app.services.terminal_service import TerminalService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/session", summary="터미널 세션 생성", tags=["terminal"])
async def create_terminal_session(
    request: Request,
    session_data: TerminalSessionCreate,
    db: AsyncSession = Depends(get_db),
    service: TerminalService = Depends(get_terminal_service),
) -> TerminalSessionResponse:
    """
    새 터미널 세션 생성

    Docker 컨테이너 기반 샌드박스 터미널 환경을 생성합니다.
    세션은 30분 후 자동 만료됩니다.

    Args:
        session_data: 세션 생성 데이터
            - tip_id: 연결할 Tip ID (선택적)
            - session_data: 세션 메타데이터 (선택적)
        db: 데이터베이스 세션 (자동 주입)
        service: TerminalService (자동 주입)

    Returns:
        TerminalSessionResponse: 생성된 세션 정보
            - session_id: 세션 ID
            - container_id: Docker 컨테이너 ID
            - ws_url: WebSocket 연결 URL
            - status: 세션 상태
            - expires_at: 만료 시각

    Raises:
        HTTPException:
            - 404: tip_id가 존재하지 않는 경우
            - 500: 컨테이너 생성 실패

    Example:
        ```
        POST /api/v1/terminal/session
        Content-Type: application/json

        {
            "tip_id": "tip_01JCAW0V1QQ9KZ2F3XHBP8TGNY",
            "session_data": {"terminal_size": {"rows": 24, "cols": 80}}
        }

        Response:
        {
            "session_id": "session_01JCAW0V1QQ9KZ2F3XHBP8TGNY",
            "container_id": "abc123def456",
            "ws_url": "ws://localhost:8000/api/v1/terminal/ws/session_01JCAW0V1QQ9KZ2F3XHBP8TGNY",
            "status": "active",
            "expires_at": "2025-10-28T12:30:00Z"
        }
        ```

    Note:
        - 세션 생성 시간: 1-2초 (프로토타입 목표)
        - 30분 후 자동 만료 및 컨테이너 삭제
        - IP 주소 및 User-Agent 자동 수집 (보안 추적)
    """
    try:
        # 클라이언트 IP 주소 추출
        client_ip: IPv4Address | IPv6Address | None = None
        if request.client and request.client.host:
            try:
                client_ip = ip_address(request.client.host)
            except ValueError:
                logger.warning(f"잘못된 IP 주소 형식: {request.client.host}")

        # User-Agent 추출
        user_agent = request.headers.get("user-agent")

        # 세션 생성
        session = await service.create_session(
            db, session_data, ip_address=client_ip, user_agent=user_agent
        )

        # WebSocket URL 생성
        # request.url.scheme이 http면 ws, https면 wss
        ws_scheme = "wss" if request.url.scheme == "https" else "ws"
        ws_url = f"{ws_scheme}://{request.url.netloc}/api/v1/terminal/ws/{session.id}"

        await db.commit()

        logger.info(f"세션 생성 완료: {session.id}")

        return TerminalSessionResponse(
            session_id=session.id,
            container_id=session.container_id or "unknown",
            ws_url=ws_url,
            status=session.status.value,
            expires_at=session.expires_at,
        )

    except Exception as e:
        await db.rollback()
        logger.error(f"세션 생성 실패: {str(e)}", exc_info=True)
        raise


@router.delete("/session/{session_id}", summary="터미널 세션 종료", tags=["terminal"])
async def terminate_terminal_session(
    session_id: str = Path(
        ...,
        description="세션 ID (session_xxxx 형식)",
        pattern="^session_[0-9A-Z]{26}$",
    ),
    db: AsyncSession = Depends(get_db),
    service: TerminalService = Depends(get_terminal_service),
) -> dict:
    """
    터미널 세션 종료

    세션을 수동으로 종료하고 컨테이너를 삭제합니다.

    Args:
        session_id: 종료할 세션 ID
        db: 데이터베이스 세션 (자동 주입)
        service: TerminalService (자동 주입)

    Returns:
        dict: 종료 결과
            - success: 성공 여부
            - session_id: 세션 ID
            - terminated_at: 종료 시각

    Raises:
        HTTPException:
            - 400: ID 형식이 올바르지 않은 경우
            - 404: 세션을 찾을 수 없는 경우

    Example:
        ```
        DELETE /api/v1/terminal/session/session_01JCAW0V1QQ9KZ2F3XHBP8TGNY

        Response:
        {
            "success": true,
            "session_id": "session_01JCAW0V1QQ9KZ2F3XHBP8TGNY",
            "terminated_at": "2025-10-28T12:15:00Z"
        }
        ```

    Note:
        - 멱등성 보장: 이미 종료된 세션도 성공 반환
        - 컨테이너 자동 삭제
    """
    # ID 타입 검증
    if not validate_id_type(session_id, IDPrefix.SESSION):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid session ID format. Expected 'session_' prefix, got: {session_id}",
        )

    try:
        # 세션 종료
        await service.terminate_session(db, session_id)
        await db.commit()

        logger.info(f"세션 종료 완료: {session_id}")

        return {
            "success": True,
            "session_id": session_id,
            "terminated_at": datetime.utcnow().isoformat() + "Z",
        }

    except Exception as e:
        await db.rollback()
        logger.error(f"세션 종료 실패: {str(e)}", exc_info=True)
        raise


@router.websocket("/ws/{session_id}")
async def websocket_terminal(
    websocket: WebSocket,
    session_id: str = Path(
        ...,
        description="세션 ID (session_xxxx 형식)",
        pattern="^session_[0-9A-Z]{26}$",
    ),
    db: AsyncSession = Depends(get_db),
    service: TerminalService = Depends(get_terminal_service),
):
    """
    WebSocket 터미널 통신 엔드포인트

    실시간 터미널 명령어 실행 및 출력 스트리밍을 제공합니다.

    WebSocket 프로토콜:
        - 클라이언트 → 서버: {"type": "command", "data": "ls -la"}
        - 서버 → 클라이언트: {"type": "output", "data": "..."}
        - 에러: {"type": "error", "code": "...", "message": "..."}
        - Ping/Pong: {"type": "ping"} ↔ {"type": "pong"}

    Args:
        websocket: WebSocket 연결
        session_id: 세션 ID
        db: 데이터베이스 세션 (자동 주입)
        service: TerminalService (자동 주입)

    Example:
        ```javascript
        const ws = new WebSocket('ws://localhost:8000/api/v1/terminal/ws/session_01JCAW...');

        // 명령어 전송
        ws.send(JSON.stringify({
            type: "command",
            data: "ls -la"
        }));

        // 출력 수신
        ws.onmessage = (event) => {
            const msg = JSON.parse(event.data);
            if (msg.type === "output") {
                console.log(msg.data);
            }
        };
        ```

    Note:
        - 연결 시 세션 유효성 검증
        - 30초마다 Ping/Pong으로 연결 유지
        - 세션 만료 시 자동 연결 종료
    """
    # ID 타입 검증
    if not validate_id_type(session_id, IDPrefix.SESSION):
        await websocket.close(code=1008, reason="Invalid session ID format")
        return

    # WebSocket 연결 먼저 수락 (세션 검증 전에)
    await websocket.accept()
    logger.info(f"WebSocket 연결 수락 시도: {session_id}")

    try:
        # 세션 조회 및 검증
        try:
            session = await service.get_session(db, session_id, check_expiry=True)
            logger.info(f"WebSocket 세션 검증 완료: {session_id}")
        except AppException as e:
            # 세션 검증 실패 (존재하지 않음/만료됨/종료됨)
            logger.warning(f"WebSocket 세션 검증 실패: {session_id}, {e.detail}")
            error_msg = WSErrorMessage(
                code="SESSION_ERROR",
                message=e.detail,
            )
            await websocket.send_text(error_msg.model_dump_json())
            await websocket.close(code=1008)
            return

        # 초기 메시지: 프롬프트 전송
        welcome_msg = WSOutputMessage(
            data="Welcome to Linux Daily Tips Terminal!\nlinuxuser@linux-tips:~$ "
        )
        await websocket.send_text(welcome_msg.model_dump_json())

        # 메시지 수신 루프
        while True:
            try:
                # 클라이언트로부터 메시지 수신
                raw_data = await websocket.receive_text()
                data = json.loads(raw_data)

                msg_type = data.get("type")

                # Ping 메시지 처리
                if msg_type == "ping":
                    pong_msg = WSPongMessage()
                    await websocket.send_text(pong_msg.model_dump_json())
                    continue

                # Command 메시지 처리
                if msg_type == "command":
                    command = data.get("data", "").strip()

                    if not command:
                        continue

                    logger.info(f"명령어 수신: [{session_id}] {command}")

                    try:
                        # 명령어 실행
                        result = await service.execute_command(db, session_id, command)

                        # 출력 전송 (stdout + stderr)
                        output = result.stdout
                        if result.stderr:
                            output += f"\n{result.stderr}"

                        output_msg = WSOutputMessage(
                            data=output, exit_code=result.exit_code
                        )
                        await websocket.send_text(output_msg.model_dump_json())

                        # 프롬프트 다시 전송 (다음 명령어 대기)
                        prompt_msg = WSOutputMessage(
                            data="linuxuser@linux-tips:~$ "
                        )
                        await websocket.send_text(prompt_msg.model_dump_json())

                    except Exception as e:
                        # 명령어 실행 에러 전송
                        error_msg = WSErrorMessage(
                            code="COMMAND_ERROR",
                            message=str(e),
                        )
                        await websocket.send_text(error_msg.model_dump_json())

                        # 에러 후에도 프롬프트 전송
                        prompt_msg = WSOutputMessage(
                            data="linuxuser@linux-tips:~$ "
                        )
                        await websocket.send_text(prompt_msg.model_dump_json())

                else:
                    # 알 수 없는 메시지 타입
                    logger.warning(f"알 수 없는 메시지 타입: {msg_type}")

            except WebSocketDisconnect:
                logger.info(f"WebSocket 연결 종료: {session_id}")
                break
            except json.JSONDecodeError:
                logger.warning(f"잘못된 JSON 메시지: {raw_data}")
                error_msg = WSErrorMessage(
                    code="INVALID_JSON",
                    message="잘못된 JSON 형식입니다",
                )
                await websocket.send_text(error_msg.model_dump_json())
            except Exception as e:
                logger.error(f"메시지 처리 중 오류: {str(e)}", exc_info=True)
                error_msg = WSErrorMessage(
                    code="SERVER_ERROR",
                    message="서버 오류가 발생했습니다",
                    details=str(e),
                )
                await websocket.send_text(error_msg.model_dump_json())

    except Exception as e:
        logger.error(f"WebSocket 연결 실패: {str(e)}", exc_info=True)
        try:
            await websocket.close(code=1011, reason=str(e))
        except Exception:
            pass
    finally:
        # 연결 종료 시 세션 종료 (선택적)
        # 사용자가 명시적으로 종료하지 않아도 WebSocket 끊김 시 세션 종료
        try:
            await service.terminate_session(db, session_id)
            await db.commit()
            logger.info(f"WebSocket 종료로 세션 자동 종료: {session_id}")
        except Exception as e:
            logger.warning(f"세션 자동 종료 실패: {str(e)}")
