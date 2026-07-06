"""add chat type to chat sessions

Revision ID: bba7f605307a
Revises: 25c5c388213d
Create Date: 2026-07-02 11:35:03.721098

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bba7f605307a'
down_revision: Union[str, Sequence[str], None] = '25c5c388213d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    chat_type = sa.Enum(
        "DOCUMENT",
        "GLOBAL",
        name="chattype",
    )

    chat_type.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "chat_sessions",
        sa.Column(
            "chat_type",
            chat_type,
            nullable=False,
            server_default="DOCUMENT",
        ),
    )

    op.alter_column(
        "chat_sessions",
        "document_id",
        existing_type=sa.INTEGER(),
        nullable=True,
    )

    op.alter_column(
        "chat_sessions",
        "chat_type",
        server_default=None,
    )

def downgrade() -> None:
    op.alter_column(
        "chat_sessions",
        "document_id",
        existing_type=sa.INTEGER(),
        nullable=False,
    )

    op.drop_column("chat_sessions", "chat_type")

    sa.Enum(
        "DOCUMENT",
        "GLOBAL",
        name="chattype",
    ).drop(op.get_bind(), checkfirst=True)