import logging

from sqlalchemy.orm import Session

from app.models.document import Document as DocumentModel
from app.services.llm_service import ask_llm
from app.services.rag_service import (
    build_context,
    generate_rag_prompt,
    build_history,
    parse_structured_answer,
    render_answer_as_text,
)
from app.services.chat_memory_service import save_message, get_history
from app.services.agent.agent_tools import (
    execute_tool,
    tool_search_chunks,
    tool_search_section,
    tool_get_all_chunks,
    tool_count_category,
)
from app.services.agent.agent_prompts import PLANNER_PROMPT
from app.services.agent.agent_helpers import (
    extract_json_object,
    rewrite_question,
    default_plan,
    build_source_entry,
    is_greeting_question,
)

logger = logging.getLogger("saas-ia-platform")

def _run_planner(question: str, history: str) -> dict:
    rewritten = rewrite_question(question, history)

    prompt = (
        PLANNER_PROMPT
        .replace("<<HISTORY>>", history or "No previous conversation.")
        .replace("<<QUESTION>>", rewritten)
    )

    try:
        raw = ask_llm(prompt)
        raw_text = raw.content if hasattr(raw, "content") else str(raw)
    except Exception as exc:
        logger.error(f"Planner LLM call failed: {exc}")
        return default_plan(rewritten)

    plan = extract_json_object(raw_text)
    if not plan:
        return default_plan(rewritten)

    logger.info(f"Planner decision: {plan}")
    plan.setdefault("reformulated_question", rewritten)
    return plan


def agent_answer(
    db: Session,
    document_id: int,
    session_id: int,
    question: str,
) -> dict:
    logger.info(
        f"agent_answer doc={document_id} session={session_id} question={question!r}"
    )

    save_message(db=db, session_id=session_id, role="user", content=question)

    if is_greeting_question(question):
        text = (
            "Hello! Ask me anything about this document - "
            "I'll do my best to answer using its contents."
        )
        save_message(db=db, session_id=session_id, role="assistant", content=text)
        return {
            "document_id": document_id,
            "session_id": session_id,
            "answer": {"type": "fact", "text": text},
            "sources": [],
            "agent_plan": None,
        }

    history_messages = get_history(db=db, session_id=session_id, limit=10)
    history = build_history(history_messages)

    plan = _run_planner(question=question, history=history)

    if plan.get("action") == "clarify":
        clarification = plan.get(
            "clarification_question",
            "Could you rephrase your question? "
            "I want to make sure I understand what you're looking for.",
        )
        save_message(db=db, session_id=session_id, role="assistant", content=clarification)
        return {
            "document_id": document_id,
            "session_id": session_id,
            "answer": {"type": "fact", "text": clarification},
            "sources": [],
            "agent_plan": plan,
        }

    chunks = execute_tool(plan=plan, db=db, document_id=document_id)
    reformulated = plan.get("reformulated_question") or question.strip()

    if not chunks:
        text = f"I could not find relevant information in this document for: {reformulated}"
        save_message(db=db, session_id=session_id, role="assistant", content=text)
        return {
            "document_id": document_id,
            "session_id": session_id,
            "answer": {"type": "fact", "text": text},
            "sources": [],
            "agent_plan": plan,
        }

    context = build_context(chunks)
    prompt = generate_rag_prompt(
        question=reformulated, context=context, history=history,
    )

    logger.info(
        f"Agent prompt: {len(prompt)} chars, "
        f"{len(chunks)} chunks, tool={plan.get('tool')}"
    )

    response = ask_llm(prompt)
    answer_text = (
        response.content if hasattr(response, "content") else str(response)
    ).strip()

    if not answer_text:
        logger.warning(f"Empty answer doc={document_id} question={question!r}")
        structured = {
            "type": "fact",
            "text": f"I think you mean: {reformulated}. Please try asking that version.",
        }
    else:
        structured = parse_structured_answer(answer_text)

    save_message(
        db=db, session_id=session_id,
        role="assistant", content=render_answer_as_text(structured),
    )

    doc = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    doc_filename = doc.filename if doc else None

    return {
        "document_id": document_id,
        "session_id": session_id,
        "answer": structured,
        "sources": [
            build_source_entry(c, document_id=document_id, filename=doc_filename)
            for c in chunks
        ],
        "agent_plan": {
            "tool": plan.get("tool"),
            "reformulated_question": reformulated,
            "params": plan.get("params"),
        },
    }
