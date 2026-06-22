from sqlalchemy.orm import Session
from app.models.document_chunk import DocumentChunk
from app.core.logger import logger


def save_chunks(db: Session, document_id: int, chunks: list[str]):
    
    
    try:
        # STEP 1: Delete old chunks for this document
        deleted_count = db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document_id
        ).delete(synchronize_session="fetch")
        
        logger.info(f"Deleted {deleted_count} old chunks for document {document_id}")
        
        # STEP 2: Commit deletion immediately to prevent race conditions
        db.commit()
        
        # STEP 3: Insert new chunks
        db_chunks = []
        
        for index, chunk in enumerate(chunks):
            db_chunk = DocumentChunk(
                document_id=document_id,
                chunk_index=index,
                content=chunk,
                embedding=None
            )
            db.add(db_chunk)
            db_chunks.append(db_chunk)
        
        # STEP 4: Commit new chunks
        db.commit()
        
        # Refresh all chunks to get their IDs
        for chunk in db_chunks:
            db.refresh(chunk)
        
        logger.info(f"Saved {len(db_chunks)} new chunks for document {document_id}")
        
        return db_chunks
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving chunks for document {document_id}: {str(e)}", exc_info=True)
        raise