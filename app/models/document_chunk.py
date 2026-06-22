from sqlalchemy import Column, Integer, ForeignKey, Text, UniqueConstraint
from pgvector.sqlalchemy import Vector
from app.db.database import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    __table_args__ = (
        UniqueConstraint("document_id", "chunk_index"),
    )

    id = Column(Integer, primary_key=True, index=True)

    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)

    chunk_index = Column(Integer, nullable=False)

    content = Column(Text, nullable=False)

    embedding = Column(Vector(768), nullable=True)