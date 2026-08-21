from fastapi import status


class AppException(Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_message = "Internal server error"

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.default_message
        super().__init__(self.message)


class BadRequestError(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "Bad request"


class UnauthorizedError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_message = "Unauthorized"


class ForbiddenError(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    default_message = "Forbidden access"


class NotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    default_message = "Resource not found"


class ConflictError(AppException):
    status_code = status.HTTP_409_CONFLICT
    default_message = "Resource already exists"
