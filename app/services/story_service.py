from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exception import ForbiddenError, NotFoundError
from app.crud.crud_story import crud_story
from app.crud.crud_user import crud_user
from app.models.story import Story, StoryStatus
from app.models.user import User, UserRole
from app.schemas.story import StoryCreate, StoryCreateDetail, StoryUpdate


class StoryService:
    async def create_story(
        self,
        db: AsyncSession,
        story_data: StoryCreate,
        *,
        current_user: User,
    ) -> Story:
        story_data_detail = StoryCreateDetail(
            **story_data.model_dump(),
            author_id=current_user.id,
            created_by=current_user.id,
            updated_by=current_user.id,
        )
        return await crud_story.create(db, story_data_detail)

    async def get_story_by_id(
        self,
        db: AsyncSession,
        story_id: int,
    ) -> Story:
        story = await crud_story.get_by_id(db, story_id)

        if story is None:
            raise NotFoundError("Story not found")

        return story

    @staticmethod
    def _truncate_content(content: str, limit_len: int):
        return (
            f"{content[:limit_len].strip()}...[READ_MORE]"
            if len(content) > limit_len
            else content
        )

    async def get_stories_by_user_id(
        self,
        db: AsyncSession,
        user_id: int,
        current_user: User,
        *,
        page: int = 1,
        page_limit: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        user = await crud_user.get(db, user_id)

        if user is None:
            raise NotFoundError("User not found")

        status = None if current_user.id == user_id else StoryStatus.PUBLISHED

        stories, total = await crud_story.get_stories_by_user_id(
            db,
            user_id,
            status=status,
            page=page,
            page_limit=page_limit,
        )

        result: list[dict[str, Any]] = []

        for each in stories:
            story_dict = {c.name: getattr(each, c.name) for c in each.__table__.columns}

            story_dict["author"] = current_user.full_name

            story_dict["content"] = self._truncate_content(story_dict["content"], 100)

            result.append(story_dict)

        return result, total

    async def update_story(
        self,
        db: AsyncSession,
        story_id: int,
        update_data: StoryUpdate,
        *,
        current_user: User,
    ) -> Story:
        story = await self._get_editable_story(db, story_id, current_user)
        return await crud_story.update(
            db, story, update_data, updated_by=current_user.id
        )

    async def delete_story(
        self,
        db: AsyncSession,
        story_id: int,
        *,
        current_user: User,
    ) -> None:
        story = await self._get_editable_story(db, story_id, current_user)
        await crud_story.delete(db, story)

    async def publish_story(
        self,
        db: AsyncSession,
        story_id: int,
        *,
        current_user: User,
    ) -> Story:
        story = await self._get_editable_story(db, story_id, current_user)
        return await crud_story.set_publication(
            db,
            story,
            status=StoryStatus.PUBLISHED,
            published_at=datetime.now(UTC),
            updated_by=current_user.id,
        )

    async def unpublish_story(
        self,
        db: AsyncSession,
        story_id: int,
        *,
        current_user: User,
    ) -> Story:
        story = await self._get_editable_story(db, story_id, current_user)
        return await crud_story.set_publication(
            db,
            story,
            status=StoryStatus.DRAFT,
            published_at=None,
            updated_by=current_user.id,
        )

    async def _get_editable_story(
        self, db: AsyncSession, story_id: int, current_user: User
    ) -> Story:
        story = await crud_story.get(db, story_id)
        if story is None:
            raise NotFoundError("Story not found")

        if current_user.role != UserRole.ADMIN and story.author_id != current_user.id:
            raise ForbiddenError()
        return story


story_service = StoryService()
