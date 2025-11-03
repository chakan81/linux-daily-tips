"""
Docker 컨테이너 명령어 실행

컨테이너 내부에서 안전하게 명령어를 실행하고 결과를 반환합니다.
"""

import asyncio
import logging
import time
from typing import Any

import docker
from docker.errors import NotFound

from app.config.docker_config import (
    COMMAND_TIMEOUT,
    CONTAINER_WORKDIR,
    MAX_OUTPUT_SIZE,
)
from app.core.exceptions import AppException
from app.services.docker.security_validator import SecurityValidator

logger = logging.getLogger(__name__)


class CommandExecutor:
    """
    컨테이너 명령어 실행기

    보안 검증 후 Docker exec를 통해 명령어를 실행합니다.

    Attributes:
        client: Docker SDK 클라이언트
        validator: 보안 검증기
    """

    def __init__(self, client: docker.DockerClient) -> None:
        """
        CommandExecutor 초기화

        Args:
            client: Docker SDK 클라이언트
        """
        self.client = client
        self.validator = SecurityValidator()

    async def execute_command(
        self, container_id: str, command: str, timeout: int | None = None
    ) -> dict[str, Any]:
        """
        컨테이너에서 명령어 실행 (비동기)

        보안 검증 후 Docker exec를 통해 명령어를 실행합니다.

        Args:
            container_id: 컨테이너 ID
            command: 실행할 명령어
            timeout: 명령어 실행 타임아웃 (초, None이면 5초 기본값)

        Returns:
            dict[str, Any]: 실행 결과
                - exit_code: 종료 코드
                - output: 표준 출력 (stdout)
                - error: 표준 에러 (stderr)

        Raises:
            AppException:
                - 400: 위험한 명령어 또는 명령어 길이 초과
                - 403: 위험한 명령어
                - 404: 컨테이너를 찾을 수 없음
                - 408: 명령어 실행 타임아웃
                - 500: 실행 실패

        Example:
            ```python
            executor = CommandExecutor(client)
            result = await executor.execute_command("abc123", "ls -la")
            print(f"Output: {result['output']}, exit_code: {result['exit_code']}")
            ```
        """
        # 1. 명령어 길이 제한
        if len(command) > 1000:
            raise AppException(
                status_code=400,
                detail="명령어가 너무 깁니다 (최대 1000자)",
            )

        # 2. 보안 검증
        if not self.validator.is_command_safe(command):
            raise AppException(
                status_code=403,
                detail="위험한 명령어는 실행할 수 없습니다",
            )

        try:
            container = self.client.containers.get(container_id)

            logger.info(f"명령어 실행 시작: [{container_id}] {command}")
            start_time = time.time()

            # 비동기 실행 (타임아웃 적용)
            loop = asyncio.get_event_loop()
            exec_timeout = timeout if timeout is not None else COMMAND_TIMEOUT

            try:
                exec_result = await asyncio.wait_for(
                    loop.run_in_executor(
                        None,
                        lambda: container.exec_run(
                            cmd=["bash", "-c", command],
                            stdout=True,
                            stderr=True,
                            demux=True,  # stdout과 stderr 분리
                            workdir=CONTAINER_WORKDIR,
                        ),
                    ),
                    timeout=exec_timeout,
                )
            except asyncio.TimeoutError:
                logger.error(f"명령어 실행 타임아웃: {command}")
                raise AppException(
                    status_code=408,
                    detail=f"명령어 실행 시간이 {exec_timeout}초를 초과했습니다",
                )

            elapsed = time.time() - start_time

            # 결과 파싱 (mock과 실제 Docker SDK 모두 지원)
            if isinstance(exec_result, tuple):
                # 테스트 mock: (exit_code, output) 튜플
                exit_code = exec_result[0]
                output_data = exec_result[1] if len(exec_result) > 1 else b""

                # demux 처리: output이 튜플이면 (stdout, stderr), 아니면 단일 바이트열
                if isinstance(output_data, tuple):
                    stdout_bytes, stderr_bytes = output_data
                else:
                    stdout_bytes, stderr_bytes = output_data, b""
            else:
                # 실제 Docker SDK: ExecResult 객체
                exit_code = exec_result.exit_code
                # demux=True일 때 output은 (stdout, stderr) 튜플
                if exec_result.output:
                    stdout_bytes, stderr_bytes = exec_result.output
                else:
                    stdout_bytes, stderr_bytes = b"", b""

            # 바이트를 문자열로 변환
            stdout = stdout_bytes.decode("utf-8", errors="replace") if stdout_bytes else ""
            stderr = stderr_bytes.decode("utf-8", errors="replace") if stderr_bytes else ""

            # 출력 크기 제한
            stdout = self._truncate_output(stdout)
            stderr = self._truncate_output(stderr)

            logger.info(
                f"명령어 실행 완료: [{container_id}] exit_code={exit_code}, "
                f"stdout_len={len(stdout)}, stderr_len={len(stderr)}, "
                f"소요 시간={elapsed:.2f}초"
            )

            return {"exit_code": exit_code, "output": stdout, "error": stderr}

        except NotFound:
            logger.error(f"컨테이너를 찾을 수 없음: {container_id}")
            raise AppException(
                status_code=404,
                detail="터미널 세션이 만료되었습니다. 새로 시작해주세요.",
            )
        except AppException:
            raise
        except Exception as e:
            logger.error(f"명령어 실행 실패: {str(e)}", exc_info=True)
            raise AppException(
                status_code=500,
                detail="명령어 실행에 실패했습니다. 다시 시도해주세요.",
            )

    def _truncate_output(self, output: str) -> str:
        """
        출력 크기 제한 (10KB)

        메모리 소진 공격을 방지합니다.

        Args:
            output: 원본 출력

        Returns:
            str: 잘린 출력 (필요 시)
        """
        if len(output) > MAX_OUTPUT_SIZE:
            truncated = output[:MAX_OUTPUT_SIZE]
            return truncated + "\n... (출력이 잘렸습니다. 최대 10KB)"
        return output
