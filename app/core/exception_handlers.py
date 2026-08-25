from collections.abc import Mapping

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exception import AppException
from app.core.logging import logger
from app.schemas.common import ApiResponse


def error_response(
    status_code: int,
    message: str,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    response = ApiResponse[None](
        status_code=status_code, status=False, message=message, data=None
    )
    return JSONResponse(
        status_code=status_code, content=response.model_dump(), headers=headers
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request,
        exc: AppException,
    ) -> JSONResponse:
        logger.warning(
            "Application error | %s %s | %s",
            request.method,
            request.url.path,
            exc.message,
        )

        return error_response(status_code=exc.status_code, message=exc.message)

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        logger.warning(
            "HTTP error | %s %s | status=%s",
            request.method,
            request.url.path,
            exc.status_code,
        )

        message = (
            str(exc.detail)
            if exc.status_code < status.HTTP_500_INTERNAL_SERVER_ERROR
            else "Internal server error"
        )

        return error_response(
            status_code=exc.status_code,
            message=message,
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        logger.warning(
            "Request validation error | %s %s | %s",
            request.method,
            request.url.path,
            exc.errors(),
        )

        return error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            message="Invalid request data",
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(
        request: Request,
        exc: ValidationError,
    ) -> JSONResponse:
        logger.warning(
            "Pydantic validation error | %s %s | %s",
            request.method,
            request.url.path,
            exc.errors(),
        )

        return error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            message="Validation failed",
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(
        request: Request,
        exc: ValueError,
    ) -> JSONResponse:
        logger.warning(
            "Value error | %s %s | %s",
            request.method,
            request.url.path,
            exc,
        )

        return error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Invalid request",
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(
        request: Request,
        exc: IntegrityError,
    ) -> JSONResponse:
        logger.exception(
            "Database integrity error | %s %s",
            request.method,
            request.url.path,
        )

        return error_response(
            status_code=status.HTTP_409_CONFLICT,
            message="Resource conflict",
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(
        request: Request,
        exc: SQLAlchemyError,
    ) -> JSONResponse:
        logger.exception(
            "Database error | %s %s",
            request.method,
            request.url.path,
        )

        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Database operation failed",
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        logger.exception(
            "Unhandled error | %s %s",
            request.method,
            request.url.path,
        )

        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
        )
