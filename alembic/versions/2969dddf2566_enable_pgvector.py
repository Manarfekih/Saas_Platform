"""enable pgvector

Revision ID: 2969dddf2566
Revises: b4e98eba4cad
Create Date: 2026-06-11 10:46:24.931321

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2969dddf2566'
down_revision: Union[str, Sequence[str], None] = 'b4e98eba4cad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute(
        "CREATE EXTENSION IF NOT EXISTS vector"
    )


def downgrade():
    op.execute(
        "DROP EXTENSION IF EXISTS vector"
    )