from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import authenticate_user, validate_auth
from app.core.exception import ConflictError
from app.crud.crud_story import crud_story
from app.db.session import get_db
from app.models.story import StoryStatus
from app.schemas.common import ApiResponse
from app.schemas.story import (
    PublishedStoryPagedResponse,
    StoryCreate,
    StoryCreateDetail,
    StoryListPagedResponse,
    StoryResponse,
)
from app.services.story_service import story_service

router = APIRouter(prefix="/story", tags=["Story"])


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


@router.get(
    "/user/{user_id}",
    description="Get stories by user ID",
    response_model=ApiResponse[StoryListPagedResponse],
    dependencies=[Depends(validate_auth)],
)
async def get_stories_by_user_id(
    request: Request,
    user_id: int,
    page: int = Query(default=1, ge=1),
    page_limit: int = Query(default=5, ge=1),
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    user = await authenticate_user(request, db)

    stories, total = await story_service.get_stories_by_user_id(
        db,
        user_id,
        user,
        page=page,
        page_limit=page_limit,
    )

    if stories:
        message = "Success"
    elif user.id == user_id:
        message = "No stories found"
    else:
        message = "This user has no published stories."

    result = {"total": total, "stories": stories}

    return {
        "status_code": status.HTTP_200_OK,
        "status": True,
        "message": message,
        "data": result,
    }


@router.get(
    "/published",
    description="Get published stories with optional search",
    response_model=ApiResponse[PublishedStoryPagedResponse],
    dependencies=[Depends(validate_auth)],
)
async def get_published_stories(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=5, ge=1),
    q: str | None = Query(default=None, min_length=1),
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    stories, total = await story_service.get_published_stories(
        db,
        page=page,
        size=size,
        q=q,
    )

    return {
        "status_code": status.HTTP_200_OK,
        "status": True,
        "message": "Success" if stories else "No published stories found",
        "data": {"total": total, "page": page, "size": size, "stories": stories},
    }


@router.get(
    "/{story_id}",
    description="Get a story by ID",
    response_model=ApiResponse[StoryResponse | None],
    dependencies=[Depends(validate_auth)],
)
async def get_story(
    request: Request,
    story_id: int,
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    user = await authenticate_user(request, db)

    story = await story_service.get_story_by_id(db, story_id)

    message = "Success"

    if story.status != StoryStatus.PUBLISHED and story.author_id != user.id:
        message = "Story is unavailable for public access."
        story = None

    return {
        "status_code": status.HTTP_200_OK,
        "status": True,
        "message": message,
        "data": story,
    }
