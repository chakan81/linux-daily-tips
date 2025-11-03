"""
터미널 세션 관리 모듈

터미널 세션의 생성, 조회, 종료를 담당합니다.
"""

import logging
from datetime import datetime, timedelta, timezone
from ipaddress import IPv4Address, IPv6Address

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.core.exceptions import AppException
from app.models.terminal import TerminalSession, TerminalStatus
from app.schemas.terminal import TerminalSessionCreate
from app.services.docker_service import DockerService

# 로거 인스턴스
logger = logging.getLogger(__name__)

# 세션 설정 (환경 변수에서 로드)
settings = get_settings()
SESSION_EXPIRY_MINUTES = settings.session_expiry_minutes


async def create_session(
    db: AsyncSession,
    session_data: TerminalSessionCreate,
    docker_service: DockerService,
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
        docker_service: DockerService 인스턴스
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
        session = await create_session(
            db,
            TerminalSessionCreate(tip_id="tip_01JCAW..."),
            docker_service,
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

            container_id = await docker_service.create_container(
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
    db: AsyncSession, session_id: str
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
        session = await get_session_by_id(db, "session_01JCAW...")
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
    db: AsyncSession, session_id: str, check_expiry: bool = True
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
        session = await get_session(db, "session_01JCAW...")
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
    db: AsyncSession,
    session_id: str,
    docker_service: DockerService,
) -> TerminalSession:
    """
    세션 종료 (DB 업데이트 + 컨테이너 삭제)

    Args:
        db: 데이터베이스 세션
        session_id: 세션 ID
        docker_service: DockerService 인스턴스

    Returns:
        TerminalSession: 종료된 세션

    Raises:
        AppException: 세션을 찾을 수 없는 경우 (404)

    Note:
        멱등성 보장: 이미 종료된 세션도 성공 반환

    Example:
        ```python
        session = await terminate_session(db, "session_01JCAW...", docker_service)
        ```
    """
    try:
        # 세션 조회 (만료 체크 비활성화)
        session = await get_session(db, session_id, check_expiry=False)

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
                await docker_service.remove_container(
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
