import re
import logging

from difflib import SequenceMatcher

from sqlalchemy.orm import Session

from app.services.embedding_service import embedding_service
from app.services.vector_search_service import (
    search_similar_chunks,
    SIMILARITY_THRESHOLD,
)

logger = logging.getLogger("saas-ia-platform")


def _normalize_text(text: str) -> str:
    return " ".join(text.split()).lower()


def _token_set(text: str) -> set[str]:
    return set(
        re.findall(
            r"\w+",
            text.lower(),
            flags=re.UNICODE,
        )
    )


def _content_similarity(
    left: str,
    right: str,
) -> float:

    normalized_left = _normalize_text(left)
    normalized_right = _normalize_text(right)

    if not normalized_left or not normalized_right:
        return 0.0

    sequence_similarity = SequenceMatcher(
        None,
        normalized_left,
        normalized_right,
    ).ratio()

    left_tokens = _token_set(normalized_left)
    right_tokens = _token_set(normalized_right)

    if left_tokens and right_tokens:

        jaccard_similarity = (
            len(left_tokens & right_tokens)
            / len(left_tokens | right_tokens)
        )

    else:
        jaccard_similarity = 0.0

    return max(
        sequence_similarity,
        jaccard_similarity,
    )


def _deduplicate_results(results: list):

    seen_contents = set()

    deduplicated = []

    for result in results:

        content_key = _normalize_text(
            result.content
        )

        if content_key in seen_contents:
            continue

        seen_contents.add(content_key)

        deduplicated.append(result)

    return deduplicated


def _rerank_with_mmr(
    results: list,
    limit: int,
    lambda_mult: float = 0.75,
):

    if not results:
        return []

    if len(results) <= limit:
        return results

    selected = [results[0]]

    remaining = results[1:]

    while (
        remaining
        and len(selected) < limit
    ):

        best_index = 0

        best_score = float("-inf")

        for index, candidate in enumerate(
            remaining
        ):

            relevance = max(
                0.0,
                1.0 - float(candidate.distance),
            )

            redundancy = max(
                _content_similarity(
                    candidate.content,
                    chosen.content,
                )
                for chosen in selected
            )

            score = (
                lambda_mult * relevance
            ) - (
                (1.0 - lambda_mult)
                * redundancy
            )

            if score > best_score:

                best_score = score

                best_index = index

        selected.append(
            remaining.pop(best_index)
        )

    return selected


def retrieve_chunks(
    db: Session,
    document_id: int,
    query: str,
    limit: int = 5,
    similarity_threshold: float = SIMILARITY_THRESHOLD,
):
    """
    Complete retrieval pipeline.
    """

    logger.info(
        f"Retrieving chunks for document={document_id}"
    )

    query_embedding = embedding_service.embed(
        query
    )

    candidate_limit = max(
        limit * 5,
        20,
    )

    results = search_similar_chunks(
        db=db,
        document_id=document_id,
        query_embedding=query_embedding,
        limit=candidate_limit,
        similarity_threshold=similarity_threshold,
    )

    results = _deduplicate_results(
        results
    )

    results = _rerank_with_mmr(
        results,
        limit,
    )

    logger.info(
        f"Retrieved {len(results)} chunks"
    )

    return results