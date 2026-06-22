from sqlalchemy.orm import Session
from app.models.document_chunk import DocumentChunk
import logging

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

        logger.info(
            f"Searching document={document_id} "
            f"threshold={similarity_threshold}"
        )

        results = (
            db.query(
                DocumentChunk.id.label("chunk_id"),
                DocumentChunk.document_id.label("document_id"),
                DocumentChunk.chunk_index.label("chunk_index"),
                DocumentChunk.content,
                DocumentChunk.embedding.cosine_distance(
                    query_embedding
                ).label("distance"),
            )
            .filter(
                DocumentChunk.document_id == document_id
            )
            .filter(
                DocumentChunk.embedding.isnot(None)
            )
            .filter(
                DocumentChunk.embedding.cosine_distance(
                    query_embedding
                ) <= similarity_threshold
            )
            .order_by(
                DocumentChunk.embedding.cosine_distance(
                    query_embedding
                )
            )
            .limit(limit)
            .all()
        )

        logger.info(
            f"Found {len(results)} chunks"
        )

        return results

    except Exception as e:
        logger.error(
            f"Vector search error: {str(e)}",
            exc_info=True
        )
        raise