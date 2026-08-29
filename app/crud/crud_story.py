from datetime import datetime
from typing import Any, cast

from sqlalchemy import Row, delete, func, select, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.story import Story, StoryGenre, StoryStatus
from app.schemas.story import StoryCreateDetail, StoryUpdate


class CRUDStory:
    async def create(self, db: AsyncSession, story_data: StoryCreateDetail) -> Story:
        story = Story(**story_data.model_dump())

        db.add(story)

        await db.commit()

        await db.refresh(story)

        return story

    async def get(self, db: AsyncSession, story_id: int) -> Story | None:
        result = await db.execute(select(Story).where(Story.id == story_id))
        return result.scalar_one_or_none()

    async def get_by_id(self, db: AsyncSession, story_id: int) -> Story | None:
        result = await db.execute(select(Story).where(Story.id == story_id))
        return result.scalar_one_or_none()

    async def get_story_by_title(self, db: AsyncSession, title: str) -> Story | None:
        result = await db.execute(select(Story).where(Story.title == title))
        return result.scalar_one_or_none()

    async def get_stories_by_user_id(
        self,
        db: AsyncSession,
        user_id: int,
        *,
        status: StoryStatus | None = None,
        page: int = 1,
        page_limit: int = 20,
    ) -> tuple[list[Story], int]:
        statement = select(Story).where(Story.author_id == user_id)

        if status is not None:
            statement = statement.where(Story.status == status)

        # count total before pagination
        count_statement = select(func.count()).select_from(statement.subquery())

        total_result = await db.execute(count_statement)

        total = total_result.scalar_one()

        # apply pagination
        statement = statement.order_by(Story.created_at.desc())

        statement = statement.offset((page - 1) * page_limit).limit(page_limit)

        result = await db.execute(statement)

        return list(result.scalars().all()), total

    async def get_published_stories(
        self,
        db: AsyncSession,
        *,
        skip: int,
        limit: int,
        q: str | None = None,
    ) -> tuple[list[Story], int]:
        statement = select(Story).where(Story.status == StoryStatus.PUBLISHED)

        if q is not None:
            search_term = f"%{q}%"
            statement = statement.where(Story.title.ilike(search_term))

        count_statement = select(func.count()).select_from(statement.subquery())

        total_result = await db.execute(count_statement)

        total = total_result.scalar_one()

        statement = statement.order_by(Story.published_at.desc(), Story.id.desc())

        statement = statement.offset(skip).limit(limit)

        result = await db.execute(statement)

        return list(result.scalars().all()), total

    async def count_by_author(self, db: AsyncSession, author_id: int) -> int:
        statement = (
            select(func.count()).select_from(Story).where(Story.author_id == author_id)
        )
        result = await db.execute(statement)
        return result.scalar_one()

    async def get_by_title(
        self, db: AsyncSession, title: str
    ) -> Row[tuple[int, str]] | None:
        result = await db.execute(
            select(Story.id, Story.title).where(Story.title == title)
        )
        return result.one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 20,
        title: str | None = None,
        genre: StoryGenre | None = None,
        status: StoryStatus | None = None,
        author_id: int | None = None,
    ) -> list[Story]:
        statement = select(Story)

        if title is not None:
            statement = statement.where(Story.title.ilike(f"%{title}%"))
        if genre is not None:
            statement = statement.where(Story.genre == genre)
        if status is not None:
            statement = statement.where(Story.status == status)
        if author_id is not None:
            statement = statement.where(Story.author_id == author_id)

        statement = statement.order_by(Story.created_at.desc(), Story.id.desc())
        statement = statement.offset(skip).limit(limit)
        result = await db.execute(statement)
        return list(result.scalars().all())

    async def update(
        self,
        db: AsyncSession,
        story: Story,
        update_data: StoryUpdate,
        *,
        updated_by: int,
    ) -> Story:
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(story, field, value)

        story.updated_by = updated_by
        await db.commit()
        await db.refresh(story)
        return story

    async def set_publication(
        self,
        db: AsyncSession,
        story: Story,
        *,
        status: StoryStatus,
        published_at: datetime | None,
        updated_by: int,
    ) -> Story:
        story.status = status
        story.published_at = published_at
        story.updated_by = updated_by
        await db.commit()
        await db.refresh(story)
        return story

    async def delete(self, db: AsyncSession, story: Story) -> None:
        await db.delete(story)
        await db.commit()

    async def delete_by_author(
        self,
        db: AsyncSession,
        author_id: int,
        *,
        commit: bool = True,
    ) -> int:
        statement = delete(Story).where(Story.author_id == author_id)
        result = cast(CursorResult[Any], await db.execute(statement))
        if commit:
            await db.commit()
        return result.rowcount or 0

    async def clear_audit_references(
        self,
        db: AsyncSession,
        user_id: int,
        *,
        commit: bool = True,
    ) -> None:
        await db.execute(
            update(Story).where(Story.created_by == user_id).values(created_by=None)
        )

        await db.execute(
            update(Story).where(Story.updated_by == user_id).values(updated_by=None)
        )

        if commit:
            await db.commit()


crud_story = CRUDStory()
