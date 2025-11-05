"""
로깅 설정 모듈

구조화된 로깅 시스템을 제공합니다.
- JSON 형식 로그 (프로덕션)
- 컬러 포맷 로그 (개발)
- 로그 레벨 관리
- 파일 로테이션
- 요청 추적 (Request ID)
"""

import logging
import sys
from pathlib import Path
from typing import Any

from pythonjsonlogger import jsonlogger

from app.core.config import settings


class ColoredFormatter(logging.Formatter):
    """
    컬러 로그 포맷터 (개발 환경용)

    로그 레벨에 따라 다른 색상을 적용합니다.
    """

    # ANSI 색상 코드
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        """로그 레코드를 컬러 포맷으로 변환"""
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname:8}{self.RESET}"
        return super().format(record)


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    커스텀 JSON 포맷터 (프로덕션 환경용)

    구조화된 JSON 로그를 생성합니다.
    """

    def add_fields(
        self,
        log_record: dict[str, Any],
        record: logging.LogRecord,
        message_dict: dict[str, Any],
    ) -> None:
        """로그 필드 커스터마이징"""
        super().add_fields(log_record, record, message_dict)

        # 기본 필드 추가
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["module"] = record.module
        log_record["function"] = record.funcName
        log_record["line"] = record.lineno

        # 환경 정보
        log_record["environment"] = settings.ENVIRONMENT


def setup_logging() -> None:
    """
    로깅 시스템 초기화

    환경에 따라 다른 포맷을 적용합니다:
    - 프로덕션: JSON 형식 (구조화된 로그)
    - 개발: 컬러 포맷 (가독성)
    """
    # 로그 레벨 설정
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # 기존 핸들러 제거 (중복 방지)
    root_logger.handlers.clear()

    # 콘솔 핸들러 추가
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    if settings.is_production:
        # 프로덕션: JSON 포맷
        json_formatter = CustomJsonFormatter(
            "%(timestamp)s %(level)s %(logger)s %(module)s %(function)s %(line)d %(message)s"
        )
        console_handler.setFormatter(json_formatter)
    else:
        # 개발: 컬러 포맷
        colored_formatter = ColoredFormatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(colored_formatter)

    root_logger.addHandler(console_handler)

    # 파일 핸들러 추가 (프로덕션 전용)
    if settings.is_production:
        # 로그 디렉토리 생성
        log_dir = Path("/var/log/linux-daily-tips")
        log_dir.mkdir(parents=True, exist_ok=True)

        # 로그 파일 경로
        log_file = log_dir / "app.log"

        # 로테이팅 파일 핸들러 (10MB, 최대 5개 백업)
        from logging.handlers import RotatingFileHandler

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(json_formatter)
        root_logger.addHandler(file_handler)

    # 써드파티 라이브러리 로그 레벨 조정
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.WARNING if settings.is_production else logging.INFO
    )

    # 로깅 초기화 완료 메시지
    logger = logging.getLogger(__name__)
    logger.info(
        f"로깅 시스템 초기화 완료 (환경: {settings.ENVIRONMENT}, 레벨: {logging.getLevelName(log_level)})"
    )


def get_logger(name: str) -> logging.Logger:
    """
    로거 인스턴스 생성

    Args:
        name: 로거 이름 (일반적으로 __name__)

    Returns:
        logging.Logger: 로거 인스턴스

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Hello, world!")
    """
    return logging.getLogger(name)
