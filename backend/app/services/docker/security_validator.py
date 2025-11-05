"""
Docker 명령어 보안 검증

터미널에서 실행될 명령어의 안전성을 검증합니다.
"""

import logging

from app.config.docker_config import DANGEROUS_COMMANDS

logger = logging.getLogger(__name__)


class SecurityValidator:
    """
    명령어 보안 검증기

    위험한 명령어를 블랙리스트 기반으로 차단합니다.
    """

    def __init__(self) -> None:
        """SecurityValidator 초기화"""
        self.dangerous_commands = DANGEROUS_COMMANDS

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
            validator = SecurityValidator()
            if not validator.is_command_safe("rm -rf /"):
                raise ValueError("위험한 명령어입니다")
            ```
        """
        command_lower = command.lower().strip()

        # 블랙리스트 검증
        for dangerous in self.dangerous_commands:
            if dangerous in command_lower:
                logger.warning(f"위험한 명령어 차단됨: {command}")
                return False

        # 파이프를 통한 우회 방지
        if "|" in command:
            for dangerous in self.dangerous_commands:
                if dangerous in command_lower:
                    logger.warning(f"파이프 우회 시도 차단됨: {command}")
                    return False

        return True
