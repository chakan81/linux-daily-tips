"""
Terminal Pydantic 스키마

WebSocket 터미널 에뮬레이터 API 요청/응답 스키마입니다.
- TerminalSessionCreate: 세션 생성 요청
- TerminalSessionResponse: 세션 응답
- CommandRequest: 터미널 명령어 요청
- CommandResponse: 명령어 실행 결과
- WebSocket 메시지 스키마
"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class TerminalSessionCreate(BaseModel):
    """
    터미널 세션 생성 요청 스키마

    사용자가 새 터미널 세션을 시작할 때 사용합니다.
    """

    tip_id: str | None = Field(
        default=None,
        description="연결할 Tip ID (선택적, 익명 세션 가능)",
        pattern="^tip_[0-9A-Z]{26}$",
        examples=["tip_01JCAW0V1QQ9KZ2F3XHBP8TGNY"],
    )

    session_data: dict[str, Any] = Field(
        default_factory=dict,
        description="세션 메타데이터 (터미널 크기 등)",
        examples=[{"terminal_size": {"rows": 24, "cols": 80}}],
    )


class TerminalSessionResponse(BaseModel):
    """
    터미널 세션 응답 스키마

    세션 생성 후 클라이언트에 반환되는 정보입니다.
    """

    session_id: str = Field(
        ...,
        description="생성된 세션 ID",
        pattern="^session_[0-9A-Z]{26}$",
        examples=["session_01JCAW0V1QQ9KZ2F3XHBP8TGNY"],
    )

    container_id: str = Field(
        ...,
        description="Docker 컨테이너 ID",
        examples=["abc123def456"],
    )

    status: str = Field(
        ...,
        description="세션 상태 (active/terminated/expired)",
        examples=["active"],
    )

    expires_at: datetime = Field(
        ...,
        description="세션 만료 시각 (UTC)",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "session_01JCAW0V1QQ9KZ2F3XHBP8TGNY",
                "container_id": "abc123def456",
                "status": "active",
                "expires_at": "2025-10-28T12:30:00Z",
            }
        },
    )


class CommandRequest(BaseModel):
    """
    터미널 명령어 요청 스키마

    사용자가 터미널에 입력한 명령어를 서버로 전송할 때 사용합니다.
    """

    command: str = Field(
        ...,
        max_length=1000,
        description="실행할 Bash 명령어 (최대 1000자)",
        examples=["ls -la", "pwd", "echo 'Hello, Linux!'"],
    )


class CommandResponse(BaseModel):
    """
    명령어 실행 결과 스키마

    Docker 컨테이너에서 명령어 실행 후 반환되는 결과입니다.
    """

    stdout: str = Field(
        default="",
        description="표준 출력",
    )

    stderr: str = Field(
        default="",
        description="표준 에러",
    )

    exit_code: int = Field(
        ...,
        description="종료 코드 (0=성공, 비0=실패)",
    )

    execution_time: float = Field(
        ...,
        ge=0,
        description="실행 시간 (초)",
    )


# WebSocket 메시지 스키마


class WSMessageBase(BaseModel):
    """WebSocket 메시지 베이스 클래스"""

    type: str = Field(
        ...,
        description="메시지 타입",
    )

    timestamp: datetime = Field(
        default_factory=lambda: datetime.utcnow(),
        description="메시지 전송 시각 (UTC)",
    )


class WSCommandMessage(WSMessageBase):
    """
    WebSocket 명령어 메시지 (클라이언트 → 서버)

    사용자가 터미널에 명령어를 입력하면 이 메시지로 전송됩니다.
    """

    type: Literal["command"] = "command"
    data: str = Field(
        ...,
        max_length=1000,
        description="실행할 명령어",
    )


class WSOutputMessage(WSMessageBase):
    """
    WebSocket 출력 메시지 (서버 → 클라이언트)

    명령어 실행 결과를 클라이언트로 전송할 때 사용합니다.
    """

    type: Literal["output"] = "output"
    data: str = Field(
        ...,
        description="명령어 출력 (stdout + stderr)",
    )
    exit_code: int | None = Field(
        default=None,
        description="종료 코드 (선택적)",
    )


class WSErrorMessage(WSMessageBase):
    """
    WebSocket 에러 메시지 (서버 → 클라이언트)

    명령어 실행 실패나 시스템 오류 시 클라이언트에 전송합니다.
    """

    type: Literal["error"] = "error"
    code: str = Field(
        ...,
        description="에러 코드 (예: CONTAINER_ERROR, TIMEOUT)",
    )
    message: str = Field(
        ...,
        description="에러 메시지",
    )
    details: str | None = Field(
        default=None,
        description="상세 에러 정보 (선택적)",
    )


class WSWarningMessage(WSMessageBase):
    """
    WebSocket 경고 메시지 (서버 → 클라이언트)

    세션 타임아웃 경고 등을 클라이언트에 전송합니다.
    """

    type: Literal["warning"] = "warning"
    message: str = Field(
        ...,
        description="경고 메시지",
    )


class WSPingMessage(WSMessageBase):
    """
    WebSocket Ping 메시지 (클라이언트 → 서버)

    연결 유지를 위한 하트비트 메시지입니다.
    """

    type: Literal["ping"] = "ping"


class WSPongMessage(WSMessageBase):
    """
    WebSocket Pong 메시지 (서버 → 클라이언트)

    Ping에 대한 응답 메시지입니다.
    """

    type: Literal["pong"] = "pong"


# Union type for WebSocket messages
WSMessage = (
    WSCommandMessage
    | WSOutputMessage
    | WSErrorMessage
    | WSWarningMessage
    | WSPingMessage
    | WSPongMessage
)
