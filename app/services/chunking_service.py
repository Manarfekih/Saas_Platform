from asyncio.log import logger
import re
from collections import Counter
from difflib import SequenceMatcher

from langchain_text_splitters import RecursiveCharacterTextSplitter


DEFAULT_CHUNK_SIZE = 450
DEFAULT_CHUNK_OVERLAP = 50
MIN_CHUNK_LENGTH = 40
NEAR_DUPLICATE_THRESHOLD = 0.88
MAX_SECTION_CHUNK_SIZE = 900

HEADING_PATTERN = re.compile(r"^#{2,3}\s+.+$", flags=re.MULTILINE)

PAGE_MARKER_PATTERN = re.compile(r"\[\[PAGE\s+(\d+)\]\]")


def _normalize_text(text: str) -> str:
    return " ".join(text.split()).lower()


def _clean_extracted_text(text: str) -> str:
    raw_lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]

    line_counts = Counter(
        _normalize_text(line) for line in raw_lines if line
    )

    seen_counts: Counter[str] = Counter()
    cleaned_lines: list[str] = []

    for line in raw_lines:
        if not line:
            if cleaned_lines and cleaned_lines[-1] != "":
                cleaned_lines.append("")
            continue

        normalized_line = _normalize_text(line)

        if line.startswith("#") or PAGE_MARKER_PATTERN.search(line):
            cleaned_lines.append(line)
            continue

        if re.fullmatch(r"(?:page\s*)?\d+", normalized_line, flags=re.IGNORECASE):
            continue

        if line_counts[normalized_line] > 3 and len(normalized_line) < 120:
            seen_counts[normalized_line] += 1
            if seen_counts[normalized_line] > 1:
                continue

        if (
            cleaned_lines
            and _normalize_text(cleaned_lines[-1]) == normalized_line
        ):
            continue

        cleaned_lines.append(line)

    cleaned_text = "\n".join(cleaned_lines)
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)
    return cleaned_text.strip()


def _is_duplicate(
    chunk: str,
    existing_chunks: list[str],
    similarity_threshold: float = 0.85,
) -> bool:
    normalized_chunk = _normalize_text(chunk)
    for existing in existing_chunks:
        normalized_existing = _normalize_text(existing)
        ratio = SequenceMatcher(None, normalized_chunk, normalized_existing).ratio()
        if ratio >= similarity_threshold:
            return True
    return False


def _split_by_sections(text: str) -> list[str]:
    matches = list(HEADING_PATTERN.finditer(text))
    if not matches:
        return [text]

    sections = []
    if matches[0].start() > 0:
        preamble = text[: matches[0].start()].strip()
        if preamble:
            sections.append(preamble)

    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        section = text[start:end].strip()
        if section:
            sections.append(section)

    return sections


def _extract_page_number(text: str) -> int | None:
    
    matches = PAGE_MARKER_PATTERN.findall(text)
    if not matches:
        return None
   
    return int(matches[0])


def combine_with_classification(raw_text: str, classified_block: str) -> str:
    if not classified_block:
        return raw_text
    return (
        f"{raw_text}\n\n"
        f"## Structured Summary\n"
        f"{classified_block}"
    )


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[tuple[str, int | None]]:
   

    cleaned_text = _clean_extracted_text(text)
    if not cleaned_text:
        return []

    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", "; ", ": ", " ", ""],
    )

    raw_chunks: list[str] = []

    for section in _split_by_sections(cleaned_text):
        section_tokens_estimate = len(section) // 4
        if section_tokens_estimate <= MAX_SECTION_CHUNK_SIZE:
            raw_chunks.append(section)
        else:
            raw_chunks.extend(splitter.split_text(section))

    logger.info(f"RAW CHUNKS: {len(raw_chunks)}")

    deduplicated: list[tuple[str, int | None]] = []
    seen_texts: list[str] = []

    for chunk in raw_chunks:
        stripped = chunk.strip()

        if not stripped:
            continue
        if len(_normalize_text(stripped)) < MIN_CHUNK_LENGTH:
            continue
        if _is_duplicate(stripped, seen_texts, similarity_threshold=NEAR_DUPLICATE_THRESHOLD):
            continue

        page_number = _extract_page_number(stripped)
        deduplicated.append((stripped, page_number))
        seen_texts.append(stripped)

    logger.info(f"FINAL CHUNKS: {len(deduplicated)}")
    return deduplicated
