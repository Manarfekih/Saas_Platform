import json
import logging

from app.services.llm_service import ask_llm

logger = logging.getLogger("saas-ia-platform")

GREETING_WORDS = {"hello", "hi", "hey", "salut", "bonjour", "coucou", "yo"}


def strip_code_fences(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()
    return cleaned


def extract_json_object(raw_text: str) -> dict | None:
    cleaned = strip_code_fences(raw_text)
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        logger.warning(
            "Planner JSON parse failed, using fallback. raw=%r",
            cleaned[:300],
        )
        return None

    if not isinstance(parsed, dict):
        logger.warning("Planner returned non-object JSON: %r", type(parsed))
        return None

    if "action" not in parsed:
        logger.warning("Planner JSON missing action field: %r", parsed)
        return None

    return parsed


def rewrite_question(question: str, history: str = "") -> str:
    prompt = f"""/no_think
Rewrite the user's question into a clear, concise question.

Rules:
- Keep the original meaning.
- Fix grammar, typos, and broken phrasing.
- Resolve pronouns and vague references using the conversation history.
- Do not add facts that are not present.
- Return only the rewritten question text, with no quotes and no JSON.

CONVERSATION HISTORY:
{history or 'No previous conversation.'}

QUESTION:
{question}

REWRITTEN QUESTION:
""".strip()

    try:
        response = ask_llm(prompt)
        text = response.content if hasattr(response, "content") else str(response)
        text = strip_code_fences(text).strip().strip('"')
        return text or question.strip()
    except Exception as exc:
        logger.warning(f"Question rewrite failed: {exc}")
        return question.strip()


def default_plan(question: str) -> dict:
    return {
        "action": "tool",
        "tool": "search_chunks",
        "params": {"query": question.strip(), "limit": 8},
        "reformulated_question": question.strip(),
    }


def build_source_entry(chunk, document_id: int | None = None, filename: str | None = None) -> dict:
    page_number = getattr(chunk, "page_number", None)
    if isinstance(page_number, str):
        try:
            page_number = int(page_number)
        except ValueError:
            page_number = None

    entry: dict = {
        "chunk_id": getattr(chunk, "chunk_id", None),
        "chunk_index": getattr(chunk, "chunk_index", 0),
        "page_number": page_number,
        "content": getattr(chunk, "content", ""),
        "distance": float(getattr(chunk, "distance", 0.0)),
    }

    if document_id is not None:
        entry["document_id"] = document_id

    if filename is not None:
        entry["filename"] = filename
    elif hasattr(chunk, "document") and chunk.document:
        entry["filename"] = chunk.document.filename

    return entry


def is_greeting_question(question: str) -> bool:
    return question.strip().lower() in GREETING_WORDS
