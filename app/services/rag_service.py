import json
import logging

from sqlalchemy.orm import Session  # kept: build_context type hint

logger = logging.getLogger("saas-ia-platform")

MAX_CONTEXT_CHARS = 24000


def build_context(results) -> str:
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


def build_history(history) -> str:
    if not history:
        return "No previous conversation."

    return "\n".join(
        f"{msg.role.upper()}: {msg.content}"
        for msg in history
    )


def generate_rag_prompt(
    question: str,
    context: str,
    history: str,
) -> str:

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
        lines = [f"{structured.get('number', '?')} {structured.get('label', 'items')}:"]
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
            f"Structured answer JSON parse failed. raw={cleaned[:300]!r}"
        )
        return {
            "type": "fact",
            "text": raw_response.strip()
            or "I could not generate an answer from this document.",
        }

    if not isinstance(parsed, dict) or "type" not in parsed:
        logger.warning(
            f"Structured answer missing type field. parsed={str(parsed)[:300]!r}"
        )
        return {
            "type": "fact",
            "text": raw_response.strip()
            or "I could not generate an answer from this document.",
        }

    valid_types = {"list", "count", "overview", "fact"}

    if parsed["type"] not in valid_types:
        logger.warning(f"Unexpected answer type: {parsed['type']!r}")
        parsed["type"] = "fact"
        parsed.setdefault("text", raw_response.strip())

    return parsed