from asyncio.log import logger
import re
from collections import Counter
from difflib import SequenceMatcher

from langchain_text_splitters import RecursiveCharacterTextSplitter


DEFAULT_CHUNK_SIZE = 450
DEFAULT_CHUNK_OVERLAP = 50
MIN_CHUNK_LENGTH = 40
NEAR_DUPLICATE_THRESHOLD = 0.88


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

        if re.fullmatch(
            r"(?:page\s*)?\d+",
            normalized_line,
            flags=re.IGNORECASE
        ):
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

    cleaned_text = re.sub(
        r"\n{3,}",
        "\n\n",
        cleaned_text
    )

    return cleaned_text.strip()


def _is_duplicate(
    chunk: str,
    existing_chunks: list[str],
    similarity_threshold: float = 0.85
) -> bool:

    normalized_chunk = _normalize_text(chunk)

    for existing in existing_chunks:

        normalized_existing = _normalize_text(existing)

        ratio = SequenceMatcher(
            None,
            normalized_chunk,
            normalized_existing
        ).ratio()

        if ratio >= similarity_threshold:
            return True

    return False


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
):

    cleaned_text = _clean_extracted_text(text)

    if not cleaned_text:
        return []

    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=[
            "\n\n",
            "\n",
            ". ",
            "; ",
            ": ",
            " ",
            "",
        ],
    )

    raw_chunks = splitter.split_text(cleaned_text)

    logger.info(f"RAW CHUNKS: {len(raw_chunks)}")


    for i, c in enumerate(raw_chunks):
        logger.info(f"Chunk {i}: {len(c)} characters")

    deduplicated_chunks = []

    for chunk in raw_chunks:

        if not chunk.strip():
            continue

        if len(_normalize_text(chunk)) < MIN_CHUNK_LENGTH:
            continue

        if not _is_duplicate(
            chunk,
            deduplicated_chunks,
            similarity_threshold=NEAR_DUPLICATE_THRESHOLD,
        ):
            deduplicated_chunks.append(chunk.strip())

    logger.info(f"FINAL CHUNKS: {len(deduplicated_chunks)}")

    return deduplicated_chunks