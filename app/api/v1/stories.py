from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_authenticated_user, validate_auth
from app.crud.crud_story import crud_story
from app.db.session import get_db
from app.models.story import StoryGenre
from app.schemas.common import ApiResponse
from app.schemas.story import StoryCreate, StoryCreateDetail, StoryResponse

router = APIRouter(prefix="/your-story", tags=["Story"])


@router.post(
    "/add",
    description="Add a new user short story",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(validate_auth)],
    response_model=ApiResponse[StoryResponse],
)
async def add(
    request: Request,
    new_story_payload: StoryCreate,
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    user = await get_authenticated_user(request, db)

    genre = new_story_payload.genre

    new_story_detail = StoryCreateDetail(
        **new_story_payload.model_dump(),
        genre=genre if genre else StoryGenre.UNSPECIFIED,
        author_id=user.id,
        created_by=user.id,
        updated_by=user.id,
    )

    new_story = await crud_story.create(db, new_story_detail)

    return {
        "status_code": status.HTTP_201_CREATED,
        "status": True,
        "message": "User created successfully",
        "data": new_story,
    }
