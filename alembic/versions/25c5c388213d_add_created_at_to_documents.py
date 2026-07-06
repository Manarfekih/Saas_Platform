"""add created_at to documents

Revision ID: 25c5c388213d
Revises: d205b8d64aa6
Create Date: 2026-06-28 01:07:18.293683

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '25c5c388213d'
down_revision: Union[str, Sequence[str], None] = 'd205b8d64aa6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "documents",
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("documents", "created_at")