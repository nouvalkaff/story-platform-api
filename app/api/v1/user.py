from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    authenticate_user,
    decode_token_to_payload,
    oauth2_scheme,
    validate_admin_access,
    validate_auth,
)
from app.core.exception import (
    BadRequestError,
    ConflictError,
    NotFoundError,
    UnauthorizedError,
)
from app.core.security import get_password_hash, verify_password
from app.crud.crud_story import crud_story
from app.crud.crud_user import crud_user
from app.db.session import get_db
from app.models.user import UserRole
from app.schemas.common import ApiResponse
from app.schemas.user import (
    UserCreateDetail,
    UserCreatePayload,
    UserListResponse,
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
    user_data: UserCreatePayload,
    db: AsyncSession = Depends(get_db),  # noqa: B008
    token: str | None = Depends(oauth2_scheme),
):
    new_user = UserCreateDetail(**user_data.model_dump())

    if token:
        payload = decode_token_to_payload(token, is_raw_token=True)

        validate_admin_access(payload)

        new_user.created_by = payload.sub
        new_user.updated_by = payload.sub

    user = await auth_service.register(db, new_user)

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
    dependencies=[Depends(validate_auth)],
)
async def get_my_data(
    request: Request,
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    current_user = await authenticate_user(request, db)

    return {
        "status_code": status.HTTP_200_OK,
        "status": True,
        "message": "Success",
        "data": current_user,
    }


@router.get(
    "/all",
    response_model=ApiResponse[UserListResponse],
    description="Get all users data [ADMIN-only]",
    dependencies=[Depends(validate_auth)],
)
async def get_all_users(
    request: Request,
    db: AsyncSession = Depends(get_db),  # noqa: B008
    include_active: bool = True,
    include_inactive: bool = False,
):
    await authenticate_user(request, db, is_check_admin=True)

    users = await crud_user.get_all(db, include_active, include_inactive)

    return {
        "status_code": status.HTTP_200_OK,
        "status": True,
        "message": "Success",
        "data": {"total": len(users), "users": users},
    }


@router.patch(
    "/{user_id}",
    response_model=ApiResponse[UserResponse],
    description="Update user email and full name",
    dependencies=[Depends(validate_auth)],
)
async def update(
    request: Request,
    user_id: int,
    update_data: UserUpdate,
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    user_db = await crud_user.get(db, user_id)

    if user_db is None:
        raise NotFoundError()

    current_user = await authenticate_user(
        request,
        db,
        is_check_admin=True,
        is_validate_access=True,
    )

    if update_data.email is not None:
        is_email_exist = await crud_user.get_by_email(db, update_data.email)

        if is_email_exist:
            raise ConflictError("Email already registered")

    user_dict = user_db.to_dict()
    update_dict = update_data.model_dump(exclude_unset=True)

    for key, val in update_dict.items():
        if val != user_dict[key]:
            setattr(user_db, key, val)

    user_db.updated_by = current_user.id

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
    dependencies=[Depends(validate_auth)],
)
async def update_password(
    request: Request,
    user_id: int,
    update_data: UserPasswordUpdate,
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    old_pass = update_data.old_password

    new_pass = update_data.new_password

    user_db = await crud_user.get(db, user_id)

    if user_db is None:
        raise NotFoundError()

    current_user = await authenticate_user(
        request,
        db,
        is_check_admin=True,
        is_validate_access=True,
    )

    if current_user.role != UserRole.ADMIN:
        if not old_pass:
            raise BadRequestError("old_password cannot be empty")

        if not verify_password(old_pass, user_db.hashed_password):
            raise UnauthorizedError("Incorrect old password")

    user_db.hashed_password = get_password_hash(new_pass)

    user_db.updated_by = current_user.id

    updated_user_db = await crud_user.update(db, user_db)

    return {
        "status_code": status.HTTP_200_OK,
        "status": True,
        "message": f"Password user {user_id} updated successfully",
        "data": updated_user_db,
    }


@router.delete(
    "/sdelete/{user_id}",
    response_model=ApiResponse[UserResponse],
    description="Soft delete user account",
    dependencies=[Depends(validate_auth)],
)
async def soft_delete(
    request: Request,
    user_id: int,
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    user_db = await crud_user.get(db, user_id)

    if user_db is None:
        raise NotFoundError()

    current_user = await authenticate_user(
        request,
        db,
        is_check_admin=True,
        is_validate_access=True,
    )

    user_db.is_active = False

    user_db.updated_by = current_user.id

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
    dependencies=[Depends(validate_auth)],
)
async def hard_delete(
    request: Request,
    user_id: int,
    is_agree: bool = False,
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    user_db = await crud_user.get(db, user_id)

    if user_db is None:
        raise NotFoundError()

    await authenticate_user(
        request,
        db,
        is_check_admin=True,
        is_validate_access=True,
    )

    story_count = await crud_story.count_by_author(db, user_id)
    if story_count > 0 and not is_agree:
        raise ConflictError("User cannot be deleted because they still own stories")

    await crud_story.delete_by_author(db, user_id, commit=False)
    await crud_user.delete(db, user_db, commit=False)
    await db.commit()

    return {
        "status_code": status.HTTP_200_OK,
        "status": True,
        "message": f"User {user_id} permanently deleted successfully",
        "data": None,
    }
