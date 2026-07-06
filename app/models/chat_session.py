from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Enum as SqlEnum,
)

from app.db.database import Base
from app.models.chat_type import ChatType


class ChatSession(Base):

    __tablename__ = "chat_sessions"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )


    document_id = Column(
        Integer,
        ForeignKey("documents.id"),
        nullable=True,
    )

    chat_type = Column(
        SqlEnum(ChatType),
        nullable=False,
        default=ChatType.DOCUMENT,
    )