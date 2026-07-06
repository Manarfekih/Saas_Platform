import json
import logging

from app.services.llm_service import ask_llm

logger = logging.getLogger("saas-ia-platform")



CATEGORY_SETS: dict[str, list[str]] = {

    "cv": [
        "contact_info",
        "summary",
        "skill",
        "formal_education",   
        "certification",      
        "project",
        "experience",          
        "leadership",          
        "language",
        "other",
    ],

    "invoice": [
        "metadata",            
        "vendor",
        "customer",
        "line_item",          
        "subtotal",
        "tax",
        "total",
        "payment_terms",
        "other",
    ],

    "contract": [
        "metadata",            
        "party",                
        "clause",                
        "definition",           
        "signature",
        "other",
    ],

    "report": [
        "metadata",             
        "executive_summary",
        "finding",               
        "recommendation",
        "data_point",            
        "other",
    ],
}


GENERIC_CATEGORIES = [
    "metadata",       
    "key_fact",       
    "list_item",      
    "description",    
    "other",
]


def _categories_for(doc_type):
    if not doc_type:
        return GENERIC_CATEGORIES
    return CATEGORY_SETS.get(doc_type.lower(), GENERIC_CATEGORIES)


CLASSIFICATION_PROMPT = """/no_think
You are a structured-data extractor. You will be given the raw
extracted text of a document of type "{doc_type}". Your job is to
break it into a clean, flat list of distinct items, each tagged with
exactly one category.

Categories you may use: {categories}

Rules:
- Each item must be a single, self-contained real-world entity (one
  degree, one certification, one project, one invoice line, one
  clause, one finding, etc., depending on what is present in this
  document). Do not merge unrelated items together.
- Be especially careful with short course/certification names (e.g.
  "DataCamp — Course Title", "Udemy — Topic", platform names like
  IBM/NVIDIA/Coursera/Udemy/DataCamp followed by a short topic). These
  are very often certifications or short courses with NO further
  description, even if a longer description or technology list
  appears immediately after them in the source text — that
  description may actually belong to a separate, larger project
  nearby that the extraction step placed adjacent to it by mistake.
  If a short platform/course-style title has no bullet points of its
  own and is followed only by a single short line before the next
  short title, treat it as a standalone certification with no
  details, rather than attaching the following line to it as its
  description.
- Only include a "dates" field if a date or date range is clearly and
  unambiguously associated with that specific item in the source text.
  If you are not sure which item a date belongs to, omit the dates
  field for that item rather than guessing.
- Use the category whose meaning best matches the item's real-world
  nature, even if the source text grouped it under a different or
  misleading heading. For example, a short online course or
  professional certification should be tagged as a certification-type
  category even if the source document listed it under an education
  heading; an invoice line item should be tagged as such even if it
  appears in a table with mixed content.
- Do not invent items that are not in the source text. Do not invent
  dates, organizations, amounts, or technologies that are not
  explicitly present.
- Output ONLY a JSON array, no preamble, no markdown code fences, no
  explanation. Each array element must be an object with this shape:
  {{"category": "<one of the categories above>", "title": "<short title>",
   "organization": "<org/party name or null>", "dates": "<date or null>",
   "amount": "<numeric amount or null, only for invoice-like documents>",
   "details": "<full original descriptive text for this item, verbatim
   from the source where possible>"}}

SOURCE TEXT:

{text}

JSON ARRAY:
""".strip()


def classify_sections(raw_text, doc_type=None):
   

    categories = _categories_for(doc_type)

    prompt = CLASSIFICATION_PROMPT.format(
        doc_type=doc_type or "unknown",
        categories=", ".join(categories),
        text=raw_text[:8000], 
    )

    try:
        response = ask_llm(prompt)
    except Exception as e:
        logger.error(f"Classification LLM call failed: {str(e)}")
        return []

    cleaned = response.strip()

   
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()

    try:
        items = json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(
            f"Classification JSON parse failed: {str(e)} | "
            f"raw_response={cleaned[:300]!r}"
        )
        return []

    if not isinstance(items, list):
        logger.error(
            f"Classification did not return a list: {type(items)}"
        )
        return []

    valid_items = []

    for item in items:

        if not isinstance(item, dict):
            continue

        category = item.get("category")

        if category not in categories:
            
            logger.warning(
                f"Unexpected category {category!r} for doc_type="
                f"{doc_type!r}, coercing to 'other'"
            )
            item["category"] = "other"

        if not item.get("title"):
            continue

        valid_items.append(item)

    logger.info(
        f"Classification (doc_type={doc_type}) produced "
        f"{len(valid_items)} valid items out of {len(items)} raw items"
    )

    return valid_items


def render_classified_block(items, doc_type=None):
    

    if not items:
        return ""

    categories = _categories_for(doc_type)

    by_category = {}

    for item in items:
        by_category.setdefault(item["category"], []).append(item)

    blocks = []

    for category in categories:

        category_items = by_category.get(category)

        if not category_items:
            continue

        blocks.append(f"## {category}")

        for item in category_items:

            line = f"- {item['title']}"

            if item.get("organization"):
                line += f" ({item['organization']})"

            if item.get("amount"):
                line += f" — {item['amount']}"

            if item.get("dates"):
                line += f" — {item['dates']}"

            blocks.append(line)

            if item.get("details"):
                blocks.append(f"  {item['details']}")

    return "\n".join(blocks)