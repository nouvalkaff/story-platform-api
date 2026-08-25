from typing import Any, cast

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exception import ForbiddenError, NotFoundError, UnauthorizedError
from app.crud.crud_user import crud_user
from app.models.user import User, UserRole
from app.schemas.user import TokenPayload

REQUIRED_TOKEN_FIELDS = ("sub", "role", "email")
REQUIRED_DB_FIELDS = ("id", "role", "email")
FIELD_PAIRS = (("sub", "id"), ("email", "email"), ("role", "role"))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def _verify_token_matches_user(
    token_payload: TokenPayload, db_payload: dict[str, Any]
) -> None:
    tp = token_payload
    dp = db_payload

    if any(not getattr(tp, field) for field in REQUIRED_TOKEN_FIELDS):
        raise UnauthorizedError()

    if any(not dp.get(field) for field in REQUIRED_DB_FIELDS):
        raise UnauthorizedError()

    for tp_field, dp_field in FIELD_PAIRS:
        if getattr(tp, tp_field) != dp[dp_field]:
            raise UnauthorizedError()


def _get_jwt_token(scheme_token: str) -> str:
    if not scheme_token:
        raise UnauthorizedError()

    scheme, token = scheme_token.split(" ", 1)

    if scheme.lower() != "bearer":
        raise UnauthorizedError()

    return token


def validate_auth(
    token: str | None = Depends(oauth2_scheme),
) -> None:
    try:
        if token is None:
            raise UnauthorizedError()

        jwt.decode(
            token,
            get_settings().secret_key,
            algorithms=[get_settings().algorithm],
        )
    except JWTError:
        raise UnauthorizedError()


def decode_token_to_payload(
    scheme_token: str, is_raw_token: bool = False
) -> TokenPayload:
    try:
        jwt_token = scheme_token

        if is_raw_token:
            validate_auth(jwt_token)
        else:
            jwt_token = _get_jwt_token(scheme_token)

        payload = jwt.get_unverified_claims(jwt_token)

        sub = payload.get("sub")

        if sub is None:
            raise UnauthorizedError()

        payload["sub"] = int(sub)

        if payload.get("role") not in {each.value for each in UserRole}:
            raise ForbiddenError()

        return TokenPayload(**payload)
    except (JWTError, ValueError):
        raise UnauthorizedError()


def validate_user_access(payload: TokenPayload, target_user_id: int) -> None:
    if payload.sub != target_user_id:
        raise ForbiddenError()


def validate_admin_access(
    payload: TokenPayload,
    is_validate_access: bool = False,
    user_id_db: int | None = None,
) -> None:
    if payload.role == UserRole.ADMIN:
        return

    if is_validate_access:
        if user_id_db is None:
            raise ForbiddenError()

        validate_user_access(payload, user_id_db)
        return

    raise ForbiddenError()


async def authenticate_user(
    request: Request,
    db: AsyncSession,
    is_check_admin: bool = False,
    is_validate_access: bool = False,
) -> User:
    scheme_token = cast(str, request.headers.get("Authorization"))

    payload = decode_token_to_payload(scheme_token)

    user = await crud_user.get(db, payload.sub)

    if not user:
        raise NotFoundError()

    if not user.is_active:
        raise UnauthorizedError(
            "Account suspended. Email support@example.com to restore access."
        )

    _verify_token_matches_user(payload, user.to_dict())

    if is_check_admin:
        validate_admin_access(payload, is_validate_access, user.id)

    return user
