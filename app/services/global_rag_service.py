import re
from sqlalchemy.orm import Session

from app.models.document import Document
from app.services.retrieval_service import (
    retrieve_chunks,
    retrieve_chunks_all_documents,
)
from app.services.rag_service import (
    build_history,
    parse_structured_answer,
    render_answer_as_text,
)

_STOPWORDS = {
    "a",
    "an",
    "and",
    "about",
    "all",
    "any",
    "are",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "the",
    "this",
    "that",
    "to",
    "what",
    "where",
    "who",
    "why",
    "how",
    "tell",
    "me",
    "please",
    "doc",
    "document",
    "file",
    "candidate",
    "candidate's",
    "her",
    "his",
    "their",
}

_ALL_DOCS_PATTERN = re.compile(
    r"\b(all\s+documents|every\s+document|across\s+all|uploaded\s+documents|my\s+documents)\b",
    flags=re.IGNORECASE,
)

_LIST_PATTERN = re.compile(
    r"\b(list|what\s+are\s+the|which\s+are|name\s+them|enumerate|show\s+me\s+all)\b",
    flags=re.IGNORECASE,
)

_COUNT_PATTERN = re.compile(
    r"\b(how\s+many|number\s+of|count\s+of)\b",
    flags=re.IGNORECASE,
)

_OVERVIEW_PATTERN = re.compile(
    r"\b(what\s+is\s+.*about|what\s+does\s+.*do|summarize|summary|overview)\b",
    flags=re.IGNORECASE,
)


def _normalize_text(text: str) -> str:
    return " ".join(text.split()).lower()


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"\w+", text.lower(), flags=re.UNICODE)
        if len(token) > 1 and token not in _STOPWORDS
    }


def _doc_label(document: Document) -> str:
    return document.filename.rsplit(".", 1)[0].replace("_", " ")


def get_user_documents(db: Session, user_id: int):
    return db.query(Document).filter(Document.user_id == user_id).all()


def _document_score(document: Document, question: str, question_tokens: set[str]) -> float:
    filename = _doc_label(document)
    normalized_filename = _normalize_text(filename)
    filename_tokens = _tokens(filename)
    question_text = _normalize_text(question)
    score = 0.0

    if normalized_filename and normalized_filename in question_text:
        score += 6.0

    overlap = len(filename_tokens & question_tokens)
    score += overlap * 2.5

    if document.doc_type:
        doc_type = document.doc_type.lower()
        if doc_type in question_text:
            score += 2.0

    if document.extracted_text:
        extracted_sample = _normalize_text(document.extracted_text[:5000])
        extracted_tokens = _tokens(document.extracted_text[:5000])
        score += len(extracted_tokens & question_tokens) * 0.8
        if any(token in extracted_sample for token in question_tokens):
            score += 1.0

    if _OVERVIEW_PATTERN.search(question):
        if document.doc_type and document.doc_type.lower() == "cv":
            score += 2.5
        if "cv" in normalized_filename or "resume" in normalized_filename:
            score += 2.5

    return score


def _question_mode(question: str) -> str:
    if _COUNT_PATTERN.search(question):
        return "count"
    if _LIST_PATTERN.search(question):
        return "list"
    if _OVERVIEW_PATTERN.search(question):
        return "overview"
    return "fact"


def _build_context_from_document(
    db: Session,
    document: Document,
    question: str,
    limit: int,
):
    parts = [f"[Document: {document.filename}]"]
    sources = []

    if document.doc_type:
        parts.append(f"Type: {document.doc_type}")

    if document.extracted_text:
        parts.append("Extracted text:")
        parts.append(document.extracted_text[:6000].strip())

    chunks = retrieve_chunks(
        db=db,
        document_id=document.id,
        query=question,
        limit=max(2, min(limit, 4)),
    )

    if chunks:
        parts.append("Relevant chunks:")
        for chunk in chunks:
            parts.append(f"- Chunk {chunk.chunk_index}: {chunk.content}")
            sources.append(
                {
                    "document_id": document.id,
                    "filename": document.filename,
                    "chunk_index": chunk.chunk_index,
                }
            )
    else:
        sources.append(
            {
                "document_id": document.id,
                "filename": document.filename,
                "chunk_index": None,
            }
        )

    return "\n".join(parts).strip(), sources


def _build_context_from_chunks(db: Session, user_id: int, question: str, limit: int):
    chunks = retrieve_chunks_all_documents(
        db=db,
        user_id=user_id,
        query=question,
        limit=limit,
    )

    if not chunks:
        return "", []

    doc_map = {
        doc.id: doc.filename
        for doc in get_user_documents(db, user_id)
    }

    parts = []
    sources = []

    for chunk in chunks:
        filename = doc_map.get(chunk.document_id, f"Document {chunk.document_id}")
        parts.append(f"[Document: {filename} | Chunk {chunk.chunk_index}]\n{chunk.content}")
        sources.append(
            {
                "document_id": chunk.document_id,
                "filename": filename,
                "chunk_index": chunk.chunk_index,
            }
        )

    return "\n\n".join(parts), sources


def answer_global_question(db, session_id, user_id, question, limit=6):
    from app.services.chat_memory_service import get_history, save_message
    from app.services.llm_service import ask_llm

    save_message(db, session_id, "user", question)

    history_messages = get_history(db=db, session_id=session_id, limit=6)
    history = build_history(history_messages)
    question_mode = _question_mode(question)
    all_docs_question = bool(_ALL_DOCS_PATTERN.search(question))
    relevant_documents = [] if all_docs_question else []

    if not all_docs_question:
        question_tokens = _tokens(question)
        docs = [
            doc
            for doc in get_user_documents(db, user_id)
            if doc.status == "processed"
        ]
        scored = [
            (
                _document_score(doc, question, question_tokens),
                doc,
            )
            for doc in docs
        ]
        scored = [item for item in scored if item[0] > 0]
        scored.sort(key=lambda item: item[0], reverse=True)
        relevant_documents = [doc for _, doc in scored[:1]]

    if all_docs_question:
        context, sources = _build_context_from_chunks(db, user_id, question, limit)
        scope = "all_documents"
    elif relevant_documents:
        context, sources = _build_context_from_document(
            db=db,
            document=relevant_documents[0],
            question=question,
            limit=limit,
        )
        scope = "single_document"
    else:
        context, sources = _build_context_from_chunks(db, user_id, question, limit)
        scope = "all_documents"

    if not context:
        answer = {
            "type": "fact",
            "text": "I could not find relevant information in your documents.",
        }

        save_message(db, session_id, "assistant", answer["text"])

        return {
            "session_id": session_id,
            "answer": answer,
            "sources": [],
        }

    prompt = f"""/no_think
You are a global document assistant.
Answer the user's question using only the document context below.
Conversation history is only for understanding references, not for facts.

Question mode: {question_mode}
Question scope: {scope}

Rules:
- If the question is about one specific uploaded document, focus on that document only.
- If the question asks for an overview, summarize the document's purpose and main sections.
- If the question asks for projects, certifications, skills, or other lists, enumerate every distinct item in the context.
- If the answer is not in the context, use type "fact" with text exactly: "I could not find relevant information in your documents."
- Output ONLY a single JSON object.

FORMAT:
{{"type": "fact", "text": "..."}}
{{"type": "overview", "summary": "...", "sections": [{{"label": "...", "text": "..."}}]}}
{{"type": "count", "number": 0, "label": "...", "items": [{{"title": "...", "subtitle": "..."}}]}}
{{"type": "list", "intro": "...", "items": [{{"title": "...", "subtitle": "...", "tags": [], "details": "..."}}]}}

CHAT HISTORY:
{history}

DOCUMENT CONTEXT:
{context}

CURRENT QUESTION:
{question}

JSON ANSWER:
"""

    response = ask_llm(prompt)
    raw = response.content if hasattr(response, "content") else str(response)
    structured_answer = parse_structured_answer(raw)
    answer_text = render_answer_as_text(structured_answer)

    if not answer_text.strip():
        answer_text = "I could not find relevant information in your documents."
        structured_answer = {
            "type": "fact",
            "text": answer_text,
        }

    save_message(db, session_id, "assistant", answer_text)

    return {
        "session_id": session_id,
        "answer": structured_answer,
        "sources": sources,
    }
