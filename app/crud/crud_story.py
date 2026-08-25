from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.story import Story, StoryGenre
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

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 20,
        title: str | None = None,
        genre: StoryGenre | None = None,
        is_published: bool | None = None,
        author_id: int | None = None,
    ) -> list[Story]:
        statement = select(Story)

        if title is not None:
            statement = statement.where(Story.title.ilike(f"%{title}%"))
        if genre is not None:
            statement = statement.where(Story.genre == genre)
        if is_published is not None:
            statement = statement.where(Story.is_published == is_published)
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
        is_published: bool,
        published_at: datetime | None,
        updated_by: int,
    ) -> Story:
        story.is_published = is_published
        story.published_at = published_at
        story.updated_by = updated_by
        await db.commit()
        await db.refresh(story)
        return story

    async def delete(self, db: AsyncSession, story: Story) -> None:
        await db.delete(story)
        await db.commit()


crud_story = CRUDStory()
