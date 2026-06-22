from sqlalchemy.orm import Session
from app.models.document_chunk import DocumentChunk


def save_embedding(db: Session, chunk_id: int, vector: list[float]):

    chunk = db.query(DocumentChunk).filter(
        DocumentChunk.id == chunk_id
    ).first()

    if not chunk:
        return

    chunk.embedding = vector

    db.commit()