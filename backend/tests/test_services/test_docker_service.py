"""
DockerService 테스트 (TDD - RED 단계)

Docker 컨테이너 관리 서비스의 핵심 기능을 테스트합니다:
- 컨테이너 생성 (이미지, 리소스 제한, 네트워크 격리)
- 컨테이너 시작/중지/삭제
- 명령어 실행 및 출력 스트리밍
- 보안 설정 검증 (메모리 256MB, CPU 0.5코어, PID 100개 제한)
- 위험 명령어 블랙리스트 검증
- 명령어 타임아웃 (5초)
- 출력 크기 제한 (10KB)

주의: DockerService가 구현되지 않았으므로 이 테스트들은 실패해야 합니다!
"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from docker.errors import APIError, ContainerError, ImageNotFound, NotFound
from docker.models.containers import Container

from app.core.exceptions import AppException


@pytest.fixture
def mock_docker_client() -> MagicMock:
    """
    Mock Docker 클라이언트

    실제 Docker API를 호출하지 않고 테스트할 수 있도록
    docker.DockerClient를 모킹합니다.
    """
    client = MagicMock()
    client.containers = MagicMock()
    client.images = MagicMock()
    return client


@pytest.fixture
def mock_container() -> MagicMock:
    """
    Mock Docker 컨테이너

    docker.models.containers.Container를 모킹합니다.
    """
    container = MagicMock(spec=Container)
    container.id = "abc123def456"
    container.short_id = "abc123de"
    container.status = "running"
    container.name = "test_container"
    return container


@pytest.mark.asyncio
@pytest.mark.unit
class TestDockerServiceContainerLifecycle:
    """Docker 컨테이너 생명주기 관리 테스트"""

    async def test_create_container_with_default_settings(
        self, mock_docker_client: MagicMock
    ) -> None:
        """
        기본 설정으로 컨테이너 생성

        Given: Docker 클라이언트가 정상 동작
        When: create_container() 호출 (인자 없음)
        Then: 기본 이미지와 설정으로 컨테이너 생성
        """
        # Arrange
        from app.services.docker_service import DockerService

        mock_container = MagicMock()
        mock_container.id = "abc123def456"
        mock_docker_client.containers.run.return_value = mock_container

        service = DockerService(client=mock_docker_client)

        # Act
        container_id = await service.create_container()

        # Assert
        assert container_id == "abc123def456", "컨테이너 ID가 반환되어야 함"
        mock_docker_client.containers.run.assert_called_once()

        # 기본 이미지 검증
        call_args = mock_docker_client.containers.run.call_args
        assert call_args.kwargs["image"] == "linux-daily-tips-terminal:latest"
        assert call_args.kwargs["detach"] is True

    async def test_create_container_with_resource_limits(
        self, mock_docker_client: MagicMock
    ) -> None:
        """
        리소스 제한 설정 검증

        Given: Docker 클라이언트가 정상 동작
        When: create_container() 호출
        Then: 메모리 256MB, CPU 0.5코어, PID 100개 제한 적용
        """
        # Arrange
        from app.services.docker_service import DockerService

        mock_container = MagicMock()
        mock_container.id = "abc123def456"
        mock_docker_client.containers.run.return_value = mock_container

        service = DockerService(client=mock_docker_client)

        # Act
        await service.create_container()

        # Assert
        call_args = mock_docker_client.containers.run.call_args
        assert call_args.kwargs["mem_limit"] == "256m", "메모리 256MB 제한"
        assert call_args.kwargs["memswap_limit"] == "256m", "스왑 비활성화"
        assert call_args.kwargs["cpu_quota"] == 50000, "CPU 0.5 코어 (50%)"
        assert call_args.kwargs["pids_limit"] == 100, "최대 프로세스 100개"

    async def test_create_container_with_network_isolation(
        self, mock_docker_client: MagicMock
    ) -> None:
        """
        네트워크 격리 설정 검증

        Given: Docker 클라이언트가 정상 동작
        When: create_container() 호출
        Then: network_mode="none" 설정되어야 함
        """
        # Arrange
        from app.services.docker_service import DockerService

        mock_container = MagicMock()
        mock_container.id = "abc123def456"
        mock_docker_client.containers.run.return_value = mock_container

        service = DockerService(client=mock_docker_client)

        # Act
        await service.create_container()

        # Assert
        call_args = mock_docker_client.containers.run.call_args
        assert (
            call_args.kwargs["network_mode"] == "none"
        ), "외부 네트워크 완전 차단"

    async def test_create_container_with_read_only_filesystem(
        self, mock_docker_client: MagicMock
    ) -> None:
        """
        읽기 전용 파일시스템 설정 검증

        Given: Docker 클라이언트가 정상 동작
        When: create_container() 호출
        Then: read_only=True, tmpfs 설정되어야 함
        """
        # Arrange
        from app.services.docker_service import DockerService

        mock_container = MagicMock()
        mock_container.id = "abc123def456"
        mock_docker_client.containers.run.return_value = mock_container

        service = DockerService(client=mock_docker_client)

        # Act
        await service.create_container()

        # Assert
        call_args = mock_docker_client.containers.run.call_args
        assert call_args.kwargs["read_only"] is True, "루트 파일시스템 읽기 전용"

        # tmpfs 마운트 검증
        tmpfs = call_args.kwargs.get("tmpfs", {})
        assert "/tmp" in tmpfs, "임시 파일 디렉토리 tmpfs 마운트"
        assert "/workspace" in tmpfs, "작업 공간 tmpfs 마운트"
        assert "size=50m" in tmpfs["/tmp"], "임시 파일 50MB 제한"
        assert "size=50m" in tmpfs["/workspace"], "작업 공간 50MB 제한"

    async def test_create_container_with_custom_image(
        self, mock_docker_client: MagicMock
    ) -> None:
        """
        커스텀 이미지로 컨테이너 생성

        Given: Docker 클라이언트가 정상 동작
        When: create_container(image="custom:latest") 호출
        Then: 지정된 이미지로 컨테이너 생성
        """
        # Arrange
        from app.services.docker_service import DockerService

        mock_container = MagicMock()
        mock_container.id = "custom123"
        mock_docker_client.containers.run.return_value = mock_container

        service = DockerService(client=mock_docker_client)

        # Act
        container_id = await service.create_container(image="custom:latest")

        # Assert
        assert container_id == "custom123"
        call_args = mock_docker_client.containers.run.call_args
        assert call_args.kwargs["image"] == "custom:latest"

    async def test_create_container_fails_when_image_not_found(
        self, mock_docker_client: MagicMock
    ) -> None:
        """
        이미지 없을 때 에러 처리

        Given: Docker 이미지가 존재하지 않음
        When: create_container() 호출
        Then: AppException 발생
        """
        # Arrange
        from app.services.docker_service import DockerService

        mock_docker_client.containers.run.side_effect = ImageNotFound(
            "Image not found"
        )
        service = DockerService(client=mock_docker_client)

        # Act & Assert
        with pytest.raises(AppException) as exc_info:
            await service.create_container()

        assert "이미지를 찾을 수 없습니다" in str(exc_info.value.message)
        assert exc_info.value.status_code == 500

    async def test_create_container_fails_on_docker_api_error(
        self, mock_docker_client: MagicMock
    ) -> None:
        """
        Docker API 에러 처리

        Given: Docker API가 에러 반환
        When: create_container() 호출
        Then: AppException 발생
        """
        # Arrange
        from app.services.docker_service import DockerService

        mock_docker_client.containers.run.side_effect = APIError(
            "Docker daemon error"
        )
        service = DockerService(client=mock_docker_client)

        # Act & Assert
        with pytest.raises(AppException) as exc_info:
            await service.create_container()

        assert "컨테이너 생성 실패" in str(exc_info.value.message)
        assert exc_info.value.status_code == 500

    async def test_start_container_succeeds(
        self, mock_docker_client: MagicMock, mock_container: MagicMock
    ) -> None:
        """
        컨테이너 시작 성공

        Given: 중지된 컨테이너가 존재
        When: start_container(container_id) 호출
        Then: 컨테이너 시작됨
        """
        # Arrange
        from app.services.docker_service import DockerService

        mock_docker_client.containers.get.return_value = mock_container
        service = DockerService(client=mock_docker_client)

        # Act
        await service.start_container("abc123def456")

        # Assert
        mock_docker_client.containers.get.assert_called_once_with("abc123def456")
        mock_container.start.assert_called_once()

    async def test_start_container_fails_when_not_found(
        self, mock_docker_client: MagicMock
    ) -> None:
        """
        존재하지 않는 컨테이너 시작 시도

        Given: 컨테이너가 존재하지 않음
        When: start_container(container_id) 호출
        Then: AppException 발생
        """
        # Arrange
        from app.services.docker_service import DockerService

        mock_docker_client.containers.get.side_effect = NotFound("Container not found")
        service = DockerService(client=mock_docker_client)

        # Act & Assert
        with pytest.raises(AppException) as exc_info:
            await service.start_container("invalid_id")

        assert "컨테이너를 찾을 수 없습니다" in str(exc_info.value.message)

    async def test_stop_container_succeeds(
        self, mock_docker_client: MagicMock, mock_container: MagicMock
    ) -> None:
        """
        컨테이너 중지 성공

        Given: 실행 중인 컨테이너가 존재
        When: stop_container(container_id) 호출
        Then: 컨테이너 중지됨
        """
        # Arrange
        from app.services.docker_service import DockerService

        mock_docker_client.containers.get.return_value = mock_container
        service = DockerService(client=mock_docker_client)

        # Act
        await service.stop_container("abc123def456")

        # Assert
        mock_docker_client.containers.get.assert_called_once_with("abc123def456")
        mock_container.stop.assert_called_once()

    async def test_stop_container_with_timeout(
        self, mock_docker_client: MagicMock, mock_container: MagicMock
    ) -> None:
        """
        타임아웃 설정으로 컨테이너 중지

        Given: 실행 중인 컨테이너가 존재
        When: stop_container(container_id, timeout=10) 호출
        Then: 10초 타임아웃으로 중지 시도
        """
        # Arrange
        from app.services.docker_service import DockerService

        mock_docker_client.containers.get.return_value = mock_container
        service = DockerService(client=mock_docker_client)

        # Act
        await service.stop_container("abc123def456", timeout=10)

        # Assert
        mock_container.stop.assert_called_once_with(timeout=10)

    async def test_remove_container_succeeds(
        self, mock_docker_client: MagicMock, mock_container: MagicMock
    ) -> None:
        """
        컨테이너 삭제 성공

        Given: 컨테이너가 존재
        When: remove_container(container_id) 호출
        Then: 컨테이너 삭제됨
        """
        # Arrange
        from app.services.docker_service import DockerService

        mock_docker_client.containers.get.return_value = mock_container
        service = DockerService(client=mock_docker_client)

        # Act
        await service.remove_container("abc123def456")

        # Assert
        mock_docker_client.containers.get.assert_called_once_with("abc123def456")
        mock_container.remove.assert_called_once()

    async def test_remove_container_with_force(
        self, mock_docker_client: MagicMock, mock_container: MagicMock
    ) -> None:
        """
        강제 삭제 옵션으로 컨테이너 삭제

        Given: 실행 중인 컨테이너가 존재
        When: remove_container(container_id, force=True) 호출
        Then: 강제로 삭제됨
        """
        # Arrange
        from app.services.docker_service import DockerService

        mock_docker_client.containers.get.return_value = mock_container
        service = DockerService(client=mock_docker_client)

        # Act
        await service.remove_container("abc123def456", force=True)

        # Assert
        mock_container.remove.assert_called_once_with(force=True)

    async def test_remove_container_fails_when_not_found(
        self, mock_docker_client: MagicMock
    ) -> None:
        """
        존재하지 않는 컨테이너 삭제 시도

        Given: 컨테이너가 존재하지 않음
        When: remove_container(container_id) 호출
        Then: AppException 발생
        """
        # Arrange
        from app.services.docker_service import DockerService

        mock_docker_client.containers.get.side_effect = NotFound("Container not found")
        service = DockerService(client=mock_docker_client)

        # Act & Assert
        with pytest.raises(AppException) as exc_info:
            await service.remove_container("invalid_id")

        assert "컨테이너를 찾을 수 없습니다" in str(exc_info.value.message)


@pytest.mark.asyncio
@pytest.mark.unit
class TestDockerServiceCommandExecution:
    """Docker 컨테이너 명령어 실행 테스트"""

    async def test_execute_command_succeeds(
        self, mock_docker_client: MagicMock, mock_container: MagicMock
    ) -> None:
        """
        명령어 실행 성공

        Given: 실행 중인 컨테이너가 존재
        When: execute_command(container_id, "ls -la") 호출
        Then: 명령어 실행 결과 반환
        """
        # Arrange
        from app.services.docker_service import DockerService

        mock_docker_client.containers.get.return_value = mock_container
        mock_container.exec_run.return_value = (
            0,  # exit_code
            b"total 8\ndrwxr-xr-x 2 root root 4096 Oct 28 12:00 .\n",  # output
        )

        service = DockerService(client=mock_docker_client)

        # Act
        result = await service.execute_command("abc123def456", "ls -la")

        # Assert
        assert result["exit_code"] == 0
        assert "total 8" in result["output"]
        assert result["error"] == ""

        # Docker exec_run 호출 검증
        mock_container.exec_run.assert_called_once()
        call_args = mock_container.exec_run.call_args
        assert call_args.kwargs["cmd"] == ["bash", "-c", "ls -la"]
        assert call_args.kwargs["stdout"] is True
        assert call_args.kwargs["stderr"] is True

    async def test_execute_command_with_demux(
        self, mock_docker_client: MagicMock, mock_container: MagicMock
    ) -> None:
        """
        stdout와 stderr를 분리하여 반환

        Given: 실행 중인 컨테이너가 존재
        When: execute_command(container_id, "ls invalid") 호출 (에러 발생)
        Then: stdout와 stderr 분리된 결과 반환
        """
        # Arrange
        from app.services.docker_service import DockerService

        mock_docker_client.containers.get.return_value = mock_container
        # demux=True일 때 반환 형식: (exit_code, (stdout, stderr))
        mock_container.exec_run.return_value = (
            2,  # exit_code
            (
                b"",  # stdout
                b"ls: cannot access 'invalid': No such file or directory\n",  # stderr
            ),
        )

        service = DockerService(client=mock_docker_client)

        # Act
        result = await service.execute_command("abc123def456", "ls invalid")

        # Assert
        assert result["exit_code"] == 2
        assert result["output"] == ""
        assert "No such file or directory" in result["error"]

    async def test_execute_command_with_timeout(
        self, mock_docker_client: MagicMock, mock_container: MagicMock
    ) -> None:
        """
        타임아웃 설정으로 명령어 실행

        Given: 실행 중인 컨테이너가 존재
        When: execute_command(container_id, "sleep 10", timeout=5) 호출
        Then: 5초 후 타임아웃
        """
        # Arrange
        from app.services.docker_service import DockerService

        mock_docker_client.containers.get.return_value = mock_container
        service = DockerService(client=mock_docker_client)

        # Act
        await service.execute_command("abc123def456", "sleep 10", timeout=5)

        # Assert
        call_args = mock_container.exec_run.call_args
        assert call_args.kwargs.get("timeout") == 5

    async def test_execute_command_fails_on_timeout(
        self, mock_docker_client: MagicMock, mock_container: MagicMock
    ) -> None:
        """
        명령어 실행 타임아웃 에러 처리

        Given: 실행 중인 컨테이너가 존재
        When: 명령어 실행이 타임아웃 초과
        Then: AppException 발생
        """
        # Arrange
        from app.services.docker_service import DockerService

        mock_docker_client.containers.get.return_value = mock_container
        mock_container.exec_run.side_effect = APIError(
            "timeout: context deadline exceeded"
        )

        service = DockerService(client=mock_docker_client)

        # Act & Assert
        with pytest.raises(AppException) as exc_info:
            await service.execute_command("abc123def456", "sleep 999", timeout=5)

        assert "타임아웃" in str(exc_info.value.message)

    async def test_execute_command_truncates_large_output(
        self, mock_docker_client: MagicMock, mock_container: MagicMock
    ) -> None:
        """
        큰 출력 크기 제한 (10KB)

        Given: 실행 중인 컨테이너가 존재
        When: 10KB 이상 출력하는 명령어 실행
        Then: 출력이 10KB로 잘림
        """
        # Arrange
        from app.services.docker_service import DockerService

        mock_docker_client.containers.get.return_value = mock_container
        # 15KB 출력 (10KB 제한 초과)
        large_output = b"X" * (15 * 1024)
        mock_container.exec_run.return_value = (0, large_output)

        service = DockerService(client=mock_docker_client)

        # Act
        result = await service.execute_command("abc123def456", "cat large_file")

        # Assert
        assert len(result["output"]) <= 10 * 1024, "출력이 10KB로 제한되어야 함"
        assert "출력이 잘렸습니다" in result["output"], "잘림 메시지 포함되어야 함"

    async def test_execute_command_fails_when_container_not_found(
        self, mock_docker_client: MagicMock
    ) -> None:
        """
        존재하지 않는 컨테이너에 명령어 실행 시도

        Given: 컨테이너가 존재하지 않음
        When: execute_command(invalid_id, "ls") 호출
        Then: AppException 발생
        """
        # Arrange
        from app.services.docker_service import DockerService

        mock_docker_client.containers.get.side_effect = NotFound("Container not found")
        service = DockerService(client=mock_docker_client)

        # Act & Assert
        with pytest.raises(AppException) as exc_info:
            await service.execute_command("invalid_id", "ls")

        assert "컨테이너를 찾을 수 없습니다" in str(exc_info.value.message)


@pytest.mark.asyncio
@pytest.mark.unit
class TestDockerServiceSecurityValidation:
    """Docker 보안 검증 테스트"""

    async def test_is_command_safe_allows_safe_commands(self) -> None:
        """
        안전한 명령어 허용

        Given: 안전한 명령어 목록
        When: is_command_safe() 호출
        Then: True 반환
        """
        # Arrange
        from app.services.docker_service import DockerService

        service = DockerService()

        safe_commands = [
            "ls -la",
            "pwd",
            "echo 'Hello, Linux!'",
            "cat file.txt",
            "grep 'pattern' file.txt",
            "find . -name '*.log'",
            "ps aux",
            "df -h",
            "whoami",
        ]

        # Act & Assert
        for command in safe_commands:
            assert service.is_command_safe(
                command
            ), f"'{command}'는 안전한 명령어여야 함"

    async def test_is_command_safe_blocks_dangerous_commands(self) -> None:
        """
        위험한 명령어 차단

        Given: 블랙리스트에 있는 위험 명령어
        When: is_command_safe() 호출
        Then: False 반환
        """
        # Arrange
        from app.services.docker_service import DockerService

        service = DockerService()

        dangerous_commands = [
            "rm -rf /",
            "mkfs.ext4 /dev/sda1",
            "dd if=/dev/zero of=/dev/sda",
            "iptables -F",
            "ufw disable",
            "systemctl stop docker",
            "service networking stop",
            "nc -l 4444",
            "netcat -l 4444",
            "nmap 192.168.1.0/24",
            "apt-get install malware",
            "apt install virus",
            "yum install badpackage",
            "dnf install exploit",
            "useradd hacker",
            "userdel admin",
            "passwd root",
            "sudo rm -rf /",
            "su - root",
        ]

        # Act & Assert
        for command in dangerous_commands:
            assert not service.is_command_safe(
                command
            ), f"'{command}'는 차단되어야 함"

    async def test_is_command_safe_blocks_pipe_bypass_attempts(self) -> None:
        """
        파이프를 통한 우회 시도 차단

        Given: 파이프로 위험 명령어를 숨긴 시도
        When: is_command_safe() 호출
        Then: False 반환
        """
        # Arrange
        from app.services.docker_service import DockerService

        service = DockerService()

        bypass_attempts = [
            "echo 'test' | sudo rm -rf /",
            "ls -la | systemctl stop docker",
            "cat file.txt | apt-get install malware",
        ]

        # Act & Assert
        for command in bypass_attempts:
            assert not service.is_command_safe(
                command
            ), f"'{command}'는 차단되어야 함"

    async def test_is_command_safe_case_insensitive(self) -> None:
        """
        대소문자 구분 없이 검증

        Given: 대문자로 작성된 위험 명령어
        When: is_command_safe() 호출
        Then: False 반환
        """
        # Arrange
        from app.services.docker_service import DockerService

        service = DockerService()

        # Act & Assert
        assert not service.is_command_safe("RM -RF /")
        assert not service.is_command_safe("SuDo Rm -rf /")
        assert not service.is_command_safe("SYSTEMCTL STOP docker")

    async def test_execute_command_blocks_dangerous_command(
        self, mock_docker_client: MagicMock, mock_container: MagicMock
    ) -> None:
        """
        위험한 명령어 실행 차단

        Given: 실행 중인 컨테이너가 존재
        When: execute_command(container_id, "rm -rf /") 호출
        Then: AppException 발생, 실제 실행되지 않음
        """
        # Arrange
        from app.services.docker_service import DockerService

        mock_docker_client.containers.get.return_value = mock_container
        service = DockerService(client=mock_docker_client)

        # Act & Assert
        with pytest.raises(AppException) as exc_info:
            await service.execute_command("abc123def456", "rm -rf /")

        assert "위험한 명령어" in str(exc_info.value.message)
        assert exc_info.value.status_code == 403

        # 실제 Docker exec_run이 호출되지 않았는지 확인
        mock_container.exec_run.assert_not_called()

    async def test_execute_command_validates_command_length(
        self, mock_docker_client: MagicMock, mock_container: MagicMock
    ) -> None:
        """
        명령어 길이 제한 검증 (최대 1000자)

        Given: 실행 중인 컨테이너가 존재
        When: 1000자를 초과하는 명령어 실행
        Then: AppException 발생
        """
        # Arrange
        from app.services.docker_service import DockerService

        mock_docker_client.containers.get.return_value = mock_container
        service = DockerService(client=mock_docker_client)

        # 1001자 명령어
        long_command = "echo " + "X" * 1000

        # Act & Assert
        with pytest.raises(AppException) as exc_info:
            await service.execute_command("abc123def456", long_command)

        assert "명령어 길이 제한" in str(exc_info.value.message)
        assert exc_info.value.status_code == 400


@pytest.mark.asyncio
@pytest.mark.unit
class TestDockerServiceUtilities:
    """Docker 유틸리티 메서드 테스트"""

    async def test_get_container_status(
        self, mock_docker_client: MagicMock, mock_container: MagicMock
    ) -> None:
        """
        컨테이너 상태 조회

        Given: 컨테이너가 존재
        When: get_container_status(container_id) 호출
        Then: 컨테이너 상태 반환
        """
        # Arrange
        from app.services.docker_service import DockerService

        mock_container.status = "running"
        mock_docker_client.containers.get.return_value = mock_container
        service = DockerService(client=mock_docker_client)

        # Act
        status = await service.get_container_status("abc123def456")

        # Assert
        assert status == "running"

    async def test_get_container_stats(
        self, mock_docker_client: MagicMock, mock_container: MagicMock
    ) -> None:
        """
        컨테이너 리소스 사용량 조회

        Given: 실행 중인 컨테이너가 존재
        When: get_container_stats(container_id) 호출
        Then: CPU/메모리 사용량 반환
        """
        # Arrange
        from app.services.docker_service import DockerService

        mock_container.stats.return_value = {
            "memory_stats": {"usage": 100 * 1024 * 1024, "limit": 256 * 1024 * 1024},
            "cpu_stats": {"cpu_usage": {"total_usage": 1000000000}},
        }
        mock_docker_client.containers.get.return_value = mock_container
        service = DockerService(client=mock_docker_client)

        # Act
        stats = await service.get_container_stats("abc123def456")

        # Assert
        assert "memory_usage" in stats
        assert stats["memory_usage"] == 100 * 1024 * 1024
        assert stats["memory_limit"] == 256 * 1024 * 1024

    async def test_list_containers(self, mock_docker_client: MagicMock) -> None:
        """
        모든 컨테이너 목록 조회

        Given: 여러 컨테이너가 존재
        When: list_containers() 호출
        Then: 컨테이너 목록 반환
        """
        # Arrange
        from app.services.docker_service import DockerService

        mock_container1 = MagicMock()
        mock_container1.id = "abc123"
        mock_container1.status = "running"

        mock_container2 = MagicMock()
        mock_container2.id = "def456"
        mock_container2.status = "exited"

        mock_docker_client.containers.list.return_value = [
            mock_container1,
            mock_container2,
        ]
        service = DockerService(client=mock_docker_client)

        # Act
        containers = await service.list_containers()

        # Assert
        assert len(containers) == 2
        assert containers[0]["id"] == "abc123"
        assert containers[0]["status"] == "running"
        assert containers[1]["id"] == "def456"
        assert containers[1]["status"] == "exited"

    async def test_list_containers_with_filter(
        self, mock_docker_client: MagicMock
    ) -> None:
        """
        필터링된 컨테이너 목록 조회

        Given: 여러 상태의 컨테이너가 존재
        When: list_containers(filters={"status": "running"}) 호출
        Then: 실행 중인 컨테이너만 반환
        """
        # Arrange
        from app.services.docker_service import DockerService

        mock_container = MagicMock()
        mock_container.id = "abc123"
        mock_container.status = "running"

        mock_docker_client.containers.list.return_value = [mock_container]
        service = DockerService(client=mock_docker_client)

        # Act
        containers = await service.list_containers(filters={"status": "running"})

        # Assert
        assert len(containers) == 1
        mock_docker_client.containers.list.assert_called_once_with(
            all=True, filters={"status": "running"}
        )
