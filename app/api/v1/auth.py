from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exception import UnauthorizedError
from app.db.session import get_db
from app.schemas.user import LoginRequest
from app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", status_code=201, description="Login and get access token")
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    token = await auth_service.login(db, credentials)
    if not token:
        raise UnauthorizedError()
    return {
        "status_code": 201,
        "status": True,
        "access_token": token,
        "token_type": "Bearer",
    }
