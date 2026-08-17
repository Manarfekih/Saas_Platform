from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.document import Document
from app.services.document_text import build_coverage_excerpt
from app.services.summary.config import SUMMARY_MAX_TEXT_CHARS
from app.services.summary.parser import (
    build_fallback_summary,
    normalize_summary,
)
from app.services.summary.storage import save_summary_to_file
from app.services.summary.summary_components import build_structured_summary

logger = logging.getLogger(__name__)


def generate_summary(
    text: str,
    document_type: Optional[str] = None,
    page_count: Optional[int] = None,
    classified_items: Optional[List[Dict[str, object]]] = None,
    filename: Optional[str] = None,
) -> Dict[str, object]:
    if not text or len(text.strip()) < 50:
        logger.warning("Insufficient text for summary generation")
        return build_fallback_summary(text, document_type, page_count)

    coverage_text = build_coverage_excerpt(text, SUMMARY_MAX_TEXT_CHARS)
    structured = build_structured_summary(
        coverage_text,
        document_type,
        page_count,
        classified_items,
        filename=filename,
    )

    return normalize_summary(structured, text=coverage_text, page_count=page_count)


def generate_and_store_summary(
    db: Session,
    document: Document,
    classified_items: Optional[List[Dict[str, object]]] = None,
) -> Dict[str, object]:
    if not document.extracted_text or len(document.extracted_text.strip()) < 50:
        return {
            "success": False,
            "error": "Document has insufficient text for summarization",
        }

    try:
        logger.info("Generating summary for document %s", document.id)

        summary = generate_summary(
            text=document.extracted_text,
            document_type=document.doc_type,
            page_count=getattr(document, "page_count", None),
            classified_items=classified_items,
            filename=document.filename,
        )

        document.summary = summary
        file_path = save_summary_to_file(summary, document)
        document.summary_file_path = file_path
        document.summary_file_name = Path(file_path).name

        db.commit()
        db.refresh(document)

        logger.info("Summary stored for document %s", document.id)

        return {
            "success": True,
            "document_id": document.id,
            "summary": summary,
            "file_path": file_path,
            "file_name": document.summary_file_name,
        }
    except Exception as exc:
        logger.error("Summary generation failed: %s", exc)
        db.rollback()
        return {
            "success": False,
            "error": str(exc),
        }
