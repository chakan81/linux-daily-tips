"""
터미널 명령어 실행 모듈

Docker 컨테이너 내에서 명령어를 실행하고 결과를 반환합니다.
"""

import logging
import time

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.models.terminal import TerminalSession
from app.schemas.terminal import CommandResponse
from app.services.docker_service import DockerService

# 로거 인스턴스
logger = logging.getLogger(__name__)


async def execute_command(
    db: AsyncSession,
    session: TerminalSession,
    command: str,
    docker_service: DockerService,
) -> CommandResponse:
    """
    터미널 명령어 실행 (보안 검증 + Docker exec)

    Args:
        db: 데이터베이스 세션
        session: 터미널 세션
        command: 실행할 명령어
        docker_service: DockerService 인스턴스

    Returns:
        CommandResponse: 명령어 실행 결과

    Raises:
        AppException:
            - 400: 위험한 명령어
            - 500: 컨테이너가 연결되지 않음
            - 408: 명령어 실행 타임아웃
            - 500: 실행 실패

    Example:
        ```python
        result = await execute_command(db, session, "ls -la", docker_service)
        print(f"출력: {result.stdout}")
        ```
    """
    try:
        if not session.container_id:
            raise AppException(
                status_code=500,
                detail="컨테이너가 연결되지 않았습니다",
            )

        # 명령어 실행
        start_time = time.time()
        result = await docker_service.execute_command(
            session.container_id, command
        )
        execution_time = time.time() - start_time

        logger.info(
            f"명령어 실행 완료: [{session.id}] {command}, "
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
