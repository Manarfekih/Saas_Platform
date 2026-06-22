"""add document embeddings table

Revision ID: 2e700bc344a7
Revises: 2969dddf2566
Create Date: 2026-06-11 11:33:58.549101

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = '2e700bc344a7'
down_revision: Union[str, Sequence[str], None] = '2969dddf2566'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    op.create_table(
        "document_embeddings",

        sa.Column("id", sa.Integer(), primary_key=True),

        sa.Column(
            "chunk_id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "embedding",
            Vector(768),
            nullable=False
        ),

        sa.ForeignKeyConstraint(
            ["chunk_id"],
            ["document_chunks.id"],
            ondelete="CASCADE"
        )
    )


def downgrade():

    op.drop_table("document_embeddings")