"""
Docker 서비스 통합 인터페이스

기존 DockerService 클래스와 동일한 인터페이스를 제공하여 하위 호환성을 유지합니다.

Example:
    ```python
    # 기존 사용법 그대로 유지
    from app.services.docker import DockerService

    service = DockerService()
    container_id = await service.create_container("session_123")
    result = await service.execute_command(container_id, "ls -la")
    ```
"""

import logging
from typing import Any

import docker
from docker.errors import DockerException

from app.core.exceptions import AppException
from app.services.docker.command_executor import CommandExecutor
from app.services.docker.container_manager import ContainerManager
from app.services.docker.resource_monitor import ResourceMonitor
from app.services.docker.security_validator import SecurityValidator

logger = logging.getLogger(__name__)


class DockerService:
    """
    Docker 컨테이너 관리 서비스

    안전한 샌드박스 환경에서 터미널 명령어를 실행합니다.

    내부적으로 4개 모듈로 분리되어 있으나, 기존 인터페이스를 그대로 유지합니다:
    - ContainerManager: 컨테이너 생명주기 관리
    - CommandExecutor: 명령어 실행
    - SecurityValidator: 보안 검증
    - ResourceMonitor: 리소스 모니터링

    Attributes:
        client: Docker SDK 클라이언트
        container_manager: 컨테이너 관리자
        command_executor: 명령어 실행기
        security_validator: 보안 검증기
        resource_monitor: 리소스 모니터
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

        # 모듈 초기화
        self.container_manager = ContainerManager(self.client)
        self.command_executor = CommandExecutor(self.client)
        self.security_validator = SecurityValidator()
        self.resource_monitor = ResourceMonitor(self.client)

    # === 컨테이너 생명주기 메서드 (ContainerManager 위임) ===

    async def create_container(
        self,
        session_id: str | None = None,
        terminal_setup: dict[str, Any] | None = None,
        image: str | None = None,
    ) -> str:
        """
        Docker 컨테이너 생성 및 시작 (비동기)

        ContainerManager에게 위임합니다.
        """
        return await self.container_manager.create_container(
            session_id=session_id,
            terminal_setup=terminal_setup,
            image=image,
        )

    async def start_container(self, container_id: str) -> bool:
        """컨테이너 시작 (ContainerManager 위임)"""
        return await self.container_manager.start_container(container_id)

    async def stop_container(
        self, container_id: str, timeout: int | None = None
    ) -> bool:
        """컨테이너 중지 (ContainerManager 위임)"""
        return await self.container_manager.stop_container(container_id, timeout)

    async def remove_container(self, container_id: str, force: bool = True) -> bool:
        """컨테이너 삭제 (ContainerManager 위임)"""
        return await self.container_manager.remove_container(container_id, force)

    async def get_container_status(self, container_id: str) -> str:
        """컨테이너 상태 조회 (ContainerManager 위임)"""
        return await self.container_manager.get_container_status(container_id)

    async def list_containers(
        self, filters: dict[str, str] | None = None
    ) -> list[dict[str, Any]]:
        """컨테이너 목록 조회 (ContainerManager 위임)"""
        return await self.container_manager.list_containers(filters)

    async def cleanup_all_containers(self, label: str = "app=linux-daily-tips") -> int:
        """컨테이너 일괄 정리 (ContainerManager 위임)"""
        return await self.container_manager.cleanup_all_containers(label)

    # === 명령어 실행 메서드 (CommandExecutor 위임) ===

    async def execute_command(
        self, container_id: str, command: str, timeout: int | None = None
    ) -> dict[str, Any]:
        """
        컨테이너에서 명령어 실행 (비동기)

        CommandExecutor에게 위임합니다.
        """
        return await self.command_executor.execute_command(
            container_id, command, timeout
        )

    # === 보안 검증 메서드 (SecurityValidator 위임) ===

    def is_command_safe(self, command: str) -> bool:
        """
        명령어 안전성 검증 (블랙리스트 기반)

        SecurityValidator에게 위임합니다.
        """
        return self.security_validator.is_command_safe(command)

    # === 리소스 모니터링 메서드 (ResourceMonitor 위임) ===

    async def get_container_stats(self, container_id: str) -> dict[str, Any]:
        """
        컨테이너 리소스 사용량 조회

        ResourceMonitor에게 위임합니다.
        """
        return await self.resource_monitor.get_container_stats(container_id)


# 하위 호환성을 위한 export
__all__ = [
    "DockerService",
    "ContainerManager",
    "CommandExecutor",
    "SecurityValidator",
    "ResourceMonitor",
]
