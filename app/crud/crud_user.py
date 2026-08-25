from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exception import BadRequestError
from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreateDetail


class CRUDUser:
    async def get(self, db: AsyncSession, user_id: int) -> User | None:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_all(
        self,
        db: AsyncSession,
        include_active: bool = True,
        include_inactive: bool = False,
    ) -> list[User]:
        if not include_active and not include_inactive:
            raise BadRequestError("Select at least one user status")

        statement = select(User)

        if include_active and not include_inactive:
            statement = statement.where(User.is_active.is_(True))

        elif not include_active and include_inactive:
            statement = statement.where(User.is_active.is_(False))

        statement = statement.order_by(User.id.asc())

        result = await db.execute(statement)

        return list(result.scalars().all())

    async def create(self, db: AsyncSession, user_data: UserCreateDetail) -> User:
        hashed_password = get_password_hash(user_data.password)

        db_obj = User(
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            created_by=user_data.created_by,
            updated_by=user_data.updated_by,
        )

        db.add(db_obj)

        if db_obj.created_by is None and db_obj.updated_by is None:
            await db.flush()

            db_obj.created_by = db_obj.id
            db_obj.updated_by = db_obj.id

        await db.commit()
        await db.refresh(db_obj)

        return db_obj

    async def update(self, db: AsyncSession, user_detail: User) -> User:
        db.add(user_detail)

        await db.commit()
        await db.refresh(user_detail)

        return user_detail

    async def delete(
        self,
        db: AsyncSession,
        user_detail: User,
        *,
        commit: bool = True,
    ) -> None:
        await db.delete(user_detail)
        if commit:
            await db.commit()

    async def clear_audit_references(
        self,
        db: AsyncSession,
        user_id: int,
        *,
        commit: bool = True,
    ) -> None:
        await db.execute(
            update(User).where(User.created_by == user_id).values(created_by=None)
        )

        await db.execute(
            update(User).where(User.updated_by == user_id).values(updated_by=None)
        )

        if commit:
            await db.commit()


crud_user = CRUDUser()
