from typing import Any, cast

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exception import ForbiddenError, NotFoundError, UnauthorizedError
from app.crud.crud_user import crud_user
from app.db.session import get_db
from app.models.user import User, UserRole

REQUIRED_TOKEN_FIELDS = ("sub", "role", "email")
REQUIRED_DB_FIELDS = ("id", "role", "email")
FIELD_PAIRS = (("sub", "id"), ("email", "email"), ("role", "role"))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def verify_token_matches_user(token_payload: dict, db_payload: dict) -> None:
    tp = token_payload
    dp = db_payload

    if any(not tp.get(field) for field in REQUIRED_TOKEN_FIELDS):
        raise UnauthorizedError()

    if any(not dp[field] for field in REQUIRED_DB_FIELDS):
        raise UnauthorizedError()

    tp = {**tp, "sub": int(tp["sub"])}

    for tp_field, dp_field in FIELD_PAIRS:
        if tp[tp_field] != dp[dp_field]:
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
) -> dict[str, Any]:
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

        return payload
    except (JWTError, ValueError):
        raise UnauthorizedError()


async def get_authenticated_user(
    request: Request,
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> User:
    scheme_token = cast(str, request.headers.get("Authorization"))

    payload = decode_token_to_payload(scheme_token)

    user = await crud_user.get(db, payload["sub"])

    if not user:
        raise NotFoundError()

    verify_token_matches_user(payload, user.to_dict())

    return user
