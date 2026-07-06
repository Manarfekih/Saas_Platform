import re
import json
import logging

from sqlalchemy.orm import Session


from app.services.retrieval_service import retrieve_chunks
from app.services.llm_service import ask_llm

from app.services.chat_memory_service import (
    save_message,
    get_history,
)


logger = logging.getLogger("saas-ia-platform")

MAX_CONTEXT_CHARS = 24000


_ENUMERATION_PATTERN = re.compile(
    r"\b(all|every|list|enumerate|each|how many"
    r"|what\s+are\s+the|what\s+\w+\s+did|which\s+\w+)\b",
    flags=re.IGNORECASE,
)

DEFAULT_RETRIEVAL_LIMIT = 8
ENUMERATION_RETRIEVAL_LIMIT = 16


DEFAULT_SIMILARITY_THRESHOLD = 0.7
ENUMERATION_SIMILARITY_THRESHOLD = 0.85


def _is_enumeration_question(question: str) -> bool:
    return bool(_ENUMERATION_PATTERN.search(question))


_GREETING_PATTERN = re.compile(
    r"^\s*(hello|hi|hey|salut|bonjour|coucou|yo)\s*[!.?]*\s*$",
    flags=re.IGNORECASE,
)


def _is_greeting(question: str) -> bool:
    return bool(_GREETING_PATTERN.match(question))


def build_context(results):

    context_parts = []

    current_size = 0


    for chunk in results:

        text = chunk.content.strip()

        if not text:
            continue


        block = (
            f"[DOCUMENT CHUNK {chunk.chunk_index}]\n"
            f"{text}\n"
        )


        if current_size + len(block) > MAX_CONTEXT_CHARS:
            break


        context_parts.append(block)

        current_size += len(block)



    return "\n\n".join(context_parts)




def build_history(history):

    if not history:
        return "No previous conversation."


    messages = []


    for msg in history:

        messages.append(
            f"{msg.role.upper()}: {msg.content}"
        )


    return "\n".join(messages)





def generate_rag_prompt(
    question: str,
    context: str,
    history: str,
):

    return f"""/no_think

You are an AI document assistant. The uploaded document can be of any
type (resume, invoice, contract, report, letter, form, etc).

You answer questions about the document using ONLY the document
context below. Conversation history is only for understanding
previous questions, not as a source of facts.

CONTENT RULES:
- Do not invent information that is not in the document context.
- If the question asks for a list, count, or "all/every" of
  something, scan the ENTIRE document context provided and enumerate
  every distinct item you find, even if they appear in different
  chunks or under different headings.
- If the answer is not in the document context, use type "fact" with
  text exactly: "I could not find that information in the document."

OUTPUT FORMAT — respond with ONLY a single JSON object, no markdown
code fences, no preamble, no explanation outside the JSON. Choose the
"type" field based on the question, and follow that type's exact
shape:

TYPE "list" — for "what are the X", "list the X" questions:
{{"type": "list", "intro": "<optional one-line intro, or null>",
  "items": [{{"title": "<short item name>",
              "subtitle": "<one-line tagline/description or null>",
              "tags": ["<short tag>", "..."],
              "details": "<longer description or null>"}}]}}

TYPE "count" — for "how many X" questions:
{{"type": "count", "number": <integer>, "label": "<what was counted,
  e.g. 'certifications'>",
  "items": [{{"title": "<short item name>", "subtitle": "<detail or null>"}}]}}

TYPE "overview" — for "what is this about", "summarize" questions:
{{"type": "overview", "summary": "<1-2 plain sentences>",
  "sections": [{{"label": "<short category name, e.g. 'Focus'>",
                 "text": "<one-line plain text detail>"}}]}}

TYPE "fact" — for single-fact questions or "not found" answers:
{{"type": "fact", "text": "<the direct answer, one short sentence>"}}

Rules for the JSON:
- "tags" should be short keywords (technologies, dates, categories) —
  omit the field or use an empty list if not applicable.
- Never put markdown syntax (**, -, #) inside any string value — the
  frontend renders these fields as plain styled text, not markdown.
- Keep "title"/"label" fields short (a few words). Keep "subtitle"/
  "text" fields to one line. Use "details" only for genuinely longer
  content the question asked for explicitly.
- Output valid JSON only — no trailing commas, no comments.


CHAT HISTORY:

{history}



DOCUMENT CONTEXT:

{context}



CURRENT QUESTION:

{question}



JSON ANSWER:

""".strip()


def render_answer_as_text(structured: dict) -> str:
    

    answer_type = structured.get("type")

    if answer_type == "fact":
        return structured.get("text", "")

    if answer_type == "overview":
        lines = [structured.get("summary", "")]
        for section in structured.get("sections", []):
            lines.append(f"{section.get('label', '')}: {section.get('text', '')}")
        return "\n".join(line for line in lines if line)

    if answer_type == "count":
        lines = [
            f"{structured.get('number', '?')} {structured.get('label', 'items')}:"
        ]
        for item in structured.get("items", []):
            lines.append(f"- {item.get('title', '')}")
        return "\n".join(lines)

    if answer_type == "list":
        lines = []
        if structured.get("intro"):
            lines.append(structured["intro"])
        for item in structured.get("items", []):
            title = item.get("title", "")
            subtitle = item.get("subtitle")
            lines.append(f"- {title}" + (f": {subtitle}" if subtitle else ""))
        return "\n".join(lines)

  
    return json.dumps(structured)


def parse_structured_answer(raw_response: str) -> dict:
   

    cleaned = raw_response.strip()

    
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        logger.warning(
            f"Structured answer JSON parse failed, falling back to "
            f"plain fact. raw_response={cleaned[:300]!r}"
        )
        return {"type": "fact", "text": raw_response.strip() or
                "I could not generate an answer from this document."}

    if not isinstance(parsed, dict) or "type" not in parsed:
        logger.warning(
            f"Structured answer missing type field, falling back. "
            f"parsed={str(parsed)[:300]!r}"
        )
        return {"type": "fact", "text": raw_response.strip() or
                "I could not generate an answer from this document."}

    valid_types = {"list", "count", "overview", "fact"}

    if parsed["type"] not in valid_types:
        logger.warning(f"Unexpected structured answer type: {parsed['type']!r}")
        parsed["type"] = "fact"
        parsed.setdefault("text", raw_response.strip())

    return parsed






def answer_question(
    db: Session,
    document_id: int,
    session_id: int,
    question: str,
    limit: int = None,
):


    logger.info(
        f"""
        RAG document={document_id}
        session={session_id}
        question={question}
        """
    )


    
    is_enumeration = _is_enumeration_question(question)

    if limit is None:
        limit = (
            ENUMERATION_RETRIEVAL_LIMIT
            if is_enumeration
            else DEFAULT_RETRIEVAL_LIMIT
        )

    similarity_threshold = (
        ENUMERATION_SIMILARITY_THRESHOLD
        if is_enumeration
        else DEFAULT_SIMILARITY_THRESHOLD
    )



    save_message(
        db=db,
        session_id=session_id,
        role="user",
        content=question
    )


    
    if _is_greeting(question):

        answer_text = (
            "Hello! Ask me anything about this document and I'll do "
            "my best to answer using its contents."
        )

        save_message(
            db=db,
            session_id=session_id,
            role="assistant",
            content=answer_text
        )

        return {
            "document_id": document_id,
            "session_id": session_id,
           
            "answer": {"type": "fact", "text": answer_text},
            "sources": []
        }



    # history loading


    history_messages = get_history(
        db=db,
        session_id=session_id,
        limit=10
    )


    history = build_history(
        history_messages
    )



    #  Retrieve document chunks


    chunks = retrieve_chunks(
        db=db,
        document_id=document_id,
        query=question,
        limit=limit,
        similarity_threshold=similarity_threshold,
    )



    if not chunks:


        answer_text = (
            "I could not find relevant information "
            "in this document."
        )


        save_message(
            db=db,
            session_id=session_id,
            role="assistant",
            content=answer_text
        )


        return {

            "document_id": document_id,

            "answer": {"type": "fact", "text": answer_text},

            "sources": []

        }




    # Build context


    context = build_context(
        chunks
    )




    # rag prompt


    prompt = generate_rag_prompt(

        question=question,

        context=context,

        history=history

    )


    
    logger.info(
        f"RAG prompt size: {len(prompt)} chars, "
        f"{len(chunks)} chunks, retrieval_limit={limit}"
    )




    # Ask Qwen


    response = ask_llm(
        prompt
    )



    logger.info(
        f"Raw LLM response type={type(response).__name__}, "
        f"repr={repr(response)[:300]}"
    )


    answer_text = (

        response.content

        if hasattr(response,"content")

        else str(response)

    )


    answer_text = answer_text.strip()


 
    if not answer_text:
        logger.warning(
            f"Empty answer for document={document_id} "
            f"session={session_id} question={question!r} "
            f"chunks_retrieved={len(chunks)} prompt_chars={len(prompt)}"
        )
        structured_answer = {
            "type": "fact",
            "text": (
                "I could not generate an answer from this document. "
                "Please try rephrasing your question."
            ),
        }
    else:
        structured_answer = parse_structured_answer(answer_text)




    # Save assistant answer

    
    history_text = render_answer_as_text(structured_answer)

    save_message(

        db=db,

        session_id=session_id,

        role="assistant",

        content=history_text

    )




    return {


        "document_id": document_id,


        "session_id": session_id,


        "answer": structured_answer,


        "sources":[


            {

                "chunk_id": c.chunk_id,

                "chunk_index": c.chunk_index,

                "distance": float(c.distance)

            }

            for c in chunks

        ]

    }