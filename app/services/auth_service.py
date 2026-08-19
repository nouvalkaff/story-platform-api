from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, verify_password
from app.crud.crud_user import crud_user
from app.models.user import User
from app.schemas.user import LoginRequest, UserCreate


class AuthService:
    async def register(self, db: AsyncSession, user_data: UserCreate) -> User:
        existing = await crud_user.get_by_email(db, user_data.email)
        if existing:
            raise ValueError("Email already registered")
        return await crud_user.create(db, user_data)

    async def login(self, db: AsyncSession, credentials: LoginRequest) -> str | None:
        user = await crud_user.get_by_email(db, credentials.email)
        if not user or not verify_password(credentials.password, user.hashed_password):
            return None
        return create_access_token(data={"sub": str(user.id)})


auth_service = AuthService()
