from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate


class CRUDUser:
    @staticmethod
    def creds_exception() -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    async def get(self, db: AsyncSession, user_id: int):
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, db: AsyncSession, email: str):
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, obj_in: UserCreate):
        hashed = get_password_hash(obj_in.password)

        db_obj = User(
            email=obj_in.email, hashed_password=hashed, full_name=obj_in.full_name
        )

        db.add(db_obj)

        try:
            await db.commit()
            await db.refresh(db_obj)
        except SQLAlchemyError:
            await db.rollback()
            raise

        return db_obj

    async def update(self, db: AsyncSession, user_detail: User) -> User:
        try:
            db.add(user_detail)

            await db.commit()

            await db.refresh(user_detail)

            return user_detail
        except SQLAlchemyError:
            await db.rollback()
            raise

    async def delete(self, db: AsyncSession, user_detail: User) -> None:
        try:
            await db.delete(user_detail)
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise


crud_user = CRUDUser()
