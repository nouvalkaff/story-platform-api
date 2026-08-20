from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.user import UserRole

T = TypeVar("T")


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None
    role: UserRole = UserRole.USER


class UserCreate(UserBase):
    password: str


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


class ApiResponse[T](BaseModel):
    status_code: int
    status: bool
    message: str
    data: T


class UserResponse(UserBase):
    id: int
    is_active: bool
    role: UserRole
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
