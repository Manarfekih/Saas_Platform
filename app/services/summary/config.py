from pathlib import Path
import os

DEFAULT_SUMMARY_DIR = Path(__file__).resolve().parents[3] / "storage" / "summaries"

SUMMARY_DIR = Path(os.getenv("SUMMARY_DIR", str(DEFAULT_SUMMARY_DIR)))
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)

SUMMARY_MAX_TEXT_CHARS = int(os.getenv("SUMMARY_MAX_TEXT_CHARS", "24000"))

MAX_OVERVIEW_ITEMS = 8
