"""
터미널 세션 비즈니스 로직 서비스 (조율 레이어)

터미널 에뮬레이터 세션의 전체 생명주기를 관리합니다.
- 세션 생성/조회/종료
- Docker 컨테이너 관리
- 명령어 실행 (보안 검증 포함)
- 만료된 세션 자동 정리
"""

from ipaddress import IPv4Address, IPv6Address

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.models.terminal import TerminalSession, TerminalStatus
from app.schemas.terminal import CommandResponse, TerminalSessionCreate
from app.services.docker_service import DockerService
from app.services.terminal import command_executor, session_lifecycle, session_manager


class TerminalService:
    """
    터미널 세션 비즈니스 로직 서비스 계층

    데이터베이스 접근 및 Docker 컨테이너 관리를 조율합니다.

    Attributes:
        docker_service: DockerService 인스턴스
    """

    def __init__(self, docker_service: DockerService | None = None) -> None:
        """
        TerminalService 초기화

        Args:
            docker_service: DockerService (선택적, None이면 자동 생성)
        """
        self.docker_service = docker_service or DockerService()

    async def create_session(
        self,
        db: AsyncSession,
        session_data: TerminalSessionCreate,
        ip_address: IPv4Address | IPv6Address | None = None,
        user_agent: str | None = None,
    ) -> TerminalSession:
        """
        새 터미널 세션 생성 (DB + Docker)

        Args:
            db: 데이터베이스 세션
            session_data: 세션 생성 데이터
            ip_address: 사용자 IP 주소 (선택적)
            user_agent: 사용자 브라우저 정보 (선택적)

        Returns:
            TerminalSession: 생성된 세션

        Raises:
            AppException:
                - 404: tip_id가 존재하지 않는 경우
                - 500: 컨테이너 생성 실패
        """
        return await session_manager.create_session(
            db, session_data, self.docker_service, ip_address, user_agent
        )

    async def get_session_by_id(
        self, db: AsyncSession, session_id: str
    ) -> TerminalSession | None:
        """
        세션 ID로 조회 (만료 체크 없음)

        Args:
            db: 데이터베이스 세션
            session_id: 세션 ID

        Returns:
            TerminalSession | None: 조회된 세션 (없으면 None)
        """
        return await session_manager.get_session_by_id(db, session_id)

    async def get_session(
        self, db: AsyncSession, session_id: str, check_expiry: bool = True
    ) -> TerminalSession:
        """
        세션 조회 (만료 체크 포함)

        Args:
            db: 데이터베이스 세션
            session_id: 세션 ID
            check_expiry: 만료 여부 확인 (기본값: True)

        Returns:
            TerminalSession: 조회된 세션

        Raises:
            AppException:
                - 404: 세션을 찾을 수 없음
                - 410: 세션이 만료됨 (check_expiry=True인 경우)
        """
        return await session_manager.get_session(db, session_id, check_expiry)

    async def terminate_session(
        self, db: AsyncSession, session_id: str
    ) -> TerminalSession:
        """
        세션 종료 (DB 업데이트 + 컨테이너 삭제)

        Args:
            db: 데이터베이스 세션
            session_id: 세션 ID

        Returns:
            TerminalSession: 종료된 세션

        Raises:
            AppException: 세션을 찾을 수 없는 경우 (404)

        Note:
            멱등성 보장: 이미 종료된 세션도 성공 반환
        """
        return await session_manager.terminate_session(
            db, session_id, self.docker_service
        )

    async def execute_command(
        self, db: AsyncSession, session_id: str, command: str
    ) -> CommandResponse:
        """
        터미널 명령어 실행 (보안 검증 + Docker exec)

        Args:
            db: 데이터베이스 세션
            session_id: 세션 ID
            command: 실행할 명령어

        Returns:
            CommandResponse: 명령어 실행 결과

        Raises:
            AppException:
                - 400: 위험한 명령어
                - 404: 세션을 찾을 수 없음
                - 410: 세션이 만료됨
                - 408: 명령어 실행 타임아웃
                - 500: 실행 실패
        """
        # 세션 조회 및 검증
        try:
            session = await self.get_session(db, session_id, check_expiry=True)
        except AppException as e:
            # get_session이 발생시킨 에러를 그대로 전파
            # 410 (만료/종료) → 403으로 변경
            if e.status_code == 410:
                if "만료" in str(e.detail):
                    raise AppException(
                        status_code=403,
                        detail="세션이 만료되었습니다",
                    )
                else:
                    raise AppException(
                        status_code=403,
                        detail="세션이 종료되었습니다",
                    )
            raise

        # 명령어 실행
        return await command_executor.execute_command(
            db, session, command, self.docker_service
        )

    async def get_active_sessions(self, db: AsyncSession) -> list[TerminalSession]:
        """
        활성 세션 목록 조회

        Args:
            db: 데이터베이스 세션

        Returns:
            list[TerminalSession]: 활성 세션 목록
        """
        return await session_lifecycle.get_active_sessions(db)

    def is_session_expired(self, session: TerminalSession) -> bool:
        """
        세션 만료 여부 확인

        Args:
            session: 확인할 세션

        Returns:
            bool: 만료되었으면 True, 아니면 False
        """
        return session_lifecycle.is_session_expired(session)

    def get_session_remaining_time(self, session: TerminalSession) -> int:
        """
        세션 남은 시간 계산 (초)

        Args:
            session: 확인할 세션

        Returns:
            int: 남은 시간 (초, 만료되었으면 0)
        """
        return session_lifecycle.get_session_remaining_time(session)

    async def get_sessions_count_by_status(
        self, db: AsyncSession
    ) -> dict[TerminalStatus, int]:
        """
        상태별 세션 개수 조회

        Args:
            db: 데이터베이스 세션

        Returns:
            dict[TerminalStatus, int]: 상태별 개수
        """
        return await session_lifecycle.get_sessions_count_by_status(db)

    async def cleanup_expired_sessions(self, db: AsyncSession) -> int:
        """
        만료된 세션 자동 정리 (백그라운드 작업)

        Args:
            db: 데이터베이스 세션

        Returns:
            int: 정리된 세션 수
        """
        return await session_lifecycle.cleanup_expired_sessions(
            db, self.docker_service
        )
