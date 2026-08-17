from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.services.document_text import build_coverage_excerpt, clean_document_text
from app.services.summary.config import SUMMARY_MAX_TEXT_CHARS
from app.services.summary.parser import normalize_summary
from app.services.summary.prompts import SUMMARY_PROMPT_TEMPLATE

_SECTION_LABELS = {
    "contact_info": "Contact Information",
    "summary": "Executive Summary",
    "skill": "Skills",
    "formal_education": "Education",
    "certification": "Certifications",
    "project": "Projects",
    "experience": "Experience",
    "leadership": "Leadership",
    "language": "Languages",
    "vendor": "Vendor",
    "customer": "Customer",
    "line_item": "Line Items",
    "subtotal": "Subtotal",
    "tax": "Tax",
    "total": "Totals",
    "payment_terms": "Payment Terms",
    "party": "Parties",
    "clause": "Key Clauses",
    "definition": "Definitions",
    "signature": "Signatures",
    "executive_summary": "Executive Summary",
    "finding": "Findings",
    "recommendation": "Recommendations",
    "data_point": "Data Points",
    "metadata": "Metadata",
    "other": "Additional Information",
}

_SECTION_ORDER = [
    "metadata",
    "contact_info",
    "summary",
    "executive_summary",
    "experience",
    "project",
    "formal_education",
    "skill",
    "certification",
    "finding",
    "recommendation",
    "data_point",
    "vendor",
    "customer",
    "line_item",
    "subtotal",
    "tax",
    "total",
    "payment_terms",
    "party",
    "clause",
    "definition",
    "signature",
    "leadership",
    "language",
    "other",
]

_GENERIC_FILENAME_TOKENS = {
    "cv",
    "resume",
    "document",
    "doc",
    "summary",
    "file",
    "scan",
    "scanned",
    "image",
}

_NOISE_TITLE_PATTERN = re.compile(
    r"^(?:[#*\-\s`_]+)?(?:page\s*)?\d+(?:\s*[-–]\s*\d+)?(?:\s+of\s+\d+)?(?:\s*[#*\-\s`_]+)?$",
    flags=re.IGNORECASE,
)

_HEADING_HINTS = {
    "objective",
    "profile",
    "professional profile",
    "summary",
    "overview",
    "education",
    "experience",
    "work experience",
    "projects",
    "skills",
    "certifications",
    "certificates",
    "languages",
    "contact",
    "contact information",
    "publications",
    "research",
    "achievements",
    "interests",
    "personal information",
    "technical skills",
    "project overview",
    "system architecture",
    "technology stack",
    "workflow processes",
    "project phases",
    "key findings",
    "recommendations",
    "executive summary",
    "scope",
    "deliverables",
    "requirements",
    "implementation",
}


def _clean_candidate_title(value: str | None) -> str:
    if not value:
        return ""

    text = str(value).strip()
    text = re.sub(r"^\*\*(.*?)\*\*$", r"\1", text)
    text = re.sub(r"^[#\-*\s`_]+", "", text)
    text = re.sub(r"[\-\*\s`_]+$", "", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def _looks_like_noise_title(value: str | None) -> bool:
    text = _clean_candidate_title(value)
    if not text:
        return True

    lowered = text.lower()
    if lowered in {"summary", "document summary", "overview", "title"}:
        return True
    if lowered.startswith("page ") or lowered.startswith("pages ") or lowered.startswith("# pages"):
        return True
    if lowered in _GENERIC_FILENAME_TOKENS:
        return True
    if _NOISE_TITLE_PATTERN.match(text):
        return True
    if re.fullmatch(r"[#*\-_\s]+", text):
        return True
    return False


def _fallback_title_from_text(text: str | None, document_type: Optional[str]) -> str:
    if text:
        for line in text.splitlines()[:30]:
            candidate = _clean_candidate_title(line)
            if not candidate or _looks_like_noise_title(candidate):
                continue
            if len(candidate) < 3:
                continue
            return candidate[:120]

    if document_type:
        return f"{document_type} Summary"

    return "Document Summary"


def _title_from_source(text: str | None, document_type: Optional[str], filename: str | None = None) -> str:
    if filename:
        stem = Path(filename).stem
        if stem:
            stem = _clean_candidate_title(stem)
            if stem and not _looks_like_noise_title(stem):
                return stem[:120]

    return _fallback_title_from_text(text, document_type)


def _normalize_heading(line: str) -> str:
    heading = _clean_candidate_title(line)
    heading = re.sub(r"[:\-–]+$", "", heading).strip()
    return heading


def _is_heading_line(line: str) -> bool:
    text = _clean_candidate_title(line)
    if not text:
        return False
    if _looks_like_noise_title(text):
        return False
    if len(text) > 80:
        return False
    if text.endswith((".", ";", ",", ":")):
        return False

    lowered = text.lower()
    if lowered in _HEADING_HINTS:
        return True
    if lowered.startswith(tuple(f"{hint} " for hint in _HEADING_HINTS)):
        return True
    if text.isupper() and len(text.split()) <= 8:
        return True
    if re.match(r"^[A-Z][A-Za-z0-9/&()\-\s]{2,}$", text) and len(text.split()) <= 8:
        return True
    return False


def _split_sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [part.strip() for part in parts if part.strip()]


def _extract_text_outline(text: str) -> List[Dict[str, Any]]:
    cleaned = clean_document_text(text)
    if not cleaned:
        return []

    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    sections: list[dict[str, Any]] = []
    current_title: Optional[str] = None
    current_body: list[str] = []

    def flush_section():
        nonlocal current_title, current_body
        if not current_title:
            return

        body_text = "\n".join(current_body).strip()
        items: list[dict[str, str]] = []

        bullet_lines = [
            re.sub(r"^[\-*\u2022\s]+", "", line).strip()
            for line in current_body
            if re.match(r"^[\-*\u2022]\s+", line)
        ]
        bullet_lines = [line for line in bullet_lines if line]

        if bullet_lines:
            for bullet in bullet_lines[:6]:
                items.append({"name": bullet[:120]})
        else:
            sentences = _split_sentences(body_text)
            for sentence in sentences[:3]:
                sentence = re.sub(r"\s{2,}", " ", sentence).strip()
                if sentence:
                    items.append({"name": sentence[:160]})

        if items:
            sections.append({"title": current_title, "items": items})

        current_title = None
        current_body = []

    for line in lines:
        if _is_heading_line(line):
            flush_section()
            current_title = _normalize_heading(line)
            continue

        if current_title:
            current_body.append(line)

    flush_section()

    return sections


def build_summary_prompt(
    text: str,
    document_type: Optional[str],
    classified_items: Optional[List[Dict[str, Any]]] = None,
) -> str:
    extracted_context_block = ""
    if classified_items:
        lines = ["Relevant extracted items from the full document coverage:"]
        for item in classified_items:
            category = item.get("category", "other")
            title = item.get("title", "")
            org = item.get("organization")
            dates = item.get("dates")
            amount = item.get("amount")
            details = item.get("details")
            parts = [f"Category: {category}"]
            if title:
                parts.append(f"Title: {title}")
            if org:
                parts.append(f"Organization: {org}")
            if dates:
                parts.append(f"Dates: {dates}")
            if amount:
                parts.append(f"Amount: {amount}")
            if details:
                parts.append(f"Details: {details}")
            lines.append("- " + " | ".join(parts))
        extracted_context_block = "\n".join(lines)

    coverage_text = build_coverage_excerpt(text, SUMMARY_MAX_TEXT_CHARS)

    try:
        return SUMMARY_PROMPT_TEMPLATE.format(
            document_type=document_type or "Document",
            extracted_context_block=extracted_context_block,
            text=coverage_text,
        )
    except Exception:
        return f"""
/no_think
You are an expert document analyst. Create a clean, exhaustive summary.
Document Type: {document_type or 'Document'}
Document Text:
{text[:SUMMARY_MAX_TEXT_CHARS]}
JSON:
"""


def _section_title(category: str) -> str:
    return _SECTION_LABELS.get(category, category.replace("_", " ").title())


def _normalize_classified_items(
    classified_items: Optional[List[Dict[str, Any]]]
) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []

    for item in classified_items or []:
        if not isinstance(item, dict):
            continue

        title = (item.get("title") or "").strip()
        if not title:
            continue

        normalized.append(
            {
                "category": (item.get("category") or "other").strip(),
                "title": title,
                "organization": item.get("organization") or None,
                "dates": item.get("dates") or None,
                "amount": item.get("amount") or None,
                "details": item.get("details") or None,
            }
        )

    return normalized


def build_structured_summary(
    text: str,
    document_type: Optional[str],
    page_count: Optional[int],
    classified_items: Optional[List[Dict[str, Any]]],
    filename: str | None = None,
) -> Dict[str, Any]:
    items = _normalize_classified_items(classified_items)
    text_outline = _extract_text_outline(text)

    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for item in items:
        grouped.setdefault(item["category"], []).append(item)

    sections = []
    for category in _SECTION_ORDER:
        if category not in grouped:
            continue

        section_items = []
        for item in grouped[category]:
            parts = [
                item.get("organization"),
                item.get("dates"),
                item.get("amount"),
                item.get("details"),
            ]
            description = " | ".join(part for part in parts if part)

            entry = {"name": item["title"]}
            if description:
                entry["description"] = description
            section_items.append(entry)

        if section_items:
            sections.append({"title": _section_title(category), "items": section_items})

    if not sections and text_outline:
        sections = text_outline
    elif text_outline:
        existing_titles = {section.get("title", "").strip().lower() for section in sections}
        for outline_section in text_outline:
            title = outline_section.get("title", "").strip().lower()
            if title and title not in existing_titles:
                sections.append(outline_section)
                existing_titles.add(title)

    key_information = {
        "people": [],
        "organizations": [],
        "dates": [],
        "amounts": [],
    }

    for item in items:
        if item.get("organization"):
            org = item["organization"]
            if org not in key_information["organizations"]:
                key_information["organizations"].append(org)
        if item.get("dates"):
            date = item["dates"]
            if date not in key_information["dates"]:
                key_information["dates"].append(date)
        if item.get("amount"):
            amount = item["amount"]
            if amount not in key_information["amounts"]:
                key_information["amounts"].append(amount)

    summary = {
        "title": _title_from_source(text, document_type, filename=filename),
        "document_type": document_type or "Document",
        "overview": build_overview(text, document_type, items, text_outline),
        "key_information": key_information,
        "sections": sections,
    }

    return normalize_summary(summary, text=text, page_count=page_count)


def build_overview(
    text: str,
    document_type: Optional[str],
    items: List[Dict[str, Any]],
    text_outline: Optional[List[Dict[str, Any]]] = None,
) -> str:
    cleaned_text = re.sub(r"(?i)\b(page|pg\.?)\s*\d+(\s+of\s+\d+)?\b", "", text or "")
    cleaned_text = re.sub(
        r"---\s*PAGES?\s*\d+[-\u2013]?\d*\s*---|\[\[PAGE\s*\d+\]\]|\*\*#\s*PAGES?\s*\d+[-\u2013]?\d+\s*---\*\*",
        "",
        cleaned_text,
        flags=re.IGNORECASE,
    )
    cleaned_text = re.sub(r"^[#\-*\s`_]+", "", cleaned_text, flags=re.MULTILINE)
    cleaned_text = re.sub(r"\s{2,}", " ", cleaned_text).strip()

    doc_name = (document_type or "document").lower()
    if doc_name in {"cv", "resume"}:
        doc_name = "curriculum vitae (CV)"

    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for item in items:
        grouped.setdefault(item["category"], []).append(item)

    contact = grouped.get("contact_info", [])[:1]
    subject = f" for {contact[0]['title']}" if contact else ""

    section_names = [
        _SECTION_LABELS.get(cat, cat.replace("_", " ").title())
        for cat in _SECTION_ORDER
        if cat in grouped and cat != "contact_info"
    ]

    if not section_names and text_outline:
        section_names = [section.get("title", "") for section in text_outline if section.get("title")]

    key_topics = [item["title"] for item in items if item.get("title")][:10]
    outline_topics = []
    for section in text_outline or []:
        title = section.get("title", "")
        if title:
            outline_topics.append(title)
    if not key_topics and outline_topics:
        key_topics = outline_topics[:8]

    parts = [f"This document appears to be a {doc_name}{subject}."]

    if section_names:
        unique_sections = []
        seen = set()
        for name in section_names:
            cleaned = name.strip()
            if cleaned and cleaned.lower() not in seen:
                unique_sections.append(cleaned)
                seen.add(cleaned.lower())
        if len(unique_sections) == 1:
            parts.append(f"It mainly covers {unique_sections[0]}.")
        elif len(unique_sections) == 2:
            parts.append(f"It mainly covers {unique_sections[0]} and {unique_sections[1]}.")
        else:
            parts.append(
                f"It mainly covers {', '.join(unique_sections[:-1])}, and {unique_sections[-1]}."
            )

    if key_topics:
        if len(key_topics) == 1:
            parts.append(f"Key content includes {key_topics[0]}.")
        elif len(key_topics) == 2:
            parts.append(f"Key content includes {key_topics[0]} and {key_topics[1]}.")
        else:
            parts.append(
                f"Key content includes {', '.join(key_topics[:-1])}, and {key_topics[-1]}."
            )

    cleaned_preview = " ".join(cleaned_text.split())
    if cleaned_preview:
        snippet = cleaned_preview[:350]
        if snippet and snippet.lower() not in " ".join(parts).lower():
            parts.append(f"The cleaned text also shows: {snippet}.")

    return " ".join(parts)[:1800]
