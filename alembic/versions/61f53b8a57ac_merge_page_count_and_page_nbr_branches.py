"""Merge page_count and page_nbr branches

Revision ID: 61f53b8a57ac
Revises: 7d4a2f7a1d3c, 877a94ae9edb
Create Date: 2026-07-16 21:18:01.178671

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '61f53b8a57ac'
down_revision: Union[str, Sequence[str], None] = ('7d4a2f7a1d3c', '877a94ae9edb')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
