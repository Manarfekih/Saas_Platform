SUMMARY_PROMPT_TEMPLATE = """/no_think
You are an expert document analyst.
Create a clean, exhaustive JSON summary using the document coverage below.

Return only valid JSON. No markdown fences, no explanations, no extra text.

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
- Use only information that is explicitly present in the source.
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

Source coverage:
{text}

Relevant extracted items:
{extracted_context_block}

JSON:
""".strip()
