from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    bad_request_exception,
    creds_exception,
    forbidden_exception,
    get_current_user,
    not_found_exception,
)
from app.core.security import get_password_hash, verify_password
from app.crud.crud_user import crud_user
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.user import (
    ApiResponse,
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
    status_code=201,
)
async def create(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    try:
        user = await auth_service.register(db, user_data)
        return {
            "status_code": 201,
            "status": True,
            "message": "User created successfully",
            "data": user,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/me",
    response_model=ApiResponse[UserResponse],
    description="Get user data by id from token",
)
async def get_my_data(
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    return {
        "status_code": 200,
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
        raise not_found_exception()
    if current_user.role != UserRole.ADMIN and current_user.id != user_db.id:
        raise forbidden_exception()
    user_dict = current_user.to_dict()
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, val in update_dict.items():
        if val != user_dict[key]:
            setattr(user_db, key, val)
    db.add(user_db)
    await db.commit()
    await db.refresh(user_db)
    return {
        "status_code": 200,
        "status": True,
        "message": "Details updated successfully",
        "data": user_db,
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
        raise not_found_exception()

    if current_user.role != UserRole.ADMIN:
        if not old_pass:
            raise bad_request_exception("old_password cannot be empty")
        if current_user.id != user_db.id:
            raise forbidden_exception()
        if not verify_password(old_pass, user_db.hashed_password):
            raise creds_exception("Incorrect old password")

    new_hashed_password = get_password_hash(new_pass)
    user_db.hashed_password = new_hashed_password

    db.add(user_db)
    await db.commit()
    await db.refresh(user_db)
    return {
        "status_code": 200,
        "status": True,
        "message": f"Password user {user_id} updated succesfully",
        "data": user_db,
    }
