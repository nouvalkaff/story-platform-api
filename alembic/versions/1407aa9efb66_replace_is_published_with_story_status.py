"""replace is published with story status

Revision ID: 1407aa9efb66
Revises: f3a7c2d8e9b1
Create Date: 2026-08-26 21:22:16.756406

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "1407aa9efb66"
down_revision: Union[str, Sequence[str], None] = "f3a7c2d8e9b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    story_status = sa.Enum("draft", "published", name="storystatus")

    story_status.create(op.get_bind())

    op.add_column("stories", sa.Column("status", story_status, nullable=True))

    op.execute("""
        UPDATE stories
        SET status = CASE
            WHEN is_published = TRUE THEN 'published'::storystatus
            ELSE 'draft'::storystatus
        END
        """)

    op.alter_column("stories", "status", nullable=False)

    op.drop_column("stories", "is_published")


def downgrade() -> None:
    op.add_column(
        "stories",
        sa.Column(
            "is_published",
            sa.Boolean(),
            nullable=True,
        ),
    )

    op.execute("""
        UPDATE stories
        SET is_published = CASE
            WHEN status = 'published' THEN TRUE
            ELSE FALSE
        END
        """)

    op.alter_column(
        "stories",
        "is_published",
        nullable=False,
    )

    op.drop_column("stories", "status")

    sa.Enum(
        "draft",
        "published",
        name="storystatus",
    ).drop(op.get_bind())
