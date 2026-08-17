import logging
import re
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.services.embedding_service import embedding_service
from app.services.retrieval_service import (
    retrieve_chunks,
    _deduplicate_results,
    _rerank_with_mmr,
)
from app.services.vector_search_service import (
    search_similar_chunks,
    SIMILARITY_THRESHOLD,
)
from app.models.document_chunk import DocumentChunk

logger = logging.getLogger("saas-ia-platform")


@dataclass(slots=True)
class ToolChunkResult:
    chunk_id: int
    document_id: int
    chunk_index: int
    page_number: int | None
    content: str
    distance: float


def _build_result(chunk, distance: float) -> ToolChunkResult:
    return ToolChunkResult(
        chunk_id=chunk.id,
        document_id=chunk.document_id,
        chunk_index=chunk.chunk_index,
        page_number=getattr(chunk, "page_number", None),
        content=chunk.content,
        distance=distance,
    )


# TOOL 1: general semantic search

def tool_search_chunks(
    db: Session,
    document_id: int,
    query: str,
    limit: int = 8,
    similarity_threshold: float = SIMILARITY_THRESHOLD,
) -> list:
    logger.info(
        f"[tool_search_chunks] doc={document_id} "
        f"query={query!r} limit={limit}"
    )

    return retrieve_chunks(
        db=db,
        document_id=document_id,
        query=query,
        limit=limit,
        similarity_threshold=similarity_threshold,
    )


# TOOL 2: section-targeted retrieval

def tool_search_section(
    db: Session,
    document_id: int,
    section_name: str,
    limit: int = 8,
) -> list:
    logger.info(
        f"[tool_search_section] doc={document_id} "
        f"section={section_name!r}"
    )

    query_embedding = embedding_service.embed(section_name)
    candidate_limit = max(limit * 3, 12)

    results = search_similar_chunks(
        db=db,
        document_id=document_id,
        query_embedding=query_embedding,
        limit=candidate_limit,
        similarity_threshold=0.9,
    )

    pattern = re.compile(re.escape(section_name), flags=re.IGNORECASE)

    all_chunks = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document_id)
        .filter(DocumentChunk.embedding.isnot(None))
        .all()
    )

    text_matches = [
        _build_result(c, distance=0.3)
        for c in all_chunks
        if pattern.search(c.content or "")
    ]

    seen_ids = {r.chunk_id for r in results}
    for match in text_matches:
        if match.chunk_id not in seen_ids:
            results.append(match)
            seen_ids.add(match.chunk_id)

    results = _deduplicate_results(results)
    results = _rerank_with_mmr(results, limit)

    logger.info(f"[tool_search_section] returned {len(results)} chunks")

    return results


# TOOL 3: get all chunks (overview / full-document summarization)

def tool_get_all_chunks(
    db: Session,
    document_id: int,
    limit: int = 20,
) -> list:
    logger.info(
        f"[tool_get_all_chunks] doc={document_id} limit={limit}"
    )

    chunks = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document_id)
        .filter(DocumentChunk.embedding.isnot(None))
        .order_by(DocumentChunk.chunk_index)
        .limit(limit)
        .all()
    )

    results = [_build_result(c, distance=0.0) for c in chunks]

    logger.info(f"[tool_get_all_chunks] returned {len(results)} chunks")

    return results


# TOOL 4: count / retrieve by classification category

def tool_count_category(
    db: Session,
    document_id: int,
    category: str,
    limit: int = 20,
) -> list:
    logger.info(
        f"[tool_count_category] doc={document_id} "
        f"category={category!r}"
    )

    return tool_search_section(
        db=db,
        document_id=document_id,
        section_name=f"## {category}",
        limit=limit,
    )


def execute_tool(plan: dict, db: Session, document_id: int) -> list:
    tool_name = plan.get("tool", "search_chunks")
    params = plan.get("params", {})

    logger.info(f"Executing tool={tool_name} params={params}")

    if tool_name == "search_chunks":
        return tool_search_chunks(
            db=db,
            document_id=document_id,
            query=params.get("query", ""),
            limit=params.get("limit", 8),
        )
    if tool_name == "search_section":
        return tool_search_section(
            db=db,
            document_id=document_id,
            section_name=params.get("section_name", ""),
            limit=params.get("limit", 8),
        )
    if tool_name == "get_all_chunks":
        return tool_get_all_chunks(
            db=db,
            document_id=document_id,
            limit=params.get("limit", 20),
        )
    if tool_name == "count_category":
        return tool_count_category(
            db=db,
            document_id=document_id,
            category=params.get("category", ""),
            limit=params.get("limit", 20),
        )

    logger.warning(f"Unknown tool: {tool_name!r}, falling back to search_chunks")
    return tool_search_chunks(
        db=db,
        document_id=document_id,
        query=params.get("query", ""),
        limit=8,
    )
