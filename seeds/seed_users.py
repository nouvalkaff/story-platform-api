from sqlalchemy import select

from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.user import User
from app.schemas.user import UserRole


USERS = (
    {
        "full_name": "Admin User",
        "email": "admin@example.com",
        "password": "Admin1234!",
        "role": UserRole.ADMIN,
    },
    {
        "full_name": "Regular User",
        "email": "user@example.com",
        "password": "User1234!",
        "role": UserRole.USER,
    },
)


def seed_users() -> bool:
    """Insert standard users, skipping the seed when all of them already exist."""
    with SessionLocal() as session:
        try:
            seed_emails = [user_data["email"] for user_data in USERS]
            existing_emails = set(
                session.scalars(
                    select(User.email).where(User.email.in_(seed_emails))
                ).all()
            )
            if len(existing_emails) == len(USERS):
                return False

            for user_data in USERS:
                existing_user = session.scalar(
                    select(User).where(User.email == user_data["email"])
                )
                if existing_user is not None:
                    continue

                session.add(
                    User(
                        full_name=user_data["full_name"],
                        email=user_data["email"],
                        hashed_password=get_password_hash(user_data["password"]),
                        role=user_data["role"],
                    )
                )

            session.commit()
            return True
        except Exception:
            session.rollback()
            raise


if __name__ == "__main__":
    seed_users()
