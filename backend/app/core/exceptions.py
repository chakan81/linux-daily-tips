"""
전역 예외 핸들러

FastAPI 애플리케이션의 모든 예외를 일관되게 처리합니다.
- SQLAlchemy 예외
- Pydantic 검증 예외
- HTTP 예외
- 일반 Python 예외

JSON 형식의 일관된 에러 응답을 제공하고, 로깅을 통해 에러를 추적합니다.
"""

import logging
import traceback
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import (
    DatabaseError,
    IntegrityError,
    OperationalError,
    SQLAlchemyError,
)
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings

# 로거 인스턴스
logger = logging.getLogger(__name__)


class AppException(Exception):
    """
    애플리케이션 비즈니스 로직 예외

    Service 레이어에서 발생하는 비즈니스 로직 에러를 표현합니다.
    HTTP 상태 코드와 함께 에러 메시지를 포함합니다.

    Attributes:
        status_code: HTTP 상태 코드 (404, 409, 422 등)
        detail: 에러 상세 메시지

    Example:
        ```python
        raise AppException(
            status_code=404,
            detail="해당 팁을 찾을 수 없습니다"
        )
        ```
    """

    def __init__(self, status_code: int, detail: str = "", message: str = ""):
        self.status_code = status_code
        self.detail = detail or message  # Accept either detail or message
        self.message = detail or message  # Alias for backward compatibility
        super().__init__(self.detail)


class ErrorResponse:
    """
    표준화된 에러 응답 구조

    모든 에러 응답은 이 형식을 따릅니다.
    """

    def __init__(
        self,
        status_code: int,
        error_type: str,
        message: str,
        detail: Any = None,
    ):
        self.status_code = status_code
        self.error_type = error_type
        self.message = message
        self.detail = detail

    def to_dict(self) -> dict:
        """딕셔너리 변환 (JSON 응답용)"""
        response = {
            "error": {
                "type": self.error_type,
                "message": self.message,
            }
        }
        if self.detail is not None:
            response["error"]["detail"] = self.detail
        return response


def setup_exception_handlers(app: FastAPI) -> None:
    """
    FastAPI 앱에 전역 예외 핸들러를 등록합니다.

    Args:
        app: FastAPI 애플리케이션 인스턴스
    """

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request, exc: AppException
    ) -> JSONResponse:
        """
        AppException 핸들러 (비즈니스 로직 에러)

        Service 레이어에서 발생하는 AppException을 처리합니다.
        """
        logger.warning(
            f"AppException: {exc.status_code} - {exc.detail}",
            extra={
                "status_code": exc.status_code,
                "path": request.url.path,
                "method": request.method,
            },
        )

        error_response = ErrorResponse(
            status_code=exc.status_code,
            error_type="business_error",
            message=exc.detail,
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.to_dict(),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        """
        HTTP 예외 핸들러 (404, 403 등)

        FastAPI/Starlette의 HTTPException을 처리합니다.
        """
        logger.warning(
            f"HTTP Exception: {exc.status_code} - {exc.detail}",
            extra={
                "status_code": exc.status_code,
                "path": request.url.path,
                "method": request.method,
            },
        )

        error_response = ErrorResponse(
            status_code=exc.status_code,
            error_type="http_error",
            message=exc.detail or "HTTP error occurred",
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.to_dict(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """
        Pydantic 요청 검증 오류 핸들러

        API 요청 데이터가 스키마 검증에 실패한 경우 처리합니다.
        """
        logger.warning(
            f"Validation Error: {len(exc.errors())} errors",
            extra={
                "path": request.url.path,
                "method": request.method,
                "errors": exc.errors(),
            },
        )

        error_response = ErrorResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_type="validation_error",
            message="요청 데이터 검증에 실패했습니다",
            detail=exc.errors(),
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response.to_dict(),
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(
        request: Request, exc: ValidationError
    ) -> JSONResponse:
        """
        Pydantic 모델 검증 오류 핸들러

        내부적으로 Pydantic 모델 검증이 실패한 경우 처리합니다.
        """
        logger.warning(
            f"Pydantic Validation Error: {len(exc.errors())} errors",
            extra={
                "path": request.url.path,
                "method": request.method,
                "errors": exc.errors(),
            },
        )

        error_response = ErrorResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_type="validation_error",
            message="데이터 검증에 실패했습니다",
            detail=exc.errors(),
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response.to_dict(),
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(
        request: Request, exc: IntegrityError
    ) -> JSONResponse:
        """
        데이터베이스 무결성 오류 핸들러

        UNIQUE 제약 조건 위반, Foreign Key 오류 등을 처리합니다.
        """
        logger.error(
            f"Database Integrity Error: {str(exc.orig)}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "statement": str(exc.statement) if exc.statement else None,
            },
            exc_info=not settings.is_production,
        )

        # 프로덕션에서는 상세 에러 숨김
        detail = None if settings.is_production else str(exc.orig)

        error_response = ErrorResponse(
            status_code=status.HTTP_409_CONFLICT,
            error_type="integrity_error",
            message="데이터베이스 무결성 오류가 발생했습니다",
            detail=detail,
        )

        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=error_response.to_dict(),
        )

    @app.exception_handler(OperationalError)
    async def operational_error_handler(
        request: Request, exc: OperationalError
    ) -> JSONResponse:
        """
        데이터베이스 연결 오류 핸들러

        연결 실패, 타임아웃 등을 처리합니다.
        """
        logger.critical(
            f"Database Operational Error: {str(exc.orig)}",
            extra={
                "path": request.url.path,
                "method": request.method,
            },
            exc_info=True,
        )

        error_response = ErrorResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_type="database_error",
            message="데이터베이스 연결 오류가 발생했습니다",
            detail=None,  # 보안을 위해 상세 정보 숨김
        )

        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=error_response.to_dict(),
        )

    @app.exception_handler(DatabaseError)
    async def database_error_handler(
        request: Request, exc: DatabaseError
    ) -> JSONResponse:
        """
        일반 데이터베이스 오류 핸들러

        SQLAlchemy DatabaseError를 처리합니다.
        """
        logger.error(
            f"Database Error: {str(exc.orig)}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "statement": str(exc.statement) if exc.statement else None,
            },
            exc_info=not settings.is_production,
        )

        detail = None if settings.is_production else str(exc.orig)

        error_response = ErrorResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_type="database_error",
            message="데이터베이스 오류가 발생했습니다",
            detail=detail,
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.to_dict(),
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(
        request: Request, exc: SQLAlchemyError
    ) -> JSONResponse:
        """
        SQLAlchemy 일반 예외 핸들러

        위에서 처리하지 못한 모든 SQLAlchemy 예외를 처리합니다.
        """
        logger.error(
            f"SQLAlchemy Error: {type(exc).__name__} - {str(exc)}",
            extra={
                "path": request.url.path,
                "method": request.method,
            },
            exc_info=not settings.is_production,
        )

        detail = None if settings.is_production else str(exc)

        error_response = ErrorResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_type="database_error",
            message="데이터베이스 오류가 발생했습니다",
            detail=detail,
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.to_dict(),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """
        최종 안전망: 모든 예외 핸들러

        위에서 처리하지 못한 모든 예외를 처리합니다.
        """
        logger.critical(
            f"Unhandled Exception: {type(exc).__name__} - {str(exc)}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "traceback": traceback.format_exc(),
            },
            exc_info=True,
        )

        # 프로덕션에서는 상세 에러 숨김
        detail = None if settings.is_production else {
            "type": type(exc).__name__,
            "message": str(exc),
            "traceback": traceback.format_exc() if settings.DEBUG else None,
        }

        error_response = ErrorResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_type="internal_error",
            message="서버 내부 오류가 발생했습니다",
            detail=detail,
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.to_dict(),
        )

    logger.info("전역 예외 핸들러 등록 완료")
