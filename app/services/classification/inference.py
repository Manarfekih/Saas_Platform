from __future__ import annotations

import logging

from app.services.classification.constants import DOCUMENT_TYPE_KEYWORDS

logger = logging.getLogger("saas-ia-platform")


def _count_keyword_hits(sample_text: str, keywords: list[str]) -> int:
    return sum(1 for keyword in keywords if keyword in sample_text)


def infer_document_type(raw_text: str, filename: str | None = None):
    sample_text = f"{filename or ''}\n{raw_text[:6000]}".lower()
    filename_text = (filename or "").lower()

    scores = {
        doc_type: _count_keyword_hits(sample_text, keywords)
        for doc_type, keywords in DOCUMENT_TYPE_KEYWORDS.items()
    }

    cv_filename_hint = any(token in filename_text for token in ("cv", "resume", "curriculum vitae"))
    invoice_filename_hint = any(token in filename_text for token in ("invoice", "bill"))
    contract_filename_hint = "contract" in filename_text or "agreement" in filename_text
    report_filename_hint = "report" in filename_text or "summary" in filename_text

    resume_markers = [
        "work experience",
        "professional experience",
        "education",
        "skills",
        "summary",
        "certification",
        "projects",
        "linkedin",
    ]
    invoice_markers = [
        "invoice number",
        "bill to",
        "amount due",
        "subtotal",
        "total due",
        "payment terms",
    ]
    contract_markers = [
        "agreement",
        "clause",
        "signature",
        "party",
        "terms and conditions",
    ]
    report_markers = [
        "executive summary",
        "findings",
        "recommendations",
        "methodology",
        "conclusion",
    ]

    cv_score = scores.get("cv", 0)
    invoice_score = scores.get("invoice", 0)
    contract_score = scores.get("contract", 0)
    report_score = scores.get("report", 0)

    if cv_filename_hint:
        cv_score += 2
    if sum(1 for marker in resume_markers if marker in sample_text) >= 2:
        cv_score += 2
    if any(marker in sample_text for marker in ("curriculum vitae", "resume")):
        cv_score += 2

    if invoice_filename_hint:
        invoice_score += 1
    if sum(1 for marker in invoice_markers if marker in sample_text) >= 2:
        invoice_score += 2
    if any(marker in sample_text for marker in ("invoice number", "amount due", "bill to")):
        invoice_score += 2

    if contract_filename_hint:
        contract_score += 1
    if sum(1 for marker in contract_markers if marker in sample_text) >= 2:
        contract_score += 2

    if report_filename_hint:
        report_score += 1
    if sum(1 for marker in report_markers if marker in sample_text) >= 2:
        report_score += 2

    ranked = [
        ("cv", cv_score),
        ("invoice", invoice_score),
        ("contract", contract_score),
        ("report", report_score),
    ]
    ranked.sort(key=lambda item: item[1], reverse=True)

    best_type, best_score = ranked[0]
    second_score = ranked[1][1]

    if best_type == "cv" and best_score >= 4 and best_score >= second_score:
        logger.info("Inferred document type: cv")
        return "cv"

    if best_type == "invoice" and best_score >= 4 and invoice_score >= cv_score + 1:
        logger.info("Inferred document type: invoice")
        return "invoice"

    if best_type == "contract" and best_score >= 3 and contract_score >= max(cv_score, invoice_score, report_score):
        logger.info("Inferred document type: contract")
        return "contract"

    if best_type == "report" and best_score >= 3 and report_score >= max(cv_score, invoice_score, contract_score):
        logger.info("Inferred document type: report")
        return "report"

    logger.info("Document type inference returned unknown")
    return None
