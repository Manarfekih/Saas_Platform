from __future__ import annotations

from typing import Any

from app.services.classification.constants import CATEGORY_SETS, GENERIC_CATEGORIES


def _categories_for(doc_type: str | None):
    if not doc_type:
        return GENERIC_CATEGORIES
    return CATEGORY_SETS.get(doc_type.lower(), GENERIC_CATEGORIES)


def render_classified_block(items: list[dict[str, Any]], doc_type: str | None = None):
    if not items:
        return ""

    categories = _categories_for(doc_type)
    by_category: dict[str, list[dict[str, Any]]] = {}

    for item in items:
        by_category.setdefault(item["category"], []).append(item)

    blocks: list[str] = []

    for category in categories:
        category_items = by_category.get(category)
        if not category_items:
            continue

        blocks.append(f"## {category}")

        for item in category_items:
            line = f"- {item['title']}"

            if item.get("organization"):
                line += f" ({item['organization']})"

            if item.get("amount"):
                line += f" - {item['amount']}"

            if item.get("dates"):
                line += f" - {item['dates']}"

            blocks.append(line)

            if item.get("details"):
                blocks.append(f"  {item['details']}")

    return "\n".join(blocks)
