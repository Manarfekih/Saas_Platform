from typing import Any, Dict


def export_summary_to_markdown(summary: Dict[str, Any]) -> str:
    title = summary.get("title") or "Document Summary"
    doc_type = summary.get("document_type") or "Document"
    overview = summary.get("overview") or "No overview available"

    lines = [
        f"# {title}",
        "",
        f"Document type: {doc_type}",
        "",
        "## What this document is about",
        overview,
        "",
    ]

    key_info = summary.get("key_information") or {}
    key_order = ["people", "organizations", "dates", "amounts"]
    key_labels = {
        "people": "People",
        "organizations": "Organizations",
        "dates": "Dates",
        "amounts": "Amounts",
    }

    rendered_key_info = []
    for key in key_order:
        values = key_info.get(key) or []
        if values:
            rendered_key_info.append((key_labels[key], values))

    if rendered_key_info:
        lines.append("## Key Information")
        for label, values in rendered_key_info:
            lines.append(f"- {label}: {', '.join(str(value) for value in values)}")
        lines.append("")

    sections = summary.get("sections") or []
    if sections:
        lines.append("## Structured Overview")
        lines.append("")
        for section in sections:
            if not isinstance(section, dict):
                continue
            section_title = section.get("title") or "Section"
            lines.append(f"### {section_title}")

            items = section.get("items") or []
            for item in items:
                if not isinstance(item, dict):
                    item_name = str(item).strip()
                    if item_name:
                        lines.append(f"- {item_name}")
                    continue

                name = (item.get("name") or "").strip()
                description = (item.get("description") or "").strip()
                if not name:
                    continue
                if description:
                    lines.append(f"- {name}: {description}")
                else:
                    lines.append(f"- {name}")
            lines.append("")

    statistics = summary.get("statistics") or {}
    if statistics:
        lines.append("## Metadata")
        if statistics.get("total_pages"):
            lines.append(f"- Total pages: {statistics['total_pages']}")
        if statistics.get("generated_at"):
            lines.append(f"- Generated at: {statistics['generated_at']}")
        lines.append("")

    return "\n".join(line.rstrip() for line in lines).strip() + "\n"
