from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
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
    SLICE_OF_LIFE = "slice-of-life"
    ROMANCE = "romance"
    HORROR = "horror"
    MYSTERY = "mystery"
    THRILLER = "thriller"
    FANTASY = "fantasy"
    SCI_FI = "sci-fi"
    COMEDY = "comedy"
    DRAMA = "drama"
    HISTORICAL_FICTION = "historical-fiction"
    ADVENTURE = "adventure"
    FABLE = "fable"
    PSYCHOLOGICAL_FICTION = "psychological-fiction"
    SATIRE = "satire"
    SOCIAL_FICTION = "social-fiction"
    SPIRITUAL_FICTION = "spiritual-fiction"
    COMING_OF_AGE = "coming-of-age"
    SURREAL_FICTION = "surreal-fiction"
    CHILDREN_FICTION = "children-fiction"
    DYSTOPIAN_FICTION = "dystopian-fiction"


class Story(Base):
    __tablename__ = "stories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    title: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    genre: Mapped[StoryGenre] = mapped_column(
        Enum(
            StoryGenre,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        default=StoryGenre.UNSPECIFIED,
        nullable=False,
    )

    is_published: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
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

    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
