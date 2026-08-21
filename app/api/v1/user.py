from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.exception import (
    BadRequestError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
)
from app.core.security import get_password_hash, verify_password
from app.crud.crud_user import crud_user
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.common import ApiResponse
from app.schemas.user import (
    UserCreate,
    UserPasswordUpdate,
    UserResponse,
    UserUpdate,
)
from app.services.auth_service import auth_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/create",
    response_model=ApiResponse[UserResponse],
    description="Create a new user",
    status_code=status.HTTP_201_CREATED,
)
async def create(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    user = await auth_service.register(db, user_data)

    return {
        "status_code": status.HTTP_201_CREATED,
        "status": True,
        "message": "User created successfully",
        "data": user,
    }


@router.get(
    "/me",
    response_model=ApiResponse[UserResponse],
    description="Get user data by id from token",
)
async def get_my_data(
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    return {
        "status_code": status.HTTP_200_OK,
        "status": True,
        "message": "Success",
        "data": current_user,
    }


@router.patch(
    "/{user_id}",
    response_model=ApiResponse[UserResponse],
    description="Update user email and full name",
)
async def update(
    user_id: int,
    update_data: UserUpdate,
    db: AsyncSession = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    user_db = await crud_user.get(db, user_id)

    if user_db is None:
        raise NotFoundError()

    if current_user.role != UserRole.ADMIN and current_user.id != user_db.id:
        raise ForbiddenError()

    user_dict = current_user.to_dict()
    update_dict = update_data.model_dump(exclude_unset=True)

    for key, val in update_dict.items():
        if val != user_dict[key]:
            setattr(user_db, key, val)

    updated_user_db = await crud_user.update(db, user_db)

    return {
        "status_code": status.HTTP_200_OK,
        "status": True,
        "message": "Details updated successfully",
        "data": updated_user_db,
    }


@router.patch(
    "/change-password/{user_id}",
    response_model=ApiResponse[UserResponse],
    description="Update user password",
)
async def update_password(
    user_id: int,
    update_data: UserPasswordUpdate,
    db: AsyncSession = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    old_pass = update_data.old_password
    new_pass = update_data.new_password
    user_db = await crud_user.get(db, user_id)

    if user_db is None:
        raise NotFoundError()

    if current_user.role != UserRole.ADMIN:
        if not old_pass:
            raise BadRequestError("old_password cannot be empty")

        if current_user.id != user_db.id:
            raise ForbiddenError()

        if not verify_password(old_pass, user_db.hashed_password):
            raise UnauthorizedError("Incorrect old password")

    user_db.hashed_password = get_password_hash(new_pass)
    updated_user_db = await crud_user.update(db, user_db)

    return {
        "status_code": status.HTTP_200_OK,
        "status": True,
        "message": f"Password user {user_id} updated succesfully",
        "data": updated_user_db,
    }


@router.delete(
    "/sdelete/{user_id}",
    response_model=ApiResponse[UserResponse],
    description="Soft delete user account",
)
async def soft_delete(
    user_id: int,
    db: AsyncSession = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    user_db = await crud_user.get(db, user_id)

    if user_db is None:
        raise NotFoundError()

    if current_user.role != UserRole.ADMIN and current_user.id != user_db.id:
        raise ForbiddenError()

    user_db.is_active = False
    updated_user_db = await crud_user.update(db, user_db)

    return {
        "status_code": status.HTTP_200_OK,
        "status": True,
        "message": f"User {user_id} deactivated successfully",
        "data": updated_user_db,
    }


@router.delete(
    "/hdelete/{user_id}",
    response_model=ApiResponse[None],
    description="Permanently delete user account",
    status_code=status.HTTP_200_OK,
)
async def hard_delete(
    user_id: int,
    db: AsyncSession = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    user_db = await crud_user.get(db, user_id)

    if user_db is None:
        raise NotFoundError()

    if current_user.role != UserRole.ADMIN and current_user.id != user_db.id:
        raise ForbiddenError()

    await crud_user.delete(db, user_db)

    return {
        "status_code": status.HTTP_200_OK,
        "status": True,
        "message": f"User {user_id} permanently deleted successfully",
        "data": None,
    }
