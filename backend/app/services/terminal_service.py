"""
터미널 세션 비즈니스 로직 서비스

터미널 에뮬레이터 세션의 전체 생명주기를 관리합니다.
- 세션 생성/조회/종료
- Docker 컨테이너 관리
- 명령어 실행 (보안 검증 포함)
- 만료된 세션 자동 정리
"""

import logging
from datetime import datetime, timedelta, timezone
from ipaddress import IPv4Address, IPv6Address

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.models.terminal import TerminalSession, TerminalStatus
from app.schemas.terminal import CommandResponse, TerminalSessionCreate
from app.services.docker_service import DockerService

# 로거 인스턴스
logger = logging.getLogger(__name__)

# 세션 설정
SESSION_EXPIRY_MINUTES = 30  # 30분 후 자동 만료


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

        1. Docker 컨테이너 생성
        2. 데이터베이스에 세션 저장

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

        Example:
            ```python
            service = TerminalService()
            session = await service.create_session(
                db,
                TerminalSessionCreate(tip_id="tip_01JCAW..."),
                ip_address=IPv4Address("192.168.1.1"),
                user_agent="Mozilla/5.0..."
            )
            ```
        """
        try:
            # tip_id가 있으면 존재 여부 확인
            if session_data.tip_id:
                from app.models.tip import Tip

                stmt = select(Tip).where(Tip.id == session_data.tip_id)
                result = await db.execute(stmt)
                tip = result.scalar_one_or_none()
                if not tip:
                    raise AppException(status_code=404, detail="Tip not found")
                if not tip.is_active:
                    raise AppException(
                        status_code=400, detail="Tip is not active"
                    )

            # 세션 모델 생성 (ID 자동 생성)
            session = TerminalSession(
                tip_id=session_data.tip_id,
                ip_address=ip_address,
                user_agent=user_agent,
                session_data=session_data.session_data,
                status=TerminalStatus.ACTIVE,
                expires_at=datetime.now(timezone.utc)
                + timedelta(minutes=SESSION_EXPIRY_MINUTES),
            )

            # 데이터베이스에 저장 (ID 생성)
            db.add(session)
            await db.flush()
            await db.refresh(session)

            logger.info(f"세션 생성 시작: {session.id}")

            # Docker 컨테이너 생성
            try:
                terminal_setup = None
                if session_data.tip_id and session.tip:
                    terminal_setup = session.tip.terminal_setup

                container_id = await self.docker_service.create_container(
                    session.id, terminal_setup
                )

                # 컨테이너 ID 업데이트
                session.container_id = container_id
                await db.flush()
                await db.refresh(session)

                logger.info(
                    f"세션 생성 완료: {session.id}, 컨테이너: {container_id}"
                )

                return session

            except AppException as e:
                # 컨테이너 생성 실패 시 세션 삭제
                await db.delete(session)
                await db.flush()
                logger.error(f"컨테이너 생성 실패로 세션 삭제: {session.id}")
                raise e

        except AppException:
            raise
        except Exception as e:
            logger.error(
                f"세션 생성 중 오류: {str(e)}",
                exc_info=True,
            )
            raise AppException(
                status_code=500,
                detail="세션 생성에 실패했습니다. 다시 시도해주세요.",
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

        Example:
            ```python
            service = TerminalService()
            session = await service.get_session_by_id(db, "session_01JCAW...")
            if session:
                print(f"Session status: {session.status}")
            ```
        """
        try:
            stmt = select(TerminalSession).where(TerminalSession.id == session_id)
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"세션 조회 중 오류: {str(e)}", exc_info=True)
            return None

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

        Example:
            ```python
            service = TerminalService()
            session = await service.get_session(db, "session_01JCAW...")
            ```
        """
        try:
            stmt = select(TerminalSession).where(TerminalSession.id == session_id)
            result = await db.execute(stmt)
            session = result.scalar_one_or_none()

            if not session:
                logger.warning(f"세션을 찾을 수 없음: {session_id}")
                raise AppException(status_code=404, detail="Session not found")

            # 만료 체크
            if check_expiry and session.is_expired:
                logger.warning(f"만료된 세션 접근 시도: {session_id}")
                raise AppException(
                    status_code=410,
                    detail="세션이 만료되었습니다. 새로 시작해주세요.",
                )

            # 비활성 세션 체크
            if session.status != TerminalStatus.ACTIVE:
                logger.warning(f"비활성 세션 접근 시도: {session_id}, 상태: {session.status}")
                raise AppException(
                    status_code=410,
                    detail="세션이 종료되었습니다. 새로 시작해주세요.",
                )

            return session

        except AppException:
            raise
        except Exception as e:
            logger.error(
                f"세션 조회 중 오류: {str(e)}",
                exc_info=True,
            )
            raise

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

        Example:
            ```python
            service = TerminalService()
            session = await service.terminate_session(db, "session_01JCAW...")
            ```
        """
        try:
            # 세션 조회 (만료 체크 비활성화)
            session = await self.get_session(db, session_id, check_expiry=False)

            # 이미 종료된 세션이면 멱등성 보장
            if session.status in [TerminalStatus.TERMINATED, TerminalStatus.EXPIRED]:
                logger.info(f"이미 종료된 세션: {session_id}, 상태: {session.status}")
                return session

            # 세션 상태 업데이트
            session.status = TerminalStatus.TERMINATED
            session.terminated_at = datetime.now(timezone.utc)
            await db.flush()

            # 컨테이너 삭제 (비동기, 에러 무시)
            if session.container_id:
                try:
                    await self.docker_service.remove_container(
                        session.container_id, force=True
                    )
                except Exception as e:
                    logger.warning(
                        f"컨테이너 삭제 실패 (세션은 종료됨): {session.container_id}, {str(e)}"
                    )

            logger.info(f"세션 종료 완료: {session_id}")
            return session

        except AppException:
            raise
        except Exception as e:
            logger.error(
                f"세션 종료 중 오류: {str(e)}",
                exc_info=True,
            )
            raise

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

        Example:
            ```python
            service = TerminalService()
            result = await service.execute_command(db, "session_01JCAW...", "ls -la")
            print(f"출력: {result.stdout}")
            ```
        """
        import time

        try:
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

            if not session.container_id:
                raise AppException(
                    status_code=500,
                    detail="컨테이너가 연결되지 않았습니다",
                )

            # 명령어 실행
            start_time = time.time()
            result = await self.docker_service.execute_command(
                session.container_id, command
            )
            execution_time = time.time() - start_time

            logger.info(
                f"명령어 실행 완료: [{session_id}] {command}, "
                f"exit_code={result['exit_code']}, 소요 시간={execution_time:.2f}초"
            )

            return CommandResponse(
                stdout=result["output"],
                stderr=result["error"],
                exit_code=result["exit_code"],
                execution_time=execution_time,
            )

        except AppException:
            raise
        except Exception as e:
            logger.error(
                f"명령어 실행 중 오류: {str(e)}",
                exc_info=True,
            )
            raise

    async def get_active_sessions(self, db: AsyncSession) -> list[TerminalSession]:
        """
        활성 세션 목록 조회

        Args:
            db: 데이터베이스 세션

        Returns:
            list[TerminalSession]: 활성 세션 목록

        Example:
            ```python
            service = TerminalService()
            sessions = await service.get_active_sessions(db)
            print(f"Active sessions: {len(sessions)}")
            ```
        """
        try:
            stmt = select(TerminalSession).where(
                TerminalSession.status == TerminalStatus.ACTIVE
            )
            result = await db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"활성 세션 조회 중 오류: {str(e)}", exc_info=True)
            return []

    def is_session_expired(self, session: TerminalSession) -> bool:
        """
        세션 만료 여부 확인

        Args:
            session: 확인할 세션

        Returns:
            bool: 만료되었으면 True, 아니면 False

        Example:
            ```python
            service = TerminalService()
            if service.is_session_expired(session):
                print("Session has expired")
            ```
        """
        return session.is_expired

    def get_session_remaining_time(self, session: TerminalSession) -> int:
        """
        세션 남은 시간 계산 (초)

        Args:
            session: 확인할 세션

        Returns:
            int: 남은 시간 (초, 만료되었으면 0)

        Example:
            ```python
            service = TerminalService()
            remaining = service.get_session_remaining_time(session)
            print(f"Remaining time: {remaining} seconds")
            ```
        """
        now = datetime.now(timezone.utc)
        if session.expires_at <= now:
            return 0
        delta = session.expires_at - now
        return int(delta.total_seconds())

    async def get_sessions_count_by_status(
        self, db: AsyncSession
    ) -> dict[TerminalStatus, int]:
        """
        상태별 세션 개수 조회

        Args:
            db: 데이터베이스 세션

        Returns:
            dict[TerminalStatus, int]: 상태별 개수

        Example:
            ```python
            service = TerminalService()
            counts = await service.get_sessions_count_by_status(db)
            print(f"Active: {counts[TerminalStatus.ACTIVE]}")
            ```
        """
        try:
            from sqlalchemy import func

            stmt = select(
                TerminalSession.status, func.count(TerminalSession.id)
            ).group_by(TerminalSession.status)
            result = await db.execute(stmt)
            rows = result.all()

            # 모든 상태를 0으로 초기화
            counts = {status: 0 for status in TerminalStatus}

            # 실제 개수로 업데이트
            for status, count in rows:
                counts[status] = count

            return counts
        except Exception as e:
            logger.error(f"세션 개수 조회 중 오류: {str(e)}", exc_info=True)
            return {status: 0 for status in TerminalStatus}

    async def cleanup_expired_sessions(self, db: AsyncSession) -> int:
        """
        만료된 세션 자동 정리 (백그라운드 작업)

        expires_at이 지난 활성 세션을 찾아 종료합니다.

        Args:
            db: 데이터베이스 세션

        Returns:
            int: 정리된 세션 수

        Example:
            ```python
            service = TerminalService()
            count = await service.cleanup_expired_sessions(db)
            print(f"{count}개 세션 정리 완료")
            ```
        """
        try:
            # 만료된 활성 세션 조회
            stmt = select(TerminalSession).where(
                and_(
                    TerminalSession.status == TerminalStatus.ACTIVE,
                    TerminalSession.expires_at < datetime.now(timezone.utc),
                )
            )
            result = await db.execute(stmt)
            expired_sessions = list(result.scalars().all())

            count = 0
            for session in expired_sessions:
                try:
                    # 세션 상태 업데이트
                    session.status = TerminalStatus.EXPIRED
                    session.terminated_at = datetime.now(timezone.utc)

                    # 컨테이너 삭제
                    if session.container_id:
                        await self.docker_service.remove_container(
                            session.container_id, force=True
                        )

                    count += 1
                    logger.info(f"만료된 세션 정리: {session.id}")

                except Exception as e:
                    logger.warning(
                        f"세션 정리 실패 (계속 진행): {session.id}, {str(e)}"
                    )

            # DB 변경사항 커밋
            await db.flush()

            if count > 0:
                logger.info(f"만료된 세션 정리 완료: {count}개")

            return count

        except Exception as e:
            logger.error(
                f"세션 정리 중 오류: {str(e)}",
                exc_info=True,
            )
            return 0
