from sqlalchemy.orm import Session
from app.models.document_chunk import DocumentChunk
import logging
from app.models.document import Document

logger = logging.getLogger("saas-ia-platform")
SIMILARITY_THRESHOLD = 0.7

def search_similar_chunks(
    db: Session,
    query_embedding: list[float],
    document_id: int,
    limit: int = 5,
    similarity_threshold: float = SIMILARITY_THRESHOLD,
):
    try:
        logger.info(f"Searching document={document_id} threshold={similarity_threshold}")
        
        if all(v == 0 for v in query_embedding):
            logger.warning("Query embedding is zero vector, returning empty results")
            return []
        
        all_chunks = (
            db.query(
                DocumentChunk.id.label("chunk_id"),
                DocumentChunk.document_id.label("document_id"),
                DocumentChunk.chunk_index.label("chunk_index"),
                DocumentChunk.page_number.label("page_number"),
                DocumentChunk.content,
                DocumentChunk.embedding.cosine_distance(query_embedding).label("distance"),
            )
            .filter(DocumentChunk.document_id == document_id)
            .filter(DocumentChunk.embedding.isnot(None))
            .all()
        )
        
        filtered_results = []
        for chunk in all_chunks:
            if chunk.distance <= similarity_threshold:
                filtered_results.append(chunk)
        
        filtered_results.sort(key=lambda x: x.distance)
        results = filtered_results[:limit]
        
        logger.info(f"Found {len(results)} chunks (filtered from {len(all_chunks)})")
        
        if not results and all_chunks:
            logger.info("No results with strict threshold, returning top chunks without threshold")
            all_chunks.sort(key=lambda x: x.distance)
            results = all_chunks[:limit]
            logger.info(f"Returning {len(results)} chunks without threshold filtering")
        
        return results
    
    except Exception as e:
        logger.error(f"Vector search error: {str(e)}", exc_info=True)
        raise


def search_similar_chunks_all_documents(
    db: Session,
    query_embedding: list[float],
    user_id: int,
    limit: int = 10,
    similarity_threshold: float = SIMILARITY_THRESHOLD,
):
   

    try:

        logger.info(
            f"Searching ALL documents for user={user_id}"
        )

        if all(v == 0 for v in query_embedding):
            logger.warning("Query embedding is zero vector")
            return []

        results = (
            db.query(
                DocumentChunk.id.label("chunk_id"),
                DocumentChunk.document_id.label("document_id"),
                DocumentChunk.chunk_index.label("chunk_index"),
                DocumentChunk.page_number.label("page_number"),
                DocumentChunk.content,
                DocumentChunk.embedding.cosine_distance(query_embedding).label(
                    "distance"
                ),
            )
            .join(
                Document,
                Document.id == DocumentChunk.document_id,
            )
            .filter(Document.user_id == user_id)
            .filter(Document.status == "processed")
            .filter(DocumentChunk.embedding.isnot(None))
            .all()
        )

        filtered = [
            chunk
            for chunk in results
            if chunk.distance <= similarity_threshold
        ]

        filtered.sort(key=lambda x: x.distance)

        if filtered:
            return filtered[:limit]

        logger.info(
            "No chunks passed threshold, returning best matches."
        )

        results.sort(key=lambda x: x.distance)

        return results[:limit]

    except Exception as e:
        logger.error(str(e), exc_info=True)
        raise


