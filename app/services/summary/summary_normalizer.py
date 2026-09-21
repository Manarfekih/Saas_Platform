from datetime import datetime
from typing import Any, Dict, List, Optional

from app.services.summary.summary_cleaning import (
    clean_overview,
    clean_text_value,
    coerce_list,
    extract_title,
    is_noise_title,
)


def build_statistics(
    text: str,
    sections: List[Dict[str, Any]],
    page_count: Optional[int] = None,
) -> Dict[str, Any]:
    return {
        "total_pages": page_count or 0,
        "generated_at": datetime.utcnow().isoformat(),
    }


def merge_summary(base: Dict[str, Any], extra: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(base or {})
    extra = extra or {}

    _merge_scalar_fields(merged, extra)
    merged["key_information"] = _merge_key_information(base, extra)
    merged["sections"] = _merge_sections(
        list(base.get("sections", [])) if isinstance(base, dict) else [],
        list(extra.get("sections", [])) if isinstance(extra, dict) else [],
    )
    _merge_statistics(merged, base, extra)
    return merged


def normalize_summary(
    summary: Dict[str, Any],
    text: str | None = None,
    page_count: Optional[int] = None,
) -> Dict[str, Any]:
    normalized = dict(summary or {})

    title = clean_text_value(normalized.get("title"))
    normalized["title"] = extract_title(text) if is_noise_title(title) else title
    normalized["title"] = normalized["title"] or "Document Summary"

    normalized["document_type"] = (
        clean_text_value(normalized.get("document_type")) or "Document"
    )
    normalized["overview"] = clean_overview(str(normalized.get("overview") or ""))
    normalized["key_information"] = _normalize_key_information(
        normalized.get("key_information") or {}
    )
    normalized["sections"] = _normalize_sections(normalized.get("sections", []))
    normalized["statistics"] = build_statistics(
        text or "",
        normalized["sections"],
        page_count=page_count,
    )
    return normalized


def _merge_scalar_fields(merged: Dict[str, Any], extra: Dict[str, Any]) -> None:
    extra_title = clean_text_value(extra.get("title"))
    if extra_title and not is_noise_title(extra_title):
        merged["title"] = extra_title

    extra_type = clean_text_value(extra.get("document_type"))
    if extra_type:
        merged["document_type"] = extra_type

    extra_overview = extra.get("overview")
    if isinstance(extra_overview, str) and extra_overview.strip():
        merged["overview"] = extra_overview.strip()


def _merge_key_information(
    base: Dict[str, Any],
    extra: Dict[str, Any],
) -> Dict[str, list[str]]:
    base_info = base.get("key_information", {}) if isinstance(base, dict) else {}
    extra_info = extra.get("key_information", {}) if isinstance(extra, dict) else {}
    return {
        "people": _merge_unique_lists(
            coerce_list(base_info.get("people")),
            coerce_list(extra_info.get("people")),
        ),
        "organizations": _merge_unique_lists(
            coerce_list(base_info.get("organizations")),
            coerce_list(extra_info.get("organizations")),
        ),
        "dates": _merge_unique_lists(
            coerce_list(base_info.get("dates")),
            coerce_list(extra_info.get("dates")),
        ),
        "amounts": _merge_unique_lists(
            coerce_list(base_info.get("amounts")),
            coerce_list(extra_info.get("amounts")),
        ),
    }


def _normalize_key_information(value: Dict[str, Any]) -> Dict[str, list[str]]:
    return {
        "people": coerce_list(value.get("people")),
        "organizations": coerce_list(value.get("organizations")),
        "dates": coerce_list(value.get("dates")),
        "amounts": coerce_list(value.get("amounts")),
    }


def _merge_unique_lists(base: List[str], extra: List[str]) -> List[str]:
    merged: List[str] = []
    seen = set()
    for item in base + extra:
        cleaned = str(item).strip()
        if cleaned and cleaned.lower() not in seen:
            seen.add(cleaned.lower())
            merged.append(cleaned)
    return merged


def _merge_sections(
    base_sections: List[Dict[str, Any]],
    extra_sections: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    index_by_title: dict[str, int] = {}

    for section in base_sections + extra_sections:
        if isinstance(section, dict):
            _add_section(merged, index_by_title, section)

    return merged


def _add_section(
    merged: list[dict[str, Any]],
    index_by_title: dict[str, int],
    section: Dict[str, Any],
) -> None:
    title = clean_text_value(section.get("title", ""))
    items = _normalize_section_items(section.get("items", []))
    if not title or not items:
        return

    existing_index = index_by_title.get(title.lower())
    if existing_index is None:
        index_by_title[title.lower()] = len(merged)
        merged.append({"title": title, "items": items})
        return

    existing = merged[existing_index]
    existing_keys = _item_keys(existing.get("items", []))
    for item in items:
        key = _item_key(item)
        if key not in existing_keys:
            existing.setdefault("items", []).append(item)
            existing_keys.add(key)


def _normalize_sections(sections: Any) -> list[dict[str, Any]]:
    normalized = []
    for section in sections or []:
        if not isinstance(section, dict):
            continue
        title = clean_text_value(section.get("title", ""))
        items = _normalize_section_items(section.get("items", []))
        if title and items:
            normalized.append({"title": title, "items": items})
    return normalized


def _normalize_section_items(items: Any) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    seen = set()

    for item in items or []:
        entry = _normalize_section_item(item)
        if not entry:
            continue
        key = _item_key(entry)
        if key in seen:
            continue
        seen.add(key)
        normalized.append(entry)

    return normalized


def _normalize_section_item(item: Any) -> dict[str, str] | None:
    if not isinstance(item, dict):
        item = {"name": str(item)}

    name = clean_text_value(item.get("name", ""))
    if not name:
        return None

    entry = {"name": name}
    description = clean_text_value(item.get("description", ""))
    if description:
        entry["description"] = description
    return entry


def _item_keys(items: list[dict[str, Any]]) -> set[tuple[str, str]]:
    return {_item_key(item) for item in items}


def _item_key(item: dict[str, Any]) -> tuple[str, str]:
    return (
        str(item.get("name", "")).strip().lower(),
        str(item.get("description", "")).strip().lower(),
    )


def _merge_statistics(
    merged: Dict[str, Any],
    base: Dict[str, Any],
    extra: Dict[str, Any],
) -> None:
    statistics = dict(base.get("statistics", {}) if isinstance(base, dict) else {})
    extra_statistics = extra.get("statistics", {}) if isinstance(extra, dict) else {}
    if isinstance(extra_statistics, dict):
        statistics.update(extra_statistics)
    if statistics:
        merged["statistics"] = statistics
