import logging
from datetime import datetime
from pathlib import Path

from app.services.summary.config import SUMMARY_DIR
from app.services.summary.formatter import export_summary_to_markdown

logger = logging.getLogger(__name__)


def _safe_filename_stem(filename: str | None, fallback: str = "document") -> str:
    base_name = Path(filename or fallback).stem or fallback
    safe_name = "".join(char for char in base_name if char.isalnum() or char in " _-").strip()
    return safe_name or fallback


def build_summary_filename(document) -> str:
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    stem = _safe_filename_stem(getattr(document, "filename", None))
    return f"summary_{stem}_{timestamp}.md"


def build_summary_path(document) -> Path:
    return SUMMARY_DIR / build_summary_filename(document)


def save_summary_to_file(summary: dict, document) -> str:
    path = build_summary_path(document)
    with path.open("w", encoding="utf-8") as handle:
        handle.write(export_summary_to_markdown(summary))
    logger.info("Summary saved to: %s", path)
    return str(path)


def delete_summary_file(document) -> bool:
    summary_path = getattr(document, "summary_file_path", None)
    if not summary_path:
        return True

    try:
        path = Path(summary_path)
        if path.exists():
            path.unlink()
            logger.info("Deleted summary file: %s", path)
        return True
    except Exception as exc:
        logger.error("Failed to delete summary file: %s", exc)
        return False


def get_summary_file_content(document) -> str | None:
    summary_path = getattr(document, "summary_file_path", None)
    if not summary_path:
        return None

    try:
        path = Path(summary_path)
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as handle:
            return handle.read()
    except Exception as exc:
        logger.error("Failed to read summary file: %s", exc)
        return None
