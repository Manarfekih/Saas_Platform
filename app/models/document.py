from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from app.db.database import Base


class Document(Base):

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)

    doc_type = Column(String, nullable=True)

    extracted_text = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)

    status = Column(String, default="pending")

    processing_step = Column(String, nullable=True)

    progress = Column(Integer, default=0)

    total_chunks = Column(Integer, default=0)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )