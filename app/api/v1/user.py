from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_my_data(
    current_user: User = Depends(get_current_user),  # noqa: B008
) -> UserResponse:
    return current_user
