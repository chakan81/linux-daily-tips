"""
Docker 컨테이너 리소스 모니터링

컨테이너의 메모리, CPU 사용량 등 리소스 정보를 조회합니다.
"""

import asyncio
import logging
from typing import Any

import docker
from docker.errors import NotFound

from app.core.exceptions import AppException

logger = logging.getLogger(__name__)


class ResourceMonitor:
    """
    컨테이너 리소스 모니터

    컨테이너의 메모리, CPU 사용량을 조회합니다.

    Attributes:
        client: Docker SDK 클라이언트
    """

    def __init__(self, client: docker.DockerClient) -> None:
        """
        ResourceMonitor 초기화

        Args:
            client: Docker SDK 클라이언트
        """
        self.client = client

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
