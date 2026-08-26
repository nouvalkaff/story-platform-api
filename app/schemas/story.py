from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.story import StoryGenre, StoryStatus


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
    status: StoryStatus
    author_id: int
    published_at: datetime | None
    created_by: int | None
    created_at: datetime
    updated_by: int | None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StoryListResponse(StoryBase):
    status: StoryStatus
    author: str | None = None
    published_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class StoryListPagedResponse(BaseModel):
    total: int
    stories: list[StoryListResponse]
