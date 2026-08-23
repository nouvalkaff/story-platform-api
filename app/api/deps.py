from typing import Any

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exception import NotFoundError, UnauthorizedError
from app.crud.crud_user import crud_user
from app.db.session import get_db
from app.models.user import User

REQUIRED_TOKEN_FIELDS = ("sub", "role", "email")
REQUIRED_DB_FIELDS = ("id", "role", "email")
FIELD_PAIRS = (("sub", "id"), ("email", "email"), ("role", "role"))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def decode_token_to_payload(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token, get_settings().secret_key, algorithms=[get_settings().algorithm]
        )

        payload = {**payload, "sub": int(payload["sub"])}

        return payload
    except (JWTError, ValueError):
        raise UnauthorizedError()


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


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> User | None:
    try:
        payload = decode_token_to_payload(token)

        user_id_token = payload.get("sub")

        if user_id_token is None:
            raise UnauthorizedError()

    except JWTError:
        raise UnauthorizedError()

    user = await crud_user.get(db, int(user_id_token))

    if not user:
        raise NotFoundError()

    verify_token_matches_user(payload, user.to_dict())

    return user
