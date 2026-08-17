from datetime import datetime

from sqlalchemy import JSON, Column, Integer, String, ForeignKey, Text, DateTime
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

    summary = Column(JSON, nullable=True)

    summary_file_path = Column(String(512), nullable=True)
    summary_file_name = Column(String(255), nullable=True)
    
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )





