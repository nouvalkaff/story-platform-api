"""Refactor story tags from delimited text to PostgreSQL array.

Revision ID: ea91c0d7b264
Revises: c8e25e916dd4
Create Date: 2026-08-27 02:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "ea91c0d7b264"
down_revision: Union[str, Sequence[str], None] = "c8e25e916dd4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "stories",
        sa.Column(
            "tags_array",
            postgresql.ARRAY(sa.String()),
            nullable=False,
            server_default=sa.text("'{}'::character varying[]"),
        ),
    )
    op.execute("""
        UPDATE stories
        SET tags_array = CASE
            WHEN tags IS NULL OR btrim(tags) = '' THEN ARRAY[]::character varying[]
            ELSE ARRAY(
                SELECT btrim(tag.value)
                FROM unnest(string_to_array(tags, ';')) AS tag(value)
                WHERE btrim(tag.value) <> ''
            )
        END
        """)
    op.drop_column("stories", "tags")
    op.alter_column(
        "stories",
        "tags_array",
        new_column_name="tags",
        existing_type=postgresql.ARRAY(sa.String()),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.add_column(
        "stories", sa.Column("tags_text", sa.String(length=200), nullable=True)
    )
    op.execute("""
        UPDATE stories
        SET tags_text = NULLIF(array_to_string(tags, ';'), '')
        """)
    op.drop_column("stories", "tags")
    op.alter_column(
        "stories",
        "tags_text",
        new_column_name="tags",
        existing_type=sa.String(length=200),
        existing_nullable=True,
    )
