"""
Docker 컨테이너 관리 서비스

터미널 에뮬레이터를 위한 Docker 컨테이너 생명주기를 관리합니다.
- 컨테이너 생성/시작/중지/삭제
- 명령어 실행 (보안 검증 포함)
- 리소스 제한 및 네트워크 격리
"""

import asyncio
import logging
import time
from typing import Any

import docker
from docker.errors import APIError, DockerException, NotFound
from docker.models.containers import Container

from app.core.exceptions import AppException

# 로거 인스턴스
logger = logging.getLogger(__name__)

# 보안 설정
DANGEROUS_COMMANDS = [
    # 파일시스템 파괴
    "rm -rf /",
    "rm -rf /*",
    "mkfs",
    "dd",
    # 시스템 설정 변경
    "iptables",
    "ufw",
    "systemctl",
    "service",
    "reboot",
    "shutdown",
    "poweroff",
    # 네트워크 공격
    "nc",
    "netcat",
    "nmap",
    "curl",
    "wget",
    "ping",
    # 패키지 관리 (리소스 남용)
    "apt",
    "apt-get",
    "yum",
    "dnf",
    "pacman",
    # 사용자 관리
    "useradd",
    "userdel",
    "passwd",
    "sudo",
    "su",
    # 프로세스 조작
    "kill -9 1",  # init 프로세스 종료
    "killall",
    # 무한 루프 (포크 폭탄)
    ":(){ :|:& };:",
    "fork",
]

# 컨테이너 설정
CONTAINER_IMAGE = "linux-daily-tips-terminal:latest"
CONTAINER_MEMORY_LIMIT = "256m"
CONTAINER_CPU_QUOTA = 50000  # 50% of 100,000 (0.5 core)
CONTAINER_PIDS_LIMIT = 100
COMMAND_TIMEOUT = 5  # 초
MAX_OUTPUT_SIZE = 10 * 1024  # 10KB


class DockerService:
    """
    Docker 컨테이너 관리 서비스

    안전한 샌드박스 환경에서 터미널 명령어를 실행합니다.

    Attributes:
        client: Docker SDK 클라이언트
    """

    def __init__(self, client: docker.DockerClient | None = None) -> None:
        """
        DockerService 초기화

        Args:
            client: Docker 클라이언트 (테스트용 mock 주입 가능, None이면 자동 생성)

        Raises:
            AppException: Docker 데몬에 연결할 수 없는 경우 (500)
        """
        if client is not None:
            # 테스트용 mock 클라이언트 주입
            self.client = client
            logger.info("Docker 클라이언트 주입됨 (테스트 모드)")
        else:
            # 실제 Docker 클라이언트 생성
            try:
                self.client = docker.from_env()
                # Docker 데몬 연결 확인
                self.client.ping()
                logger.info("Docker 클라이언트 초기화 성공")
            except DockerException as e:
                logger.error(f"Docker 데몬 연결 실패: {str(e)}", exc_info=True)
                raise AppException(
                    status_code=500,
                detail="Docker 서비스에 연결할 수 없습니다. 관리자에게 문의하세요.",
            )

    async def create_container(
        self,
        session_id: str | None = None,
        terminal_setup: dict[str, Any] | None = None,
        image: str | None = None,
    ) -> str:
        """
        Docker 컨테이너 생성 및 시작 (비동기)

        보안 설정이 적용된 샌드박스 컨테이너를 생성합니다.

        Args:
            session_id: 세션 ID (컨테이너 이름으로 사용, None이면 랜덤 ID 생성)
            terminal_setup: 사전 구성할 파일/디렉토리 정보 (선택적)
            image: Docker 이미지 이름 (None이면 기본 이미지 사용)

        Returns:
            str: 생성된 컨테이너 ID

        Raises:
            AppException: 컨테이너 생성 실패 시 (500)

        Example:
            ```python
            service = DockerService()
            container_id = await service.create_container("session_01JCAW...")
            ```
        """
        try:
            # 기본값 설정
            if image is None:
                image = CONTAINER_IMAGE

            container_name = f"terminal-{session_id}" if session_id else None

            logger.info(f"컨테이너 생성 시작: {session_id or 'anonymous'}")
            start_time = time.time()

            # Docker SDK는 동기 함수이므로 비동기 실행
            loop = asyncio.get_event_loop()

            # 컨테이너 설정
            container_config = {
                "image": image,
                "detach": True,
                "network_mode": "none",  # 보안 설정: 네트워크 격리
                "read_only": False,  # 샌드박스 학습 환경이므로 쓰기 허용
                "tmpfs": {
                    "/tmp": "size=50m",  # 임시 파일 50MB 제한
                },
                "mem_limit": CONTAINER_MEMORY_LIMIT,
                "memswap_limit": CONTAINER_MEMORY_LIMIT,  # 스왑 비활성화
                "cpu_quota": CONTAINER_CPU_QUOTA,
                "pids_limit": CONTAINER_PIDS_LIMIT,
                "working_dir": "/home/linuxuser",  # 이미지의 기본 작업 디렉토리 사용
                "command": ["/bin/bash", "-c", "tail -f /dev/null"],
                "labels": {"app": "linux-daily-tips"},
            }

            # 컨테이너 이름 추가 (세션 ID가 있는 경우)
            if container_name:
                container_config["name"] = container_name
                container_config["labels"]["session_id"] = session_id

            container = await loop.run_in_executor(
                None, lambda: self.client.containers.run(**container_config)
            )

            elapsed = time.time() - start_time
            logger.info(
                f"컨테이너 생성 완료: {container.short_id} (소요 시간: {elapsed:.2f}초)"
            )

            # TODO: terminal_setup이 있으면 파일/디렉토리 사전 구성
            # if terminal_setup:
            #     await self._setup_files(container, terminal_setup)

            return container.id  # 전체 ID 반환 (short_id가 아닌)

        except docker.errors.ImageNotFound as e:
            logger.error(f"이미지를 찾을 수 없음: {str(e)}", exc_info=True)
            raise AppException(
                status_code=500,
                detail=f"이미지를 찾을 수 없습니다: {image}",
            )
        except APIError as e:
            logger.error(f"컨테이너 생성 실패: {str(e)}", exc_info=True)
            raise AppException(
                status_code=500,
                detail=f"컨테이너 생성에 실패했습니다: {str(e)}",
            )
        except Exception as e:
            logger.error(f"컨테이너 생성 중 예상치 못한 오류: {str(e)}", exc_info=True)
            raise AppException(
                status_code=500,
                detail="컨테이너 생성에 실패했습니다. 다시 시도해주세요.",
            )

    async def start_container(self, container_id: str) -> bool:
        """
        컨테이너 시작 (비동기)

        Args:
            container_id: 컨테이너 ID

        Returns:
            bool: 성공 여부

        Raises:
            AppException: 컨테이너를 찾을 수 없거나 시작 실패 시 (404, 500)
        """
        try:
            container = self.client.containers.get(container_id)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, container.start)
            logger.info(f"컨테이너 시작 완료: {container_id}")
            return True

        except NotFound:
            logger.error(f"컨테이너를 찾을 수 없음: {container_id}")
            raise AppException(status_code=404, detail="Container not found")
        except Exception as e:
            logger.error(f"컨테이너 시작 실패: {str(e)}", exc_info=True)
            raise AppException(status_code=500, detail="Failed to start container")

    async def stop_container(
        self, container_id: str, timeout: int | None = None
    ) -> bool:
        """
        컨테이너 중지 (비동기)

        Args:
            container_id: 컨테이너 ID
            timeout: 중지 타임아웃 (초, None이면 5초 기본값)

        Returns:
            bool: 성공 여부

        Raises:
            AppException: 컨테이너를 찾을 수 없거나 중지 실패 시 (404, 500)
        """
        try:
            container = self.client.containers.get(container_id)
            loop = asyncio.get_event_loop()
            stop_timeout = timeout if timeout is not None else 5
            await loop.run_in_executor(None, lambda: container.stop(timeout=stop_timeout))
            logger.info(f"컨테이너 중지 완료: {container_id}")
            return True

        except NotFound:
            logger.error(f"컨테이너를 찾을 수 없음: {container_id}")
            raise AppException(status_code=404, detail="Container not found")
        except Exception as e:
            logger.error(f"컨테이너 중지 실패: {str(e)}", exc_info=True)
            raise AppException(status_code=500, detail="Failed to stop container")

    async def remove_container(self, container_id: str, force: bool = True) -> bool:
        """
        컨테이너 삭제 (비동기)

        Args:
            container_id: 컨테이너 ID
            force: 강제 삭제 여부 (실행 중인 컨테이너도 삭제)

        Returns:
            bool: 성공 여부 (컨테이너가 없어도 성공)

        Note:
            멱등성 보장: 이미 삭제된 컨테이너도 True 반환
        """
        try:
            container = self.client.containers.get(container_id)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: container.remove(force=force))
            logger.info(f"컨테이너 삭제 완료: {container_id}")
            return True

        except NotFound:
            logger.info(f"컨테이너가 이미 삭제됨: {container_id}")
            return True  # 멱등성 보장
        except Exception as e:
            logger.error(f"컨테이너 삭제 실패: {str(e)}", exc_info=True)
            return False

    def is_command_safe(self, command: str) -> bool:
        """
        명령어 안전성 검증 (블랙리스트 기반)

        위험한 명령어를 차단하여 시스템을 보호합니다.

        Args:
            command: 검증할 명령어

        Returns:
            bool: 안전하면 True, 위험하면 False

        Example:
            ```python
            service = DockerService()
            if not service.is_command_safe("rm -rf /"):
                raise ValueError("위험한 명령어입니다")
            ```
        """
        command_lower = command.lower().strip()

        # 블랙리스트 검증
        for dangerous in DANGEROUS_COMMANDS:
            if dangerous in command_lower:
                logger.warning(f"위험한 명령어 차단됨: {command}")
                return False

        # 파이프를 통한 우회 방지
        if "|" in command:
            for dangerous in DANGEROUS_COMMANDS:
                if dangerous in command_lower:
                    logger.warning(f"파이프 우회 시도 차단됨: {command}")
                    return False

        return True

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
            service = DockerService()
            result = await service.execute_command("abc123", "ls -la")
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
        if not self.is_command_safe(command):
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
                            workdir="/home/linuxuser",  # 명시적 working directory 설정
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

            # 결과 파싱
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

    async def get_container_status(self, container_id: str) -> str:
        """
        컨테이너 상태 조회

        Args:
            container_id: 컨테이너 ID

        Returns:
            str: 컨테이너 상태 (running, exited, paused, etc.)

        Raises:
            AppException: 컨테이너를 찾을 수 없는 경우 (404)
        """
        try:
            container = self.client.containers.get(container_id)
            return container.status
        except NotFound:
            logger.error(f"컨테이너를 찾을 수 없음: {container_id}")
            raise AppException(status_code=404, detail="Container not found")
        except Exception as e:
            logger.error(f"컨테이너 상태 조회 실패: {str(e)}", exc_info=True)
            raise AppException(status_code=500, detail="Failed to get container status")

    async def get_container_stats(self, container_id: str) -> dict[str, Any]:
        """
        컨테이너 리소스 사용량 조회

        Args:
            container_id: 컨테이너 ID

        Returns:
            dict[str, Any]: 리소스 사용량
                - memory_usage: 메모리 사용량 (바이트)
                - memory_limit: 메모리 제한 (바이트)
                - cpu_usage: CPU 사용량

        Raises:
            AppException: 컨테이너를 찾을 수 없는 경우 (404)
        """
        try:
            container = self.client.containers.get(container_id)
            loop = asyncio.get_event_loop()
            stats = await loop.run_in_executor(
                None, lambda: container.stats(stream=False)
            )

            # 메모리 사용량 추출
            memory_stats = stats.get("memory_stats", {})
            memory_usage = memory_stats.get("usage", 0)
            memory_limit = memory_stats.get("limit", 0)

            # CPU 사용량 추출
            cpu_stats = stats.get("cpu_stats", {})
            cpu_usage = cpu_stats.get("cpu_usage", {}).get("total_usage", 0)

            return {
                "memory_usage": memory_usage,
                "memory_limit": memory_limit,
                "cpu_usage": cpu_usage,
            }
        except NotFound:
            logger.error(f"컨테이너를 찾을 수 없음: {container_id}")
            raise AppException(status_code=404, detail="Container not found")
        except Exception as e:
            logger.error(f"컨테이너 통계 조회 실패: {str(e)}", exc_info=True)
            raise AppException(status_code=500, detail="Failed to get container stats")

    async def list_containers(
        self, filters: dict[str, str] | None = None
    ) -> list[dict[str, Any]]:
        """
        컨테이너 목록 조회

        Args:
            filters: 필터 조건 (예: {"status": "running"})

        Returns:
            list[dict[str, Any]]: 컨테이너 목록
                - id: 컨테이너 ID
                - status: 상태
                - name: 이름

        Example:
            ```python
            service = DockerService()
            containers = await service.list_containers(filters={"status": "running"})
            ```
        """
        try:
            loop = asyncio.get_event_loop()
            containers = await loop.run_in_executor(
                None, lambda: self.client.containers.list(all=True, filters=filters)
            )

            result = []
            for container in containers:
                result.append(
                    {
                        "id": container.id,
                        "status": container.status,
                        "name": container.name,
                    }
                )

            return result
        except Exception as e:
            logger.error(f"컨테이너 목록 조회 실패: {str(e)}", exc_info=True)
            return []

    async def cleanup_all_containers(self, label: str = "app=linux-daily-tips") -> int:
        """
        라벨 기준으로 모든 컨테이너 정리 (비동기)

        백그라운드 작업에서 사용됩니다.

        Args:
            label: 필터링할 라벨 (예: "app=linux-daily-tips")

        Returns:
            int: 정리된 컨테이너 수

        Example:
            ```python
            service = DockerService()
            count = await service.cleanup_all_containers()
            print(f"{count}개 컨테이너 정리 완료")
            ```
        """
        try:
            containers = self.client.containers.list(filters={"label": label})
            count = 0

            for container in containers:
                try:
                    await self.remove_container(container.short_id, force=True)
                    count += 1
                except Exception as e:
                    logger.warning(
                        f"컨테이너 정리 실패 (계속 진행): {container.short_id}, {str(e)}"
                    )

            logger.info(f"컨테이너 일괄 정리 완료: {count}개")
            return count

        except Exception as e:
            logger.error(f"컨테이너 정리 중 오류: {str(e)}", exc_info=True)
            return 0
