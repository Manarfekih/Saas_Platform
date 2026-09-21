SUMMARY_PROMPT_TEMPLATE = """/no_think
You are an expert document analyst.
Create a clean, exhaustive JSON summary using the document coverage below.

CRITICAL OUTPUT RULES:
- Return exactly one valid JSON object.
- Your first character must be { and your last character must be }.
- Do not write markdown, headings, bullet lists outside JSON, code fences,
  explanations, or any text before/after the JSON.
- Use only information explicitly present in the source.

Required shape:
{
  "title": "Document Title",
  "document_type": "CV | Invoice | Contract | Report | Other",
  "overview": "2-4 sentence plain-text overview",
  "key_information": {
    "people": ["Person 1", "Person 2"],
    "organizations": ["Organization 1"],
    "dates": ["Date 1"],
    "amounts": ["Amount 1"]
  },
  "sections": [
    {
      "title": "Section Name",
      "items": [
        {"name": "Item Name", "description": "Details"}
      ]
    }
  ]
}

Guidelines:
- Cover the document broadly and do not ignore later pages or lower sections.
- Prefer a concise, natural summary over template-like wording.
- Keep section names short and factual.
- If a field is not supported by the document, leave it empty or omit it.
- For CVs: sections often include Personal Info, Skills, Education, Experience, Projects, Certifications, Languages.
- For Invoices: sections often include Vendor, Customer, Line Items, Totals, Payment Terms.
- For Contracts: sections often include Parties, Key Clauses, Dates, Signatures.
- For Reports: sections often include Executive Summary, Findings, Recommendations, Data Points.
- Each item must have a name. Description is optional.
- Output valid JSON only.

Document type:
{document_type}

Filename:
{filename}

Source coverage:
{text}

Relevant extracted items:
{extracted_context_block}

JSON:
""".strip()
