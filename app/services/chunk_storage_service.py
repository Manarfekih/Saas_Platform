from sqlalchemy.orm import Session
from app.models.document_chunk import DocumentChunk
from app.core.logger import logger


def save_chunks(
    db: Session,
    document_id: int,
    chunks: list[tuple[str, int | None]],
) -> list[DocumentChunk]:
    

    try:
        # old chunks
        deleted_count = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document_id)
            .delete(synchronize_session="fetch")
        )
        logger.info(f"Deleted {deleted_count} old chunks for document {document_id}")
        db.commit()

        # new chunks

        db_chunks = []
        for index, (content, page_number) in enumerate(chunks):
            db_chunk = DocumentChunk(
                document_id=document_id,
                chunk_index=index,
                page_number=page_number,
                content=content,
                embedding=None,
            )
            db.add(db_chunk)
            db_chunks.append(db_chunk)

        db.commit()

        for chunk in db_chunks:
            db.refresh(chunk)

        logger.info(
            f"Saved {len(db_chunks)} chunks for document {document_id} "
            f"(pages: {sorted({c.page_number for c in db_chunks if c.page_number})})"
        )
        return db_chunks

    except Exception as e:
        db.rollback()
        logger.error(
            f"Error saving chunks for document {document_id}: {str(e)}",
            exc_info=True,
        )
        raise