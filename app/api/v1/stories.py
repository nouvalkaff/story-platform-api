from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import authenticate_user, validate_auth
from app.core.exception import ConflictError
from app.crud.crud_story import crud_story
from app.db.session import get_db
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
    user = await authenticate_user(request, db)

    new_story_detail = StoryCreateDetail(
        **new_story_payload.model_dump(),
        author_id=user.id,
        created_by=user.id,
        updated_by=user.id,
    )

    title_from_body = new_story_payload.title

    title_exist = await crud_story.get_by_title(db, title_from_body)

    if title_exist:
        raise ConflictError(f"Title '{title_from_body}' already exists.")

    new_story = await crud_story.create(db, new_story_detail)

    return {
        "status_code": status.HTTP_201_CREATED,
        "status": True,
        "message": "User created successfully",
        "data": new_story,
    }
