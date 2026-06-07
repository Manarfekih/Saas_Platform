from sqlalchemy import Column, Integer, String, ForeignKey, Text
from app.db.database import Base


class Document(Base):

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    filename = Column(String)
    file_path = Column(String)

    doc_type = Column(String, nullable=True)

    extracted_text = Column(Text, nullable=True)

    status = Column(String, default="pending")