from __future__ import annotations

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

DOCUMENT_TYPE_KEYWORDS = {
    "cv": [
        "curriculum vitae",
        "resume",
        "experience",
        "education",
        "skills",
        "linkedin",
        "profile",
    ],
    "invoice": [
        "invoice",
        "subtotal",
        "total due",
        "bill to",
        "invoice number",
        "payment terms",
    ],
    "contract": [
        "contract",
        "agreement",
        "party",
        "clause",
        "signature",
        "terms",
    ],
    "report": [
        "report",
        "executive summary",
        "findings",
        "recommendation",
        "methodology",
    ],
}

DOCUMENT_TYPE_PROMPT = """/no_think
You are classifying the overall document type.
Choose exactly one label from: cv, invoice, contract, report, unknown.
Use the document filename and text to decide the best match.
Return only the single label, with no punctuation or explanation.

FILENAME:
{filename}

TEXT:
{text}

LABEL:
""".strip()

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
  "DataCamp - Course Title", "Udemy - Topic", platform names like
  IBM/NVIDIA/Coursera/Udemy/DataCamp followed by a short topic). These
  are very often certifications or short courses with NO further
  description, even if a longer description or technology list appears
  immediately after them in the source text. If a short platform/
  course-style title has no bullet points of its own and is followed
  only by a single short line before the next short title, treat it as
  a standalone certification with no details, rather than attaching
  the following line to it as its description.
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
