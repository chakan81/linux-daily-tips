"""
터미널 세션 생명주기 관리 모듈

세션 만료 체크, 자동 정리, 통계 조회를 담당합니다.
"""

import logging
from datetime import datetime, timezone

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.terminal import TerminalSession, TerminalStatus
from app.services.docker_service import DockerService

# 로거 인스턴스
logger = logging.getLogger(__name__)


def is_session_expired(session: TerminalSession) -> bool:
    """
    세션 만료 여부 확인

    Args:
        session: 확인할 세션

    Returns:
        bool: 만료되었으면 True, 아니면 False

    Example:
        ```python
        if is_session_expired(session):
            print("Session has expired")
        ```
    """
    return session.is_expired


def get_session_remaining_time(session: TerminalSession) -> int:
    """
    세션 남은 시간 계산 (초)

    Args:
        session: 확인할 세션

    Returns:
        int: 남은 시간 (초, 만료되었으면 0)

    Example:
        ```python
        remaining = get_session_remaining_time(session)
        print(f"Remaining time: {remaining} seconds")
        ```
    """
    now = datetime.now(timezone.utc)
    if session.expires_at <= now:
        return 0
    delta = session.expires_at - now
    return int(delta.total_seconds())


async def get_active_sessions(db: AsyncSession) -> list[TerminalSession]:
    """
    활성 세션 목록 조회

    Args:
        db: 데이터베이스 세션

    Returns:
        list[TerminalSession]: 활성 세션 목록

    Example:
        ```python
        sessions = await get_active_sessions(db)
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


async def get_sessions_count_by_status(
    db: AsyncSession,
) -> dict[TerminalStatus, int]:
    """
    상태별 세션 개수 조회

    Args:
        db: 데이터베이스 세션

    Returns:
        dict[TerminalStatus, int]: 상태별 개수

    Example:
        ```python
        counts = await get_sessions_count_by_status(db)
        print(f"Active: {counts[TerminalStatus.ACTIVE]}")
        ```
    """
    try:
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


async def cleanup_expired_sessions(
    db: AsyncSession,
    docker_service: DockerService,
) -> int:
    """
    만료된 세션 자동 정리 (백그라운드 작업)

    expires_at이 지난 활성 세션을 찾아 종료합니다.

    Args:
        db: 데이터베이스 세션
        docker_service: DockerService 인스턴스

    Returns:
        int: 정리된 세션 수

    Example:
        ```python
        count = await cleanup_expired_sessions(db, docker_service)
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
                    await docker_service.remove_container(
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
