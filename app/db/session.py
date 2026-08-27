from collections.abc import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session

from app.core.config import get_settings

settings = get_settings()
engine = create_async_engine(settings.database_url, echo=settings.sql_echo)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Manual scripts, such as seeders, use a synchronous SQLAlchemy session.  The
# application URL uses asyncpg, so switch only its driver portion for psycopg.
# Creating it lazily keeps the async API importable until the optional sync
# PostgreSQL driver is installed.
sync_database_url = settings.database_url.replace("+asyncpg", "+psycopg", 1)
sync_engine: Engine | None = None


def SessionLocal() -> Session:
    global sync_engine
    if sync_engine is None:
        sync_engine = create_engine(sync_database_url, echo=settings.sql_echo)
    return Session(bind=sync_engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
