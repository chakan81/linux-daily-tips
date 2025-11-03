"""
터미널 서비스 모듈

TerminalService를 재export하여 backward compatibility를 보장합니다.

사용법:
    from app.services.terminal import TerminalService
"""

from app.services.terminal.terminal_service import TerminalService

__all__ = ["TerminalService"]
