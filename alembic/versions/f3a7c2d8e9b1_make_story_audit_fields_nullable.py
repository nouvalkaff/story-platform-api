"""make story audit fields nullable

Revision ID: f3a7c2d8e9b1
Revises: cb94d63a3899
Create Date: 2026-08-26 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "f3a7c2d8e9b1"
down_revision: Union[str, Sequence[str], None] = "cb94d63a3899"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "stories",
        "created_by",
        existing_type=sa.Integer(),
        nullable=True,
    )
    op.alter_column(
        "stories",
        "updated_by",
        existing_type=sa.Integer(),
        nullable=True,
    )


def downgrade() -> None:
    op.execute("UPDATE stories SET created_by = author_id WHERE created_by IS NULL")
    op.execute("UPDATE stories SET updated_by = author_id WHERE updated_by IS NULL")
    op.alter_column(
        "stories",
        "updated_by",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.alter_column(
        "stories",
        "created_by",
        existing_type=sa.Integer(),
        nullable=False,
    )
