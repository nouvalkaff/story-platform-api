from collections.abc import Mapping, Sequence

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from pydantic_core import ErrorDetails
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exception import AppException
from app.core.logging import logger
from app.schemas.common import ApiResponse

SENSITIVE_FIELD_NAMES = frozenset(
    {
        "access_token",
        "api_key",
        "authorization",
        "credential",
        "credentials",
        "password",
        "refresh_token",
        "secret",
        "token",
    }
)
SENSITIVE_MESSAGE_TERMS = ("password", "token", "credential", "secret")


def _validation_error_message(errors: Sequence[ErrorDetails]) -> str:
    if not errors:
        return "Invalid request data"

    locations = [error["loc"] for error in errors]
    if any(
        isinstance(part, str) and part.casefold() in SENSITIVE_FIELD_NAMES
        for location in locations
        for part in location
    ):
        return "Invalid request data"

    error = errors[0]
    field = next(
        (
            part
            for part in reversed(error["loc"])
            if isinstance(part, str)
            and part not in {"body", "cookie", "header", "path", "query"}
        ),
        None,
    )

    if field is None:
        return "Invalid request data"

    if error["type"] == "missing":
        return f"{field} is required"
    if error["type"] == "enum":
        if field == "genre":
            return (
                "Invalid genre. Allowed values: unspecified, romance, horror, "
                "mystery, fantasy, sci-fi, adventure, drama"
            )
        context = error.get("ctx")
        expected = context.get("expected") if context else None
        if isinstance(expected, str):
            return f"{field} must be one of: {expected}"
        return f"{field} has an invalid value"
    if error["type"] == "extra_forbidden":
        return f"{field} is not allowed"

    return f"{field} is invalid"


def _app_exception_message(exc: AppException) -> str:
    message = exc.message
    if any(term in message.casefold() for term in SENSITIVE_MESSAGE_TERMS):
        return exc.default_message

    return message


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

        return error_response(
            status_code=exc.status_code,
            message=_app_exception_message(exc),
        )

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
        message = _validation_error_message(exc.errors())
        logger.warning(
            "Request validation error | %s %s | %s",
            request.method,
            request.url.path,
            message,
        )

        return error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            message=message,
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(
        request: Request,
        exc: ValidationError,
    ) -> JSONResponse:
        message = _validation_error_message(exc.errors())
        logger.warning(
            "Pydantic validation error | %s %s | %s",
            request.method,
            request.url.path,
            message,
        )

        return error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            message=message,
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
