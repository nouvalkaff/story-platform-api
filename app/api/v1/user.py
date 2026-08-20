from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import auth_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/create", response_model=UserResponse)
async def create(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    try:
        user = await auth_service.register(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/me", response_model=UserResponse)
async def get_my_data(
    current_user: User = Depends(get_current_user),  # noqa: B008
) -> UserResponse:
    return current_user
