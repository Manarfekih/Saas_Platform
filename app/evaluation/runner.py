import json
from pathlib import Path
from typing import Any

from app.db.database import SessionLocal
from app.evaluation.answer_eval import generate_answer, judge_answer
from app.evaluation.cases import EvalCase, load_cases
from app.evaluation.metrics import (
    answer_contains_score,
    average,
    retrieval_metrics,
    token_f1,
)
from app.services.retrieval_service import retrieve_chunks


def run_eval(
    cases_path: Path,
    output_path: Path | None,
    limit: int,
    threshold: float,
    generate_answers: bool,
    judge_answers: bool,
) -> dict[str, Any]:
    results = _evaluate_cases(
        cases=load_cases(cases_path),
        limit=limit,
        threshold=threshold,
        generate_answers=generate_answers,
        judge_answers=judge_answers,
    )
    report = {"summary": _summarize(results), "results": results}

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    return report


def _evaluate_cases(
    cases: list[EvalCase],
    limit: int,
    threshold: float,
    generate_answers: bool,
    judge_answers: bool,
) -> list[dict[str, Any]]:
    db = SessionLocal()
    try:
        return [
            _evaluate_case(db, case, limit, threshold, generate_answers, judge_answers)
            for case in cases
        ]
    finally:
        db.close()


def _evaluate_case(
    db,
    case: EvalCase,
    limit: int,
    threshold: float,
    generate_answers: bool,
    judge_answers: bool,
) -> dict[str, Any]:
    chunks = retrieve_chunks(
        db=db,
        document_id=case.document_id,
        query=case.question,
        limit=limit,
        similarity_threshold=threshold,
    )

    answer = (
        _evaluate_answer(case, chunks, judge_answers)
        if generate_answers
        else {}
    )

    return {
        "id": case.id,
        "document_id": case.document_id,
        "question": case.question,
        "expected_answer": case.expected_answer,
        "expected_chunk_ids": sorted(case.expected_chunk_ids),
        "expected_chunk_indexes": sorted(case.expected_chunk_indexes),
        "answer_contains": case.answer_contains,
        "retrieval": retrieval_metrics(case, chunks),
        "answer": answer,
    }


def _evaluate_answer(
    case: EvalCase,
    chunks: list[Any],
    judge_answers: bool,
) -> dict[str, Any]:
    answer = generate_answer(case.question, chunks)
    answer_text = answer["answer_text"]

    answer["contains_score"] = answer_contains_score(answer_text, case.answer_contains)
    answer["token_f1"] = token_f1(answer_text, case.expected_answer)

    if judge_answers and case.expected_answer:
        answer["llm_judge"] = judge_answer(
            question=case.question,
            expected=case.expected_answer,
            actual=answer_text,
        )

    return answer


def _summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "case_count": len(results),
        "retrieval_hit_rate": average([r["retrieval"]["hit"] for r in results]),
        "retrieval_recall": average([r["retrieval"]["recall"] for r in results]),
        "retrieval_mrr": average([r["retrieval"]["mrr"] for r in results]),
        "answer_contains_score": average(
            [r["answer"].get("contains_score") for r in results]
        ),
        "answer_token_f1": average([r["answer"].get("token_f1") for r in results]),
        "answer_llm_judge_score": average(
            [r["answer"].get("llm_judge", {}).get("score") for r in results]
        ),
    }
