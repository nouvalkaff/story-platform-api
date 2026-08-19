from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

app = FastAPI(title="Story Platform API", version="0.1.0")


@app.get("/health", tags=["System"])
async def health_check() -> dict[str, str | bool | int]:
    return {"status": True, "message": "System healthy", "statusCode": 200}


@app.get("/", tags=["System"])
async def root() -> dict[str, str | bool | int]:
    return {
        "status": True,
        "message": "Welcome to API Story Platform",
        "statusCode": 200,
    }


# Temporary endpoint to test DB
@app.get("/health/db", tags=["System"])
async def test_db(
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> dict[str, str | int | bool]:
    await db.execute(text("SELECT 1"))

    return {
        "status": True,
        "message": "Database connection healthy",
        "statusCode": 200,
    }
