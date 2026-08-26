from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class StoryGenre(str, PyEnum):
    UNSPECIFIED = "unspecified"
    ROMANCE = "romance"
    HORROR = "horror"
    MYSTERY = "mystery"
    FANTASY = "fantasy"
    SCI_FI = "sci-fi"
    ADVENTURE = "adventure"
    DRAMA = "drama"


class StoryStatus(str, PyEnum):
    DRAFT = "draft"
    PUBLISHED = "published"


class Story(Base):
    __tablename__ = "stories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    title: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    synopsis: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    genre: Mapped[StoryGenre] = mapped_column(
        Enum(
            StoryGenre,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        default=StoryGenre.UNSPECIFIED,
        nullable=False,
    )

    tags: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    status: Mapped[StoryStatus] = mapped_column(
        Enum(StoryStatus, values_callable=lambda obj: [e.value for e in obj]),
        default=StoryStatus.DRAFT,
        nullable=False,
    )

    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
