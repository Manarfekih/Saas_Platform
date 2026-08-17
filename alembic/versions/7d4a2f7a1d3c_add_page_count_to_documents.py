"""add page_count to documents

Revision ID: 7d4a2f7a1d3c
Revises: 25c5c388213d
Create Date: 2026-07-14 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7d4a2f7a1d3c'
down_revision: Union[str, Sequence[str], None] = '25c5c388213d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('documents', sa.Column('page_count', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('documents', 'page_count')
