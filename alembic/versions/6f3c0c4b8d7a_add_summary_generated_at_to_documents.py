"""add summary generated at to documents

Revision ID: 6f3c0c4b8d7a
Revises: 19c9f85a5893
Create Date: 2026-07-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f3c0c4b8d7a'
down_revision: Union[str, Sequence[str], None] = '19c9f85a5893'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'documents',
        sa.Column('summary_generated_at', sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('documents', 'summary_generated_at')
