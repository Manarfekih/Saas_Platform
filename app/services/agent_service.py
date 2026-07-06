import json
import logging

from sqlalchemy.orm import Session

from app.services.llm_service import ask_llm
from app.services.rag_service import (
    build_context,
    build_history,
    generate_rag_prompt,
    parse_structured_answer,
    render_answer_as_text,
)
from app.services.chat_memory_service import save_message, get_history
from app.services.agent_tools import (
    tool_search_chunks,
    tool_search_section,
    tool_get_all_chunks,
    tool_count_category,
)
from app.services.retrieval_service import retrieve_chunks_all_documents

logger = logging.getLogger("saas-ia-platform")


PLANNER_PROMPT = """/no_think
You are a document-chat planning assistant.

Your job is to read the user's rewritten question and decide the best
retrieval strategy for answering it from the current document.

Available tools:
1. search_chunks - general semantic search across chunks.
   Use when the question is specific, factual, or you are unsure.
   Params: {"query": "<search query>", "limit": <4-12>}

2. search_section - retrieve chunks that look like a named section.
   Use when the question is about a section-like concept or heading,
   even if the user used different wording. Examples: skills,
   competences, abilities, experience, projects, education,
   certifications, languages, clauses, line items.
   Params: {"section_name": "<section heading>", "limit": <8-16>}

3. get_all_chunks - read the whole document in order.
   Use for overview, summary, or broad "what is this about" requests.
   Params: {"limit": <16-24>}

4. count_category - retrieve repeated item categories.
   Use for "how many" or "list all" questions when the answer is
   naturally a category of items such as skills, projects,
   certifications, education items, clauses, or line items.
   Params: {"category": "<category name>", "limit": <16-20>}

Return only a single JSON object.

For tool actions:
{"action": "tool", "tool": "<tool name>", "params": {<params>},
 "reformulated_question": "<cleaned version of the question>"}

For clarification:
{"action": "clarify", "clarification_question": "<one short question>"}

Rules:
- Rewrite the user's question so it is clear and grammatical.
- Resolve pronouns and vague references using the conversation history.
- Keep the original meaning.
- Prefer search_section when the question is about a clear section-like concept.
- Prefer count_category for list/count questions about repeated items.
- Prefer get_all_chunks only for broad overview requests.
- Default to search_chunks if unsure.

CONVERSATION HISTORY:
<<HISTORY>>

USER QUESTION:
<<QUESTION>>

JSON:
""".strip()


GLOBAL_PLANNER_PROMPT = """/no_think
You are a global document-chat planning assistant.

The user has uploaded multiple documents. Decide whether the question
is about one specific document or all documents, then choose the best
retrieval tool.

Available tools:
1. search_chunks - general semantic search.
2. search_section - retrieve chunks from a section-like concept.
3. get_all_chunks - read the whole document in order.
4. count_category - retrieve repeated item categories.

Return only a single JSON object.

Required shape for tool actions:
{
  "action": "tool",
  "tool": "<tool name>",
  "params": {<params>},
  "reformulated_question": "<cleaned question>",
  "scope": "single_document" | "all_documents",
  "target_filename": "<filename if scope=single_document, else null>"
}

For clarification:
{"action": "clarify", "clarification_question": "<one short question>"}

Rules:
- Rewrite the question clearly and naturally.
- Resolve vague references using conversation history.
- If the question clearly points to one uploaded file, set scope to
  single_document and target_filename to that exact filename.
- Use all_documents for broad or cross-document questions.
- Prefer search_section and count_category when the question is about
  section-like concepts or repeated item categories.
- Default to search_chunks if unsure.

USER'S DOCUMENTS:
<<DOC_LIST>>

CONVERSATION HISTORY:
<<HISTORY>>

USER QUESTION:
<<QUESTION>>

JSON:
""".strip()


def _strip_code_fences(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()
    return cleaned


def _extract_json_object(raw_text: str) -> dict | None:
    cleaned = _strip_code_fences(raw_text)
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


def _rewrite_question(question: str, history: str = "") -> str:
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
        text = _strip_code_fences(text)
        text = text.strip().strip('"')
        return text or question.strip()
    except Exception as exc:
        logger.warning(f"Question rewrite failed: {exc}")
        return question.strip()


def _run_planner(question: str, history: str) -> dict:
    rewritten_question = _rewrite_question(question, history)

    prompt = (
        PLANNER_PROMPT.replace("<<HISTORY>>", history or "No previous conversation.")
        .replace("<<QUESTION>>", rewritten_question)
    )

    try:
        raw = ask_llm(prompt)
        raw_text = raw.content if hasattr(raw, "content") else str(raw)
    except Exception as exc:
        logger.error(f"Planner LLM call failed: {exc}")
        return _default_plan(rewritten_question)

    plan = _extract_json_object(raw_text)
    if not plan:
        return _default_plan(rewritten_question)

    logger.info(f"Planner decision: {plan}")
    plan.setdefault("reformulated_question", rewritten_question)
    return plan


def _default_plan(question: str) -> dict:
    cleaned_question = question.strip()
    return {
        "action": "tool",
        "tool": "search_chunks",
        "params": {"query": cleaned_question, "limit": 8},
        "reformulated_question": cleaned_question,
    }


def _execute_tool(
    plan: dict,
    db: Session,
    document_id: int,
) -> list:
    tool_name = plan.get("tool", "search_chunks")
    params = plan.get("params", {})

    logger.info(f"Executing tool={tool_name} params={params}")

    if tool_name == "search_chunks":
        return tool_search_chunks(
            db=db,
            document_id=document_id,
            query=params.get("query", ""),
            limit=params.get("limit", 8),
        )

    if tool_name == "search_section":
        return tool_search_section(
            db=db,
            document_id=document_id,
            section_name=params.get("section_name", ""),
            limit=params.get("limit", 8),
        )

    if tool_name == "get_all_chunks":
        return tool_get_all_chunks(
            db=db,
            document_id=document_id,
            limit=params.get("limit", 20),
        )

    if tool_name == "count_category":
        return tool_count_category(
            db=db,
            document_id=document_id,
            category=params.get("category", ""),
            limit=params.get("limit", 20),
        )

    logger.warning(
        f"Unknown tool name: {tool_name!r}, falling back to search_chunks"
    )
    return tool_search_chunks(
        db=db,
        document_id=document_id,
        query=params.get("query", ""),
        limit=8,
    )


def agent_answer(
    db: Session,
    document_id: int,
    session_id: int,
    question: str,
) -> dict:

    logger.info(
        f"agent_answer doc={document_id} session={session_id} question={question!r}"
    )

    save_message(
        db=db,
        session_id=session_id,
        role="user",
        content=question,
    )

    greeting = question.strip().lower()
    if greeting in {"hello", "hi", "hey", "salut", "bonjour", "coucou", "yo"}:
        answer_text = (
            "Hello! Ask me anything about this document - I'll do my best to answer using its contents."
        )
        save_message(
            db=db,
            session_id=session_id,
            role="assistant",
            content=answer_text,
        )
        return {
            "document_id": document_id,
            "session_id": session_id,
            "answer": {"type": "fact", "text": answer_text},
            "sources": [],
            "agent_plan": None,
        }

    history_messages = get_history(db=db, session_id=session_id, limit=10)
    history = build_history(history_messages)

    plan = _run_planner(question=question, history=history)

    if plan.get("action") == "clarify":
        clarification = plan.get(
            "clarification_question",
            "Could you rephrase your question? I want to make sure I understand what you're looking for.",
        )
        save_message(
            db=db,
            session_id=session_id,
            role="assistant",
            content=clarification,
        )
        return {
            "document_id": document_id,
            "session_id": session_id,
            "answer": {"type": "fact", "text": clarification},
            "sources": [],
            "agent_plan": plan,
        }

    chunks = _execute_tool(plan=plan, db=db, document_id=document_id)
    reformulated = plan.get("reformulated_question") or question.strip()

    if not chunks:
        answer_text = (
            "I could not find relevant information in this document for: "
            f"{reformulated}"
        )
        save_message(
            db=db,
            session_id=session_id,
            role="assistant",
            content=answer_text,
        )
        return {
            "document_id": document_id,
            "session_id": session_id,
            "answer": {"type": "fact", "text": answer_text},
            "sources": [],
            "agent_plan": plan,
        }

    context = build_context(chunks)
    prompt = generate_rag_prompt(
        question=reformulated,
        context=context,
        history=history,
    )

    logger.info(
        f"Agent answer prompt: {len(prompt)} chars, {len(chunks)} chunks, tool={plan.get('tool')}"
    )

    response = ask_llm(prompt)
    answer_text = response.content if hasattr(response, "content") else str(response)
    answer_text = answer_text.strip()

    if not answer_text:
        logger.warning(
            f"Empty agent answer for doc={document_id} question={question!r} reformulated={reformulated!r}"
        )
        structured = {
            "type": "fact",
            "text": (
                f"I think you mean: {reformulated}. Please try asking that version."
            ),
        }
    else:
        structured = parse_structured_answer(answer_text)

    save_message(
        db=db,
        session_id=session_id,
        role="assistant",
        content=render_answer_as_text(structured),
    )

    return {
        "document_id": document_id,
        "session_id": session_id,
        "answer": structured,
        "sources": [
            {
                "chunk_id": c.chunk_id,
                "chunk_index": c.chunk_index,
                "distance": float(c.distance),
            }
            for c in chunks
        ],
        "agent_plan": {
            "tool": plan.get("tool"),
            "reformulated_question": reformulated,
            "params": plan.get("params"),
        },
    }


def _build_global_context(
    db: Session,
    user_id: int,
    document_id: int | None,
    reformulated: str,
    plan: dict,
    limit: int,
) -> tuple[list, list]:

    if document_id is not None:
        chunks = _execute_tool(
            plan=plan,
            db=db,
            document_id=document_id,
        )
        from app.models.document import Document

        doc = db.query(Document).filter(Document.id == document_id).first()
        filename = doc.filename if doc else f"Document {document_id}"
        sources = [
            {
                "document_id": c.chunk_id,
                "filename": filename,
                "chunk_index": c.chunk_index,
                "distance": float(c.distance),
            }
            for c in chunks
        ]
        return chunks, sources

    chunks = retrieve_chunks_all_documents(
        db=db,
        user_id=user_id,
        query=reformulated,
        limit=limit,
    )

    if not chunks:
        return [], []

    from app.models.document import Document

    doc_map = {
        doc.id: doc.filename
        for doc in db.query(Document).filter(Document.user_id == user_id).all()
    }

    sources = [
        {
            "document_id": c.document_id,
            "filename": doc_map.get(c.document_id, f"Document {c.document_id}"),
            "chunk_index": c.chunk_index,
            "distance": float(c.distance),
        }
        for c in chunks
    ]

    return chunks, sources


def _run_global_planner(question: str, history: str, doc_list: str) -> dict:
    rewritten_question = _rewrite_question(question, history)
    prompt = (
        GLOBAL_PLANNER_PROMPT.replace("<<DOC_LIST>>", doc_list)
        .replace("<<HISTORY>>", history or "No previous conversation.")
        .replace("<<QUESTION>>", rewritten_question)
    )

    try:
        raw = ask_llm(prompt)
        raw_text = raw.content if hasattr(raw, "content") else str(raw)
    except Exception as exc:
        logger.error(f"Global planner LLM call failed: {exc}")
        return {
            "action": "tool",
            "tool": "search_chunks",
            "params": {"query": rewritten_question, "limit": 8},
            "reformulated_question": rewritten_question,
            "scope": "all_documents",
            "target_filename": None,
        }

    plan = _extract_json_object(raw_text)
    if not plan:
        return {
            "action": "tool",
            "tool": "search_chunks",
            "params": {"query": rewritten_question, "limit": 8},
            "reformulated_question": rewritten_question,
            "scope": "all_documents",
            "target_filename": None,
        }

    plan.setdefault("reformulated_question", rewritten_question)
    return plan


def agent_answer_global(
    db: Session,
    session_id: int,
    user_id: int,
    question: str,
    limit: int = 8,
) -> dict:

    logger.info(
        f"agent_answer_global session={session_id} user={user_id} question={question!r}"
    )

    save_message(db=db, session_id=session_id, role="user", content=question)

    greeting = question.strip().lower()
    if greeting in {"hello", "hi", "hey", "salut", "bonjour", "coucou", "yo"}:
        text = (
            "Hello! Ask me anything about your documents - I can search across all of them or focus on a specific one."
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

    from app.models.document import Document

    docs = (
        db.query(Document)
        .filter(Document.user_id == user_id, Document.status == "processed")
        .all()
    )

    doc_list = "\n".join(
        f"- {doc.filename} (type: {doc.doc_type or 'unknown'})"
        for doc in docs
    ) or "No processed documents found."

    plan = _run_global_planner(question=question, history=history, doc_list=doc_list)

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

    chunks, sources = _build_global_context(
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
        question=reformulated,
        context=context,
        history=history,
    )

    logger.info(
        f"Global agent prompt: {len(prompt)} chars, {len(chunks)} chunks, scope={plan.get('scope')}"
    )

    response = ask_llm(prompt)
    raw = response.content if hasattr(response, "content") else str(response)
    raw = raw.strip()

    if not raw:
        structured = {
            "type": "fact",
            "text": "I could not generate an answer. Please try rephrasing.",
        }
    else:
        structured = parse_structured_answer(raw)

    save_message(
        db=db,
        session_id=session_id,
        role="assistant",
        content=render_answer_as_text(structured),
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




