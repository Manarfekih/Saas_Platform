import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class EvalCase:
    id: str
    document_id: int
    question: str
    expected_answer: str | None
    expected_chunk_ids: set[int]
    expected_chunk_indexes: set[int]
    answer_contains: list[str]


def load_cases(path: Path) -> list[EvalCase]:
    cases = []

    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        raw = json.loads(line)
        try:
            cases.append(
                EvalCase(
                    id=str(raw.get("id") or f"line-{line_number}"),
                    document_id=int(raw["document_id"]),
                    question=str(raw["question"]),
                    expected_answer=raw.get("expected_answer"),
                    expected_chunk_ids={int(x) for x in raw.get("expected_chunk_ids", [])},
                    expected_chunk_indexes={
                        int(x) for x in raw.get("expected_chunk_indexes", [])
                    },
                    answer_contains=[str(x) for x in raw.get("answer_contains", [])],
                )
            )
        except KeyError as exc:
            raise ValueError(f"{path}:{line_number} missing required field {exc}") from exc

    return cases
