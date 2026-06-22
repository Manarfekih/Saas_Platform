"""remove document_embeddings

Revision ID: cdbb52e65c3e
Revises: 2e700bc344a7
Create Date: 2026-06-13 23:59:21.860200

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cdbb52e65c3e'
down_revision: Union[str, Sequence[str], None] = '2e700bc344a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("document_embeddings")


def downgrade() -> None:
    """Downgrade schema."""
    pass
