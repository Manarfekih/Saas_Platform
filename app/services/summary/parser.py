import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

_THINK_PATTERN = re.compile(r"<think>.*?</think>", flags=re.DOTALL)
_FENCE_PATTERN = re.compile(r"^```(?:json)?\s*(.*?)\s*```$", flags=re.DOTALL)
_PAGE_MARKER_PATTERN = re.compile(
    r"^(---\s*PAGES?\s*\d+[-\u2013]\d+\s*---|\[\[PAGE\s*\d+\]\])$",
    flags=re.IGNORECASE,
)
_NOISE_TITLE_PATTERN = re.compile(
    r"^(?:[#*\-\s`_]+)?(?:page\s*)?\d+(?:\s*[-–]\s*\d+)?(?:\s+of\s+\d+)?(?:\s*[#*\-\s`_]+)?$",
    flags=re.IGNORECASE,
)


def _coerce_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def _clean_line(line: str) -> str:
    cleaned = line.strip()
    return "" if _PAGE_MARKER_PATTERN.match(cleaned) else cleaned


def _clean_title_value(value: Any) -> str:
    text = str(value or "").strip()
    text = re.sub(r"^\*\*(.*?)\*\*$", r"\1", text)
    text = re.sub(r"^[#\-*\s`_]+", "", text)
    text = re.sub(r"[\-\*\s`_]+$", "", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def _is_noise_title(value: Any) -> bool:
    text = _clean_title_value(value)
    if not text:
        return True

    lowered = text.lower()
    if lowered in {"summary", "document summary", "overview", "title"}:
        return True
    if lowered in {"cv", "resume", "document", "doc", "file", "scan", "scanned", "image"}:
        return True
    if lowered.startswith("page ") or lowered.startswith("pages ") or lowered.startswith("# pages"):
        return True
    if _NOISE_TITLE_PATTERN.match(text):
        return True
    if re.fullmatch(r"[#*\-\_\s]+", text):
        return True
    return False


def _extract_title(text: str | None) -> str:
    if not text:
        return "Document Summary"

    for line in text.splitlines()[:30]:
        cleaned = _clean_line(line)
        cleaned = _clean_title_value(cleaned)
        if cleaned and not _is_noise_title(cleaned):
            return cleaned[:120]

    return "Document Summary"


def parse_llm_json(raw: str) -> Optional[Dict[str, Any]]:
    if not raw:
        return None

    text = raw.strip()
    text = _THINK_PATTERN.sub("", text).strip()

    fence_match = _FENCE_PATTERN.match(text)
    if fence_match:
        text = fence_match.group(1).strip()

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            pass

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def build_statistics(
    text: str,
    sections: List[Dict[str, Any]],
    page_count: Optional[int] = None,
) -> Dict[str, Any]:
    return {
        "total_pages": page_count or 0,
        "generated_at": datetime.utcnow().isoformat(),
    }


def _clean_overview(overview: str) -> str:
    if not overview:
        return "No overview available"

    overview = re.sub(r'^[=\-#\*\s\._]+', '', overview, flags=re.MULTILINE)
    overview = re.sub(
        r'\[\s*(page|pg\.?)\s*\d+(\s+of\s+\d+)?\s*\]',
        '',
        overview,
        flags=re.IGNORECASE,
    )
    overview = re.sub(
        r'\(\s*(page|pg\.?)\s*\d+(\s+of\s+\d+)?\s*\)',
        '',
        overview,
        flags=re.IGNORECASE,
    )
    overview = re.sub(
        r'---\s*PAGES?\s*\d+[-\u2013]?\d*\s*---|\[\[PAGE\s*\d+\]\]|\*\*#\s*PAGES?\s*\d+[-\u2013]?\d+\s*---\*\*',
        '',
        overview,
        flags=re.IGNORECASE,
    )
    overview = re.sub(r'(?i)\b(page|pg\.?)\s*\d+(\s+of\s+\d+)?\b', '', overview)
    overview = re.sub(r'\[\s*\]', '', overview)
    overview = re.sub(r'\(\s*\)', '', overview)
    overview = re.sub(r'\{\s*\}', '', overview)
    overview = re.sub(r' {2,}', ' ', overview)
    overview = re.sub(r'\s+([,\.\?!;])', r'\1', overview)
    overview = re.sub(r'(?im)^\s*(title|document type|overview|sections?|key information)\s*:\s*', '', overview)

    lines = []
    for line in overview.splitlines():
        line_clean = line.strip()
        line_clean = re.sub(r'^[\-\*\s\._]+', '', line_clean)
        line_clean = re.sub(r'[\-\*\s_]+$', '', line_clean)
        if line_clean:
            lines.append(line_clean)

    return "\n\n".join(lines).strip() or "No overview available"


def _clean_text_value(value: Any) -> str:
    text = str(value or "").strip()
    text = re.sub(r'^\s*(title|document type|overview|summary)\s*:\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^[#\-*\s]+', '', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()


def _merge_unique_lists(base: List[str], extra: List[str]) -> List[str]:
    merged: List[str] = []
    seen = set()
    for item in base + extra:
        cleaned = str(item).strip()
        if not cleaned:
            continue
        key = cleaned.lower()
        if key in seen:
            continue
        seen.add(key)
        merged.append(cleaned)
    return merged


def _merge_sections(
    base_sections: List[Dict[str, Any]],
    extra_sections: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    index_by_title: dict[str, int] = {}

    def add_section(section: Dict[str, Any]):
        title = _clean_text_value(section.get("title", ""))
        if not title:
            return

        items = section.get("items", [])
        cleaned_items: list[dict[str, Any]] = []
        seen_items = set()
        for item in items:
            if not isinstance(item, dict):
                item = {"name": str(item)}
            name = _clean_text_value(item.get("name", ""))
            if not name:
                continue
            description = _clean_text_value(item.get("description", ""))
            key = (name.lower(), description.lower())
            if key in seen_items:
                continue
            seen_items.add(key)
            entry: dict[str, Any] = {"name": name}
            if description:
                entry["description"] = description
            cleaned_items.append(entry)

        if not cleaned_items:
            return

        existing_index = index_by_title.get(title.lower())
        if existing_index is None:
            index_by_title[title.lower()] = len(merged)
            merged.append({"title": title, "items": cleaned_items})
            return

        existing = merged[existing_index]
        existing_keys = {
            (
                str(item.get("name", "")).strip().lower(),
                str(item.get("description", "")).strip().lower(),
            )
            for item in existing.get("items", [])
        }
        for item in cleaned_items:
            key = (item["name"].lower(), item.get("description", "").lower())
            if key in existing_keys:
                continue
            existing.setdefault("items", []).append(item)
            existing_keys.add(key)

    for section in base_sections:
        if isinstance(section, dict):
            add_section(section)
    for section in extra_sections:
        if isinstance(section, dict):
            add_section(section)

    return merged


def merge_summary(base: Dict[str, Any], extra: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(base or {})
    extra = extra or {}

    extra_title = _clean_text_value(extra.get("title"))
    if extra_title and not _is_noise_title(extra_title):
        merged["title"] = extra_title

    extra_type = _clean_text_value(extra.get("document_type"))
    if extra_type:
        merged["document_type"] = extra_type

    extra_overview = extra.get("overview")
    if isinstance(extra_overview, str) and extra_overview.strip():
        merged["overview"] = extra_overview.strip()

    base_key_info = base.get("key_information", {}) if isinstance(base, dict) else {}
    extra_key_info = extra.get("key_information", {}) if isinstance(extra, dict) else {}
    merged["key_information"] = {
        "people": _merge_unique_lists(
            _coerce_list(base_key_info.get("people")),
            _coerce_list(extra_key_info.get("people")),
        ),
        "organizations": _merge_unique_lists(
            _coerce_list(base_key_info.get("organizations")),
            _coerce_list(extra_key_info.get("organizations")),
        ),
        "dates": _merge_unique_lists(
            _coerce_list(base_key_info.get("dates")),
            _coerce_list(extra_key_info.get("dates")),
        ),
        "amounts": _merge_unique_lists(
            _coerce_list(base_key_info.get("amounts")),
            _coerce_list(extra_key_info.get("amounts")),
        ),
    }

    merged["sections"] = _merge_sections(
        list(base.get("sections", [])) if isinstance(base, dict) else [],
        list(extra.get("sections", [])) if isinstance(extra, dict) else [],
    )

    statistics = dict(base.get("statistics", {}) if isinstance(base, dict) else {})
    extra_statistics = extra.get("statistics", {}) if isinstance(extra, dict) else {}
    if isinstance(extra_statistics, dict):
        statistics.update(extra_statistics)

    if statistics:
        merged["statistics"] = statistics
    elif isinstance(base, dict) and base.get("statistics"):
        merged["statistics"] = base.get("statistics")

    return merged


def normalize_summary(
    summary: Dict[str, Any],
    text: str | None = None,
    page_count: Optional[int] = None,
) -> Dict[str, Any]:
    normalized = dict(summary or {})

    title = _clean_text_value(normalized.get("title"))
    if _is_noise_title(title):
        title = _extract_title(text)
    normalized["title"] = title or "Document Summary"

    normalized.setdefault("document_type", normalized.get("document_type") or "Document")
    normalized["document_type"] = _clean_text_value(normalized.get("document_type")) or "Document"

    overview = normalized.get("overview")
    if not isinstance(overview, str):
        overview = str(overview) if overview is not None else ""
    normalized["overview"] = _clean_overview(overview)
    normalized.setdefault("key_information", {})
    normalized.setdefault("sections", [])

    key_info = normalized.get("key_information") or {}
    normalized["key_information"] = {
        "people": _coerce_list(key_info.get("people")),
        "organizations": _coerce_list(key_info.get("organizations")),
        "dates": _coerce_list(key_info.get("dates")),
        "amounts": _coerce_list(key_info.get("amounts")),
    }

    sections = []
    for section in normalized.get("sections", []):
        if not isinstance(section, dict):
            continue

        title = _clean_text_value(section.get("title", ""))
        if not title:
            continue

        items = []
        seen_items = set()
        for item in section.get("items", []):
            if isinstance(item, dict):
                name = _clean_text_value(item.get("name", ""))
                if not name:
                    continue
                entry = {"name": name}
                description = item.get("description")
                if description not in (None, ""):
                    entry["description"] = _clean_text_value(description)
                key = (entry["name"].lower(), entry.get("description", "").lower())
                if key in seen_items:
                    continue
                seen_items.add(key)
                items.append(entry)
            else:
                name = _clean_text_value(item)
                if name and name.lower() not in {i["name"].lower() for i in items}:
                    items.append({"name": name})

        if items:
            sections.append({"title": title, "items": items})

    normalized["sections"] = sections
    normalized["statistics"] = build_statistics(text or "", sections, page_count=page_count)

    return normalized


def build_fallback_summary(
    text: str,
    document_type: Optional[str] = None,
    page_count: Optional[int] = None,
) -> Dict[str, Any]:
    preview = (text or "").strip()
    cleaned_lines = [
        line.strip()
        for line in preview.splitlines()[:40]
        if _clean_line(line)
    ]
    cleaned_preview = " ".join(cleaned_lines).strip() or preview

    summary = {
        "title": _extract_title(text),
        "document_type": document_type or "Document",
        "overview": cleaned_preview[:300] or "No content available",
        "key_information": {
            "people": [],
            "organizations": [],
            "dates": [],
            "amounts": [],
        },
        "sections": [],
    }

    if cleaned_preview:
        summary["sections"] = [
            {
                "title": "Document Content",
                "items": [
                    {
                        "name": "Content Preview",
                        "description": cleaned_preview[:700],
                    }
                ],
            }
        ]

    return normalize_summary(summary, text=cleaned_preview, page_count=page_count)
