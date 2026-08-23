"""Alter column created_by and updated_by allow null

Revision ID: b4740e030bed
Revises: cdec805f1496
Create Date: 2026-08-23 06:36:41.030761

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "b4740e030bed"
down_revision: Union[str, Sequence[str], None] = "cdec805f1496"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "users",
        "created_by",
        existing_type=sa.Integer(),
        nullable=True,
    )

    op.alter_column(
        "users",
        "updated_by",
        existing_type=sa.Integer(),
        nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "users",
        "updated_by",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.alter_column(
        "users",
        "created_by",
        existing_type=sa.Integer(),
        nullable=False,
    )
