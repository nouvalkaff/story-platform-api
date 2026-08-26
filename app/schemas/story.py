from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.story import StoryGenre, StoryStatus


class StoryBase(BaseModel):
    title: str
    content: str = Field(min_length=1, max_length=20_000)
    synopsis: str | None = Field(default=None, max_length=500)
    genre: StoryGenre = StoryGenre.UNSPECIFIED
    tags: str | None = Field(default=None, max_length=200)


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


class StoryStatusUpdate(BaseModel):
    status: StoryStatus


class StoryStatusResponse(BaseModel):
    id: int
    title: str
    status: StoryStatus
    published_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


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


class AllStoryListResponse(StoryBase):
    status: StoryStatus
    published_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class StoryListResponse(AllStoryListResponse):
    author: str | None = None

    model_config = ConfigDict(from_attributes=True)


class StoryListPagedResponse(BaseModel):
    total: int
    stories: list[StoryListResponse]


class PublishedStoryPagedResponse(BaseModel):
    total: int
    page: int
    size: int
    stories: list[AllStoryListResponse]
