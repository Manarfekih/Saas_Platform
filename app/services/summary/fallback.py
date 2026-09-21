from typing import Any, Dict, Optional

from app.services.summary.summary_cleaning import clean_line, extract_title
from app.services.summary.summary_normalizer import normalize_summary


def build_fallback_summary(
    text: str,
    document_type: Optional[str] = None,
    page_count: Optional[int] = None,
) -> Dict[str, Any]:
    preview = (text or "").strip()
    cleaned_lines = [
        line.strip()
        for line in preview.splitlines()[:40]
        if clean_line(line)
    ]
    cleaned_preview = " ".join(cleaned_lines).strip() or preview

    summary = {
        "title": extract_title(text),
        "document_type": document_type or "Document",
        "overview": cleaned_preview[:300] or "No content available",
        "key_information": {
            "people": [],
            "organizations": [],
            "dates": [],
            "amounts": [],
        },
        "sections": _fallback_sections(cleaned_preview),
    }

    return normalize_summary(summary, text=cleaned_preview, page_count=page_count)


def _fallback_sections(cleaned_preview: str) -> list[dict[str, Any]]:
    if not cleaned_preview:
        return []
    return [
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
