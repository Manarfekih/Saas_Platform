import math
import re
from statistics import mean
from typing import Any

from app.evaluation.cases import EvalCase


def normalize_text(text: str | None) -> str:
    if not text:
        return ""
    return " ".join(re.findall(r"\w+", text.lower(), flags=re.UNICODE))


def average(values: list[float | None]) -> float | None:
    real_values = [value for value in values if value is not None and not math.isnan(value)]
    return mean(real_values) if real_values else None


def retrieval_metrics(case: EvalCase, retrieved: list[Any]) -> dict[str, Any]:
    retrieved_ids = [int(chunk.chunk_id) for chunk in retrieved]
    retrieved_indexes = [int(chunk.chunk_index) for chunk in retrieved]

    relevant_positions = [
        position
        for position, chunk in enumerate(retrieved, start=1)
        if _is_relevant_chunk(case, chunk)
    ]

    expected_count = (
        len(case.expected_chunk_ids)
        if case.expected_chunk_ids
        else len(case.expected_chunk_indexes)
    )

    return {
        "retrieved_chunk_ids": retrieved_ids,
        "retrieved_chunk_indexes": retrieved_indexes,
        "hit": bool(relevant_positions) if expected_count else None,
        "recall": len(relevant_positions) / expected_count if expected_count else None,
        "mrr": 1 / relevant_positions[0] if relevant_positions else 0.0,
    }


def answer_contains_score(answer: str, required_terms: list[str]) -> float | None:
    if not required_terms:
        return None

    normalized_answer = normalize_text(answer)
    matches = [
        term
        for term in required_terms
        if normalize_text(term) and normalize_text(term) in normalized_answer
    ]
    return len(matches) / len(required_terms)


def token_f1(predicted: str, expected: str | None) -> float | None:
    if not expected:
        return None

    predicted_tokens = normalize_text(predicted).split()
    expected_tokens = normalize_text(expected).split()
    if not predicted_tokens or not expected_tokens:
        return 0.0

    overlap = _token_overlap(predicted_tokens, expected_tokens)
    if overlap == 0:
        return 0.0

    precision = overlap / len(predicted_tokens)
    recall = overlap / len(expected_tokens)
    return 2 * precision * recall / (precision + recall)


def _is_relevant_chunk(case: EvalCase, chunk: Any) -> bool:
    if case.expected_chunk_ids:
        return int(chunk.chunk_id) in case.expected_chunk_ids
    return int(chunk.chunk_index) in case.expected_chunk_indexes


def _token_overlap(left: list[str], right: list[str]) -> int:
    left_counts = _counts(left)
    right_counts = _counts(right)
    return sum(min(left_counts.get(token, 0), right_counts[token]) for token in right_counts)


def _counts(tokens: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for token in tokens:
        counts[token] = counts.get(token, 0) + 1
    return counts
