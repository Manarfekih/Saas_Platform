import re
from typing import Any, List

PAGE_MARKER_PATTERN = re.compile(
    r"^(---\s*PAGES?\s*\d+[-\u2013]\d+\s*---|\[\[PAGE\s*\d+\]\])$",
    flags=re.IGNORECASE,
)
NOISE_TITLE_PATTERN = re.compile(
    r"^(?:[#*\-\s`_]+)?(?:page\s*)?\d+(?:\s*[-–]\s*\d+)?"
    r"(?:\s+of\s+\d+)?(?:\s*[#*\-\s`_]+)?$",
    flags=re.IGNORECASE,
)
GENERIC_TITLE_TOKENS = {
    "cv",
    "resume",
    "document",
    "doc",
    "file",
    "scan",
    "scanned",
    "image",
}


def coerce_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def clean_line(line: str) -> str:
    cleaned = line.strip()
    return "" if PAGE_MARKER_PATTERN.match(cleaned) else cleaned


def clean_title_value(value: Any) -> str:
    text = str(value or "").strip()
    text = re.sub(r"^\*\*(.*?)\*\*$", r"\1", text)
    text = re.sub(r"^[#\-*\s`_]+", "", text)
    text = re.sub(r"[\-\*\s`_]+$", "", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def clean_text_value(value: Any) -> str:
    text = str(value or "").strip()
    text = re.sub(
        r"^\s*(title|document type|overview|summary)\s*:\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"^[#\-*\s]+", "", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def is_noise_title(value: Any) -> bool:
    text = clean_title_value(value)
    if not text:
        return True
    if not clean_line(text):
        return True

    lowered = text.lower()
    if lowered in {
        "summary",
        "document summary",
        "overview",
        "title",
        "exhaustive summary of the document",
    }:
        return True
    if lowered in GENERIC_TITLE_TOKENS:
        return True
    if lowered.startswith(("page ", "pages ", "# pages")):
        return True
    if NOISE_TITLE_PATTERN.match(text):
        return True
    return bool(re.fullmatch(r"[#*\-\_\s]+", text))


def extract_title(text: str | None) -> str:
    if text:
        for line in text.splitlines()[:30]:
            cleaned = clean_title_value(clean_line(line))
            if cleaned and not is_noise_title(cleaned):
                return cleaned[:120]
    return "Document Summary"


def clean_overview(overview: str) -> str:
    if not overview:
        return "No overview available"

    overview = re.sub(r"^[=\-#\*\s\._]+", "", overview, flags=re.MULTILINE)
    overview = re.sub(
        r"\[\s*(page|pg\.?)\s*\d+(\s+of\s+\d+)?\s*\]",
        "",
        overview,
        flags=re.IGNORECASE,
    )
    overview = re.sub(
        r"\(\s*(page|pg\.?)\s*\d+(\s+of\s+\d+)?\s*\)",
        "",
        overview,
        flags=re.IGNORECASE,
    )
    overview = re.sub(
        r"---\s*PAGES?\s*\d+[-\u2013]?\d*\s*---|\[\[PAGE\s*\d+\]\]|"
        r"\*\*#\s*PAGES?\s*\d+[-\u2013]?\d+\s*---\*\*",
        "",
        overview,
        flags=re.IGNORECASE,
    )
    overview = re.sub(r"(?i)\b(page|pg\.?)\s*\d+(\s+of\s+\d+)?\b", "", overview)
    overview = re.sub(r"[\[\(\{]\s*[\]\)\}]", "", overview)
    overview = re.sub(r" {2,}", " ", overview)
    overview = re.sub(r"\s+([,\.\?!;])", r"\1", overview)
    overview = re.sub(
        r"(?im)^\s*(title|document type|overview|sections?|key information)\s*:\s*",
        "",
        overview,
    )

    lines = []
    for line in overview.splitlines():
        line_clean = re.sub(r"^[\-\*\s\._]+", "", line.strip())
        line_clean = re.sub(r"[\-\*\s_]+$", "", line_clean)
        if line_clean:
            lines.append(line_clean)

    return "\n\n".join(lines).strip() or "No overview available"
