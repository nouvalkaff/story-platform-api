from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.story import StoryGenre


class StoryBase(BaseModel):
    title: str
    content: str
    genre: StoryGenre = StoryGenre.UNSPECIFIED


class StoryCreate(StoryBase):
    pass


class StoryCreateDetail(StoryCreate):
    author_id: int
    created_by: int | None
    updated_by: int | None


class StoryUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    genre: StoryGenre | None = None


class StoryResponse(StoryBase):
    id: int
    is_published: bool
    author_id: int
    published_at: datetime | None
    created_by: int
    created_at: datetime
    updated_by: int
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
