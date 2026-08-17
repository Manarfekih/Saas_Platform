import logging

from sqlalchemy.orm import Session

from app.services.llm_service import ask_llm
from app.services.rag_service import (
    build_context,
    generate_rag_prompt,
    build_history,
    parse_structured_answer,
    render_answer_as_text,
)
from app.services.chat_memory_service import save_message, get_history
from app.services.retrieval_service import retrieve_chunks_all_documents
from app.services.agent.agent_prompts import GLOBAL_PLANNER_PROMPT
from app.services.agent.agent_helpers import (
    extract_json_object,
    rewrite_question,
    build_source_entry,
    is_greeting_question,
)
from app.services.agent.agent_tools import execute_tool
from app.models.document import Document


logger = logging.getLogger("saas-ia-platform")

def _run_global_planner(
    question: str,
    history: str,
    doc_list: str,
) -> dict:
    rewritten = rewrite_question(question, history)

    prompt = (
        GLOBAL_PLANNER_PROMPT
        .replace("<<DOC_LIST>>", doc_list)
        .replace("<<HISTORY>>", history or "No previous conversation.")
        .replace("<<QUESTION>>", rewritten)
    )

    try:
        raw = ask_llm(prompt)
        raw_text = raw.content if hasattr(raw, "content") else str(raw)
    except Exception as exc:
        logger.error(f"Global planner LLM call failed: {exc}")
        return _global_default_plan(rewritten)

    plan = extract_json_object(raw_text)
    if not plan:
        return _global_default_plan(rewritten)

    plan.setdefault("reformulated_question", rewritten)
    return plan


def _global_default_plan(question: str) -> dict:
    return {
        "action": "tool",
        "tool": "search_chunks",
        "params": {"query": question.strip(), "limit": 8},
        "reformulated_question": question.strip(),
        "scope": "all_documents",
        "target_filename": None,
    }


def _build_context(
    db: Session,
    user_id: int,
    document_id: int | None,
    reformulated: str,
    plan: dict,
    limit: int,
) -> tuple[list, list]:
    if document_id is not None:
        chunks = execute_tool(plan=plan, db=db, document_id=document_id)

        doc = db.query(Document).filter(Document.id == document_id).first()
        filename = doc.filename if doc else f"Document {document_id}"

        sources = [
            build_source_entry(c, document_id=document_id, filename=filename)
            for c in chunks
        ]
        return chunks, sources

    chunks = retrieve_chunks_all_documents(
        db=db, user_id=user_id, query=reformulated, limit=limit,
    )

    if not chunks:
        return [], []

    doc_map = {
        doc.id: doc.filename
        for doc in db.query(Document).filter(Document.user_id == user_id).all()
    }

    sources = [
        build_source_entry(
            c,
            document_id=getattr(c, "document_id", None),
            filename=doc_map.get(getattr(c, "document_id", None), "Unknown Document"),
        )
        for c in chunks
    ]

    return chunks, sources


def agent_answer_global(
    db: Session,
    session_id: int,
    user_id: int,
    question: str,
    limit: int = 8,
) -> dict:
    logger.info(
        f"agent_answer_global session={session_id} "
        f"user={user_id} question={question!r}"
    )

    save_message(db=db, session_id=session_id, role="user", content=question)

    if is_greeting_question(question):
        text = (
            "Hello! Ask me anything about your documents - "
            "I can search across all of them or focus on a specific one."
        )
        save_message(db=db, session_id=session_id, role="assistant", content=text)
        return {
            "session_id": session_id,
            "answer": {"type": "fact", "text": text},
            "sources": [],
            "agent_plan": None,
        }

    history_messages = get_history(db=db, session_id=session_id, limit=10)
    history = build_history(history_messages)

    docs = (
        db.query(Document)
        .filter(Document.user_id == user_id, Document.status == "processed")
        .all()
    )

    doc_list = (
        "\n".join(
            f"- {doc.filename} (type: {doc.doc_type or 'unknown'})"
            for doc in docs
        )
        or "No processed documents found."
    )

    plan = _run_global_planner(
        question=question, history=history, doc_list=doc_list,
    )

    if plan.get("action") == "clarify":
        text = plan.get(
            "clarification_question",
            "Could you be more specific? Which document are you asking about?",
        )
        save_message(db=db, session_id=session_id, role="assistant", content=text)
        return {
            "session_id": session_id,
            "answer": {"type": "fact", "text": text},
            "sources": [],
            "agent_plan": plan,
        }

    reformulated = plan.get("reformulated_question") or question.strip()
    target_filename = plan.get("target_filename")
    target_doc_id = None

    if target_filename and plan.get("scope") == "single_document":
        match = next((d for d in docs if d.filename == target_filename), None)
        if match:
            target_doc_id = match.id

    chunks, sources = _build_context(
        db=db,
        user_id=user_id,
        document_id=target_doc_id,
        reformulated=reformulated,
        plan=plan,
        limit=limit,
    )

    if not chunks:
        text = "I could not find relevant information in your documents."
        save_message(db=db, session_id=session_id, role="assistant", content=text)
        return {
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
        f"Global agent prompt: {len(prompt)} chars, "
        f"{len(chunks)} chunks, scope={plan.get('scope')}"
    )

    response = ask_llm(prompt)
    raw = (
        response.content if hasattr(response, "content") else str(response)
    ).strip()

    structured = (
        parse_structured_answer(raw)
        if raw
        else {"type": "fact", "text": "I could not generate an answer. Please try rephrasing."}
    )

    save_message(
        db=db, session_id=session_id,
        role="assistant", content=render_answer_as_text(structured),
    )

    return {
        "session_id": session_id,
        "answer": structured,
        "sources": sources,
        "agent_plan": {
            "tool": plan.get("tool"),
            "reformulated_question": reformulated,
            "scope": plan.get("scope"),
            "target_filename": target_filename,
        },
    }
