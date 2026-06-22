from sqlalchemy import (
    Column,
    Integer,
    ForeignKey
)

from app.db.database import Base


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
        nullable=False
    )