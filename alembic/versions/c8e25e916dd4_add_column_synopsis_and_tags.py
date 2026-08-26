"""Add column synopsis and tags

Revision ID: c8e25e916dd4
Revises: 1407aa9efb66
Create Date: 2026-08-27 00:18:23.270563

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "c8e25e916dd4"
down_revision: Union[str, Sequence[str], None] = "1407aa9efb66"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "stories", sa.Column("synopsis", sa.String(length=500), nullable=True)
    )
    op.add_column("stories", sa.Column("tags", sa.String(length=200), nullable=True))


def downgrade() -> None:
    op.drop_column("stories", "tags")
    op.drop_column("stories", "synopsis")
