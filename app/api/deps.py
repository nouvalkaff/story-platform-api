from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.crud.crud_user import crud_user
from app.db.session import get_db
from app.models.user import User

REQUIRED_TOKEN_FIELDS = ("sub", "role", "email")
REQUIRED_DB_FIELDS = ("id", "role", "email")
FIELD_PAIRS = (("sub", "id"), ("email", "email"), ("role", "role"))
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"  # pyright: ignore[reportCallIssue]
)


@staticmethod
def creds_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def decode_token_to_payload(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token, get_settings().secret_key, algorithms=[get_settings().algorithm]
        )
        payload = {**payload, "sub": int(payload["sub"])}
        return payload
    except (JWTError, ValueError):
        raise creds_exception()


def verify_token_matches_user(token_payload: dict, db_payload: dict) -> None:
    tp = token_payload
    dp = db_payload

    if any(tp.get(field) is None for field in REQUIRED_TOKEN_FIELDS):
        raise creds_exception()
    if any(dp[field] is None for field in REQUIRED_DB_FIELDS):
        raise creds_exception()

    tp = {**tp, "sub": int(tp["sub"])}

    for tp_field, dp_field in FIELD_PAIRS:
        if tp[tp_field] != dp[dp_field]:
            raise creds_exception()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> User:
    try:
        payload = decode_token_to_payload(token)
        user_id_token = payload.get("sub")
        if user_id_token is None:
            raise creds_exception()
    except JWTError:
        raise creds_exception()
    user = await crud_user.get(db, int(user_id_token))
    verify_token_matches_user(payload, user.to_dict())
    return user
