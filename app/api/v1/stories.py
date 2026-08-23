from fastapi import APIRouter, status

router = APIRouter(prefix="/your-story", tags=["Story"])


@router.post(
    "/add",
    description="Add a new user short story",
    status_code=status.HTTP_201_CREATED,
)
async def add():
    pass
