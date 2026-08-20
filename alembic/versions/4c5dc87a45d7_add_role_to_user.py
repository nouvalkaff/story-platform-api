"""add role to user

Revision ID: 4c5dc87a45d7
Revises: 224cf0a2d38e
Create Date: 2026-08-20 04:38:43.294512

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "4c5dc87a45d7"
down_revision: Union[str, Sequence[str], None] = "224cf0a2d38e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    userrole = sa.Enum("admin", "user", name="userrole")
    userrole.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "users",
        sa.Column(
            "role",
            userrole,
            server_default="user",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "role")
    sa.Enum(name="userrole").drop(op.get_bind(), checkfirst=True)
