from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str


class UserCreatePayload(UserBase):
    password: str


class UserCreateDetail(UserCreatePayload):
    created_by: int | None = None
    updated_by: int | None = None


class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr | None = None
    full_name: str | None = None


class UserPasswordUpdate(BaseModel):
    old_password: str | None = None
    new_password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    created_by: int
    updated_at: datetime
    updated_by: int
    role: UserRole

    model_config = ConfigDict(from_attributes=True)
