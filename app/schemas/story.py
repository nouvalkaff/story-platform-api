from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.story import StoryGenre, StoryStatus

MAX_TAGS = 10
MAX_TAGS_SERIALIZED_LENGTH = 200


def _normalize_tags(value: Any) -> list[str]:
    if value is None:
        return []

    if not isinstance(value, list):
        raise TypeError("tags must be an array of strings")

    normalized_tags: list[str] = []

    for tag in value:
        if not isinstance(tag, str):
            raise TypeError("each tag must be a string")

        normalized_tag = tag.strip()

        if not normalized_tag:
            continue

        if ";" in normalized_tag:
            raise ValueError("tags cannot contain semicolons")

        normalized_tags.append(normalized_tag)

    serialized_length = sum(map(len, normalized_tags)) + max(
        len(normalized_tags) - 1, 0
    )

    if serialized_length > MAX_TAGS_SERIALIZED_LENGTH:
        raise ValueError(
            f"combined tags length must not exceed {MAX_TAGS_SERIALIZED_LENGTH} characters"
        )

    return normalized_tags


class StoryBase(BaseModel):
    title: str
    content: str = Field(min_length=1, max_length=20_000)
    synopsis: str | None = Field(default=None, max_length=500)
    genre: StoryGenre = StoryGenre.UNSPECIFIED
    tags: list[str] = Field(default_factory=list)

    @field_validator("tags", mode="before")
    @classmethod
    def normalize_tags(cls, value: Any) -> list[str]:
        return _normalize_tags(value)


class StoryCreate(StoryBase):
    pass


class StoryCreateDetail(StoryCreate):
    author_id: int
    created_by: int | None
    updated_by: int | None


class StoryUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = None
    content: str | None = Field(default=None, min_length=1, max_length=20_000)
    synopsis: str | None = Field(default=None, max_length=500)
    genre: StoryGenre | None = None
    tags: list[str] | None = None

    @field_validator("tags", mode="before")
    @classmethod
    def normalize_tags(cls, value: Any) -> list[str]:
        return _normalize_tags(value)


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
