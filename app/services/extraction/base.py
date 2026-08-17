from typing import Iterator
import re


def batch_items(items: list, batch_size: int) -> Iterator[list]:
    """Batch items into chunks of specified size"""
    for index in range(0, len(items), batch_size):
        yield items[index:index + batch_size]


class BaseExtractor:

    @staticmethod
    def normalize_text(text: str) -> str:
        if not text:
            return ""
        return text.strip()

    @staticmethod
    def clean_whitespace(text: str) -> str:
        return re.sub(r"\n{3,}", "\n\n", text)
