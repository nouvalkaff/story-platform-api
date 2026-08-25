"""update story genres and make title unique

Revision ID: cb94d63a3899
Revises: 0f833cfe058d
Create Date: 2026-08-25 18:27:06.416393

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "cb94d63a3899"
down_revision: Union[str, Sequence[str], None] = "0f833cfe058d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Convert removed genres to unspecified first
    op.execute("""
        UPDATE stories
        SET genre = 'unspecified'
        WHERE genre NOT IN (
            'unspecified',
            'romance',
            'horror',
            'mystery',
            'fantasy',
            'sci-fi',
            'adventure',
            'drama'
        )
        """)

    # Rename old enum
    op.execute("ALTER TYPE storygenre RENAME TO storygenre_old")

    # Create new enum
    new_story_genre = sa.Enum(
        "unspecified",
        "romance",
        "horror",
        "mystery",
        "fantasy",
        "sci-fi",
        "adventure",
        "drama",
        name="storygenre",
    )

    new_story_genre.create(op.get_bind())

    # Change column to new enum
    op.execute("""
        ALTER TABLE stories
        ALTER COLUMN genre TYPE storygenre
        USING genre::text::storygenre
        """)

    # Remove old enum
    op.execute("DROP TYPE storygenre_old")

    # Make title unique
    op.create_unique_constraint(
        "uq_stories_title",
        "stories",
        ["title"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_stories_title",
        "stories",
        type_="unique",
    )

    op.execute("ALTER TYPE storygenre RENAME TO storygenre_new")

    old_story_genre = sa.Enum(
        "unspecified",
        "slice-of-life",
        "romance",
        "horror",
        "mystery",
        "thriller",
        "fantasy",
        "sci-fi",
        "comedy",
        "drama",
        "historical-fiction",
        "adventure",
        "fable",
        "psychological-fiction",
        "satire",
        "social-fiction",
        "spiritual-fiction",
        "coming-of-age",
        "surreal-fiction",
        "children-fiction",
        "dystopian-fiction",
        name="storygenre",
    )

    old_story_genre.create(op.get_bind())

    op.execute("""
        ALTER TABLE stories
        ALTER COLUMN genre TYPE storygenre
        USING genre::text::storygenre
        """)

    op.execute("DROP TYPE storygenre_new")
