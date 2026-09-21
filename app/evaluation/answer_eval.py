import json
from typing import Any

from app.services.llm_service import ask_llm
from app.services.rag_service import (
    build_context,
    generate_rag_prompt,
    parse_structured_answer,
    render_answer_as_text,
)


def generate_answer(question: str, chunks: list[Any]) -> dict[str, Any]:
    prompt = generate_rag_prompt(
        question=question,
        context=build_context(chunks),
        history="No previous conversation.",
    )
    raw_answer = ask_llm(prompt)
    structured = parse_structured_answer(str(raw_answer))

    return {
        "raw_answer": str(raw_answer),
        "structured_answer": structured,
        "answer_text": render_answer_as_text(structured),
    }


def judge_answer(question: str, expected: str, actual: str) -> dict[str, Any]:
    raw = ask_llm(_judge_prompt(question, expected, actual))

    try:
        parsed = json.loads(str(raw).strip().strip("`"))
    except json.JSONDecodeError:
        return {"score": None, "reason": str(raw)}

    return {
        "score": _parse_score(parsed.get("score")),
        "reason": parsed.get("reason"),
    }


def _judge_prompt(question: str, expected: str, actual: str) -> str:
    return f"""
/no_think

Grade whether the actual answer correctly answers the question using the expected answer.
Return only JSON with keys score and reason.
score must be one of: 0, 0.5, 1.

Question: {question}

Expected answer: {expected}

Actual answer: {actual}
""".strip()


def _parse_score(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
