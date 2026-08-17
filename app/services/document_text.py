from __future__ import annotations

import re
from typing import Iterable

from app.services.chunking_service import _clean_extracted_text

_PAGE_SPLIT_PATTERN = re.compile(
    r"(?:\n\s*\n)|(?:^\[\[PAGE\s+\d+\]\]$)|(?:^---\s*PAGES?\s*\d+(?:[-\u2013]\d+)?\s*---$)",
    flags=re.IGNORECASE | re.MULTILINE,
)


def clean_document_text(text: str | None) -> str:
    if not text:
        return ""
    return _clean_extracted_text(text).strip()


def _split_blocks(text: str) -> list[str]:
    raw_blocks = [block.strip() for block in _PAGE_SPLIT_PATTERN.split(text) if block and block.strip()]
    if raw_blocks:
        return raw_blocks
    return [text.strip()] if text.strip() else []


def _sample_block(block: str, budget: int) -> str:
    block = block.strip()
    if not block or budget <= 0:
        return ""

    if len(block) <= budget:
        return block

    if budget <= 120:
        return block[:budget].strip()

    head_budget = max(60, budget // 2)
    tail_budget = max(60, budget - head_budget - 5)
    if head_budget + tail_budget + 5 > budget:
        tail_budget = max(40, budget - head_budget - 5)

    head = block[:head_budget].rstrip()
    tail = block[-tail_budget:].lstrip()
    return f"{head}\n...\n{tail}".strip()


def build_coverage_excerpt(text: str | None, max_chars: int) -> str:
    cleaned = clean_document_text(text)
    if not cleaned:
        return ""

    if len(cleaned) <= max_chars:
        return cleaned

    blocks = _split_blocks(cleaned)
    if len(blocks) <= 1:
        return _sample_block(cleaned, max_chars)

    excerpts: list[str] = []
    remaining = max_chars

    for index, block in enumerate(blocks):
        slots_left = len(blocks) - index
        if remaining <= 0:
            break

        share = max(180, remaining // slots_left)
        excerpt = _sample_block(block, share)
        if not excerpt:
            continue

        if len(excerpt) > remaining:
            excerpt = excerpt[:remaining].rstrip()

        excerpts.append(excerpt)
        remaining -= len(excerpt)

    combined = "\n\n".join(excerpts).strip()
    if not combined:
        return _sample_block(cleaned, max_chars)

    if len(combined) <= max_chars:
        return combined

    return combined[:max_chars].rstrip()
