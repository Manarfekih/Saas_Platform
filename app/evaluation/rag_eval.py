import argparse
import json
from pathlib import Path

from app.evaluation.runner import run_eval


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate document retrieval and RAG answer generation."
    )
    parser.add_argument("cases", type=Path, help="JSONL file with evaluation cases.")
    parser.add_argument("--output", type=Path, help="Write a JSON report to this path.")
    parser.add_argument("--limit", type=int, default=5, help="Retrieved chunks per case.")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.7,
        help="Cosine distance threshold. Lower is stricter.",
    )
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Generate answers using the retrieved context.",
    )
    parser.add_argument(
        "--judge",
        action="store_true",
        help="Use the configured LLM to grade generated answers against expected answers.",
    )
    args = parser.parse_args()

    report = run_eval(
        cases_path=args.cases,
        output_path=args.output,
        limit=args.limit,
        threshold=args.threshold,
        generate_answers=args.generate or args.judge,
        judge_answers=args.judge,
    )
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
