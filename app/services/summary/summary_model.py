import logging
from typing import Any, Dict, List, Optional

from app.services.llm_service import ask_llm
from app.services.summary.parser import parse_llm_json
from app.services.summary.prompts import SUMMARY_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)


def generate_model_summary(
    text: str,
    document_type: Optional[str],
    classified_items: Optional[List[Dict[str, Any]]] = None,
    filename: Optional[str] = None,
) -> Dict[str, Any] | None:
    prompt = _build_summary_prompt(
        text=text,
        document_type=document_type,
        classified_items=classified_items,
        filename=filename,
    )

    try:
        raw_response = ask_llm(prompt)
    except Exception as exc:
        logger.warning("Summary model call failed: %s", exc)
        return None

    parsed = parse_llm_json(str(raw_response))
    if parsed:
        return parsed

    logger.warning("Summary model returned invalid JSON; attempting repair")
    repaired = _repair_summary_json(str(raw_response))
    if not repaired:
        logger.warning("Summary JSON repair failed")
    return repaired


def _build_summary_prompt(
    text: str,
    document_type: Optional[str],
    classified_items: Optional[List[Dict[str, Any]]],
    filename: Optional[str],
) -> str:
    return (
        SUMMARY_PROMPT_TEMPLATE
        .replace("{document_type}", document_type or "Document")
        .replace("{filename}", filename or "")
        .replace("{extracted_context_block}", _classified_context(classified_items))
        .replace("{text}", text)
    )


def _classified_context(classified_items: Optional[List[Dict[str, Any]]]) -> str:
    if not classified_items:
        return ""

    lines = ["Relevant extracted items from the full document coverage:"]
    for item in classified_items:
        if not isinstance(item, dict):
            continue
        parts = [f"Category: {item.get('category', 'other')}"]
        for label, key in [
            ("Title", "title"),
            ("Organization", "organization"),
            ("Dates", "dates"),
            ("Amount", "amount"),
            ("Details", "details"),
        ]:
            if item.get(key):
                parts.append(f"{label}: {item[key]}")
        lines.append("- " + " | ".join(parts))
    return "\n".join(lines)


def _repair_summary_json(raw_response: str) -> Dict[str, Any] | None:
    prompt = f"""
/no_think

Convert the following document summary into exactly one valid JSON object.
Return JSON only. No markdown, no headings, no code fences.

Required shape:
{{
  "title": "Document Title",
  "document_type": "CV | Invoice | Contract | Report | Other",
  "overview": "2-4 sentence plain-text overview",
  "key_information": {{
    "people": [],
    "organizations": [],
    "dates": [],
    "amounts": []
  }},
  "sections": [
    {{
      "title": "Section Name",
      "items": [
        {{"name": "Item Name", "description": "Details"}}
      ]
    }}
  ]
}}

Summary to convert:
{raw_response}
""".strip()

    try:
        repaired_response = ask_llm(prompt)
    except Exception as exc:
        logger.warning("Summary JSON repair model call failed: %s", exc)
        return None

    return parse_llm_json(str(repaired_response))
