from app.services.llm_service import ask_llm


VALID_TYPES = {
    "resume",
    "invoice",
    "contract",
    "medical",
    "research",
    "generic",
}


def detect_document_type(text: str) -> str:

    prompt = f"""
You are a document classifier.

Classify the document into exactly ONE category:

resume
invoice
contract
medical
research
generic

Rules:
- Return ONLY the category name.
- Return exactly one word.
- No explanation.
- No punctuation.

Document:

{text[:3000]}
"""

    response = ask_llm(prompt)

    result = (
        response.content
        if hasattr(response, "content")
        else str(response)
    )

    result = result.strip().lower()

    # Defensive cleanup
    result = result.split()[0]

    if result not in VALID_TYPES:
        return "generic"

    return result