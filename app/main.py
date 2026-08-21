from fastapi import FastAPI

from app.api.v1.router import router as v1_router
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(title="Story Platform API", version="0.1.0")
register_exception_handlers(app)
app.include_router(v1_router, prefix="/api/v1")


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
