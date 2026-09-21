import json
import re
from typing import Any, Dict, Optional

THINK_PATTERN = re.compile(r"<think>.*?</think>", flags=re.DOTALL)
FENCE_PATTERN = re.compile(r"^```(?:json)?\s*(.*?)\s*```$", flags=re.DOTALL)


def parse_llm_json(raw: str) -> Optional[Dict[str, Any]]:
    if not raw:
        return None

    text = THINK_PATTERN.sub("", raw.strip()).strip()
    fence_match = FENCE_PATTERN.match(text)
    if fence_match:
        text = fence_match.group(1).strip()

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            pass

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None
