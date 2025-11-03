"""
Docker 컨테이너 생명주기 관리

컨테이너의 생성, 시작, 중지, 삭제, 조회 등의 생명주기를 관리합니다.
"""

import asyncio
import logging
import time
from typing import Any

import docker
from docker.errors import APIError, NotFound
from docker.models.containers import Container

from app.config.docker_config import (
    CONTAINER_CPU_QUOTA,
    CONTAINER_IMAGE,
    CONTAINER_MEMORY_LIMIT,
    CONTAINER_PIDS_LIMIT,
    CONTAINER_STOP_TIMEOUT,
    CONTAINER_WORKDIR,
    DEFAULT_CONTAINER_LABEL,
)
from app.core.exceptions import AppException

logger = logging.getLogger(__name__)


class ContainerManager:
    """
    Docker 컨테이너 생명주기 관리자

    컨테이너 생성, 시작, 중지, 삭제, 조회, 일괄 정리 기능을 제공합니다.

    Attributes:
        client: Docker SDK 클라이언트
    """

    def __init__(self, client: docker.DockerClient) -> None:
        """
        ContainerManager 초기화

        Args:
            client: Docker SDK 클라이언트
        """
        self.client = client

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
            manager = ContainerManager(client)
            container_id = await manager.create_container("session_01JCAW...")
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
                "working_dir": CONTAINER_WORKDIR,
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
            stop_timeout = timeout if timeout is not None else CONTAINER_STOP_TIMEOUT
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
            manager = ContainerManager(client)
            containers = await manager.list_containers(filters={"status": "running"})
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

    async def cleanup_all_containers(self, label: str = DEFAULT_CONTAINER_LABEL) -> int:
        """
        라벨 기준으로 모든 컨테이너 정리 (비동기)

        백그라운드 작업에서 사용됩니다.

        Args:
            label: 필터링할 라벨 (예: "app=linux-daily-tips")

        Returns:
            int: 정리된 컨테이너 수

        Example:
            ```python
            manager = ContainerManager(client)
            count = await manager.cleanup_all_containers()
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
