import os

VISION_MODEL = os.getenv(
    "VISION_MODEL",
    "qwen2.5vl:7b",
)

OCR_DPI = int(os.getenv("OCR_DPI", "200"))
OCR_BATCH_SIZE = max(1, int(os.getenv("OCR_BATCH_SIZE", "1")))
OCR_MAX_SIDE = int(os.getenv("OCR_MAX_SIDE", "1500"))
OCR_REQUEST_TIMEOUT = int(os.getenv("OCR_REQUEST_TIMEOUT", "240"))

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://ollama:11434",
)

OCR_PROMPT = """
You are reading pages from the same document. The document type is
unknown and could be a resume, invoice, contract, report, letter,
form, or any other type. Transcribe all visible text exactly as it
appears. Do not summarize, paraphrase, or invent text.

LAYOUT RULES (critical):
- If the page has multiple columns, transcribe the ENTIRE left
  column first, top to bottom, then the ENTIRE right column, top to
  bottom. Never interleave lines from different columns.
- If the page has a header/footer separate from the main body,
  transcribe the main body first, then header/footer content at the
  very end of that page's output, clearly marked.
- Preserve reading order exactly as a human would read it: do not
  reorder sentences or merge unrelated blocks.

STRUCTURE RULES:
- When you see a section heading or label (e.g. "Experience",
  "Projects", "Education", "Skills", "Invoice Number", "Total Due",
  "Parties", "Clause 1"), output it as a markdown heading on its own
  line, like "## Experience", before its content.
- Preserve tables using markdown table syntax (| col | col |), keeping
  every row and column exactly as shown. Do not flatten tables into
  a single line of text.
- Preserve bullet points and numbered lists using "-" or "1." markers.

DATE-PAIRING RULES (critical):
- Only attach a date or date range to a title/line if that exact date
  is positioned directly adjacent to it in the image (same line,
  directly below it, or directly to its right/left as a clear visual
  pair). Do not infer or guess which title a date belongs to.
- If a date appears in its own separate row, block, or sub-column
  with no title directly touching it, transcribe it on its own
  separate line rather than merging it into the nearest heading or
  the previous item. It is better to leave a date unattached than to
  attach it to the wrong line.
- Never carry a date forward from one entry to a different entry. If
  several entries are listed with only one date visible, transcribe
  only the entry that the date is visually attached to with that
  date; leave the others without a date.

ITEM-PAIRING RULES (critical):
- Some sections contain SHORT side-by-side micro-blocks: a brief title
  or label (e.g. a course name, a certification name) positioned next
  to a separate, unrelated detail (e.g. a technology list or
  description belonging to a DIFFERENT item entirely). This is
  different from a simple two-column page layout — it can occur
  within a single section, as small adjacent pairs rather than full
  columns.
- Before pairing a title with a description/tech-list/bullet block,
  check whether they are genuinely the same item, or whether the
  title is short (a course/certification name with no further detail)
  while the description visually belongs to a different, adjacent
  item. If a short label (e.g. "DataCamp — Course Name") has no
  bullets or description directly beneath/after it before the next
  short label appears, transcribe it alone as a short standalone
  entry. Do not borrow the next visible description line to fill it
  in if that description is more plausibly attached to a different,
  larger item nearby.
- When uncertain whether two adjacent lines belong together, prefer
  transcribing them as separate standalone lines over merging them
  into one item. A human reader can still tell they're related from
  proximity; an incorrect merge cannot be undone downstream.

DIAGRAM RULES (critical):
- If the page contains a diagram, chart, flowchart, UML diagram,
  architecture diagram, org chart, or any other visual structure
  (boxes, arrows, connecting lines, nodes) rather than plain text:
  do NOT just list the text labels found inside it as a flat,
  unstructured sequence of words. A flat label dump destroys the
  diagram's meaning (e.g. listing actor names and action names from a
  UML use-case diagram with no indication of which actor performs
  which action).
- Instead, describe the diagram's structure in plain sentences: name
  the diagram type if identifiable (e.g. "Use case diagram", "Flow
  chart", "Entity relationship diagram"), then describe each
  connection or relationship explicitly, e.g. "Actor 'User' connects
  to use cases: Register, Login, Edit Profile, Upload Document, View
  Docs, Chat" rather than just "Register Login Edit Profile Upload
  Document View Docs Chat".
- If the diagram's relationships are too complex or unclear to
  describe with full confidence, still separate distinct labeled
  elements onto their own lines rather than concatenating them, and
  note "[DIAGRAM: structure unclear, labels listed individually]"
  before the list.
- Wrap diagram descriptions in their own subsection, e.g.
  "### Diagram: <short description of what it depicts>", so
  downstream processing can distinguish diagram content from regular
  prose.

OTHER RULES:
- If a page is blank, return only [BLANK].
- For each page, start with a marker like [[PAGE 1]] on its own line.
""".strip()
