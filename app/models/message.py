from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey
)

from app.db.database import Base


class Message(Base):

    __tablename__ = "messages"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    session_id = Column(
        Integer,
        ForeignKey("chat_sessions.id"),
        nullable=False
    )


    role = Column(
        String(20),
        nullable=False
    )


    content = Column(
        Text,
        nullable=False
    )