from __future__ import annotations

import json
import logging

from app.services.classification.constants import CLASSIFICATION_PROMPT
from app.services.classification.rendering import _categories_for
from app.services.document_text import build_coverage_excerpt
from app.services.llm_service import ask_llm

logger = logging.getLogger("saas-ia-platform")


def _clean_llm_json_response(response: str) -> str:
    cleaned = response.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()
    return cleaned


def classify_sections(raw_text: str, doc_type: str | None = None):
    categories = _categories_for(doc_type)
    coverage_text = build_coverage_excerpt(raw_text, 12000)

    prompt = CLASSIFICATION_PROMPT.format(
        doc_type=doc_type or "unknown",
        categories=", ".join(categories),
        text=coverage_text,
    )

    try:
        response = ask_llm(prompt)
    except Exception as exc:
        logger.error("Classification LLM call failed: %s", exc)
        return []

    cleaned = _clean_llm_json_response(response)

    try:
        items = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        logger.error(
            "Classification JSON parse failed: %s | raw_response=%r",
            exc,
            cleaned[:300],
        )
        return []

    if not isinstance(items, list):
        logger.error("Classification did not return a list: %s", type(items))
        return []

    valid_items = []
    for item in items:
        if not isinstance(item, dict):
            continue

        category = item.get("category")
        if category not in categories:
            logger.warning(
                "Unexpected category %r for doc_type=%r, coercing to 'other'",
                category,
                doc_type,
            )
            item["category"] = "other"

        if not item.get("title"):
            continue

        valid_items.append(item)

    logger.info(
        "Classification (doc_type=%s) produced %s valid items out of %s raw items",
        doc_type,
        len(valid_items),
        len(items),
    )

    return valid_items
