import importlib
import os
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.chat_session import ChatSession
from app.models.message import Message
from app.models.document_chunk import DocumentChunk
from app.services.summary import delete_summary_file
UPLOAD_DIR = "/app/uploads"

_PAGE_MARKER_PATTERN = __import__("re").compile(r"\[\[PAGE\s+(\d+)\]\]")


def _count_pages_from_text(extracted_text: str | None):
    if not extracted_text:
        return None

    matches = _PAGE_MARKER_PATTERN.findall(extracted_text)
    if matches:
        try:
            return max(int(match) for match in matches)
        except ValueError:
            return None

    return None


def get_page_count(file_path: str, extracted_text: str | None = None):
    text_count = _count_pages_from_text(extracted_text)
    if text_count:
        return text_count

    ext = os.path.splitext(file_path.lower())[1].lstrip(".")

    if ext == "pdf":
        try:
            pdf2image = importlib.import_module("pdf2image")
            pdfinfo_from_path = getattr(pdf2image, "pdfinfo_from_path")

            info = pdfinfo_from_path(file_path)
            pages = info.get("Pages")
            return int(pages) if pages is not None else None
        except Exception:
            return None

    if ext == "pptx":
        try:
            pptx = importlib.import_module("pptx")
            Presentation = getattr(pptx, "Presentation")

            return len(Presentation(file_path).slides)
        except Exception:
            return None

    if ext in {"txt", "docx"}:
        return 1

    return None


def sync_document_page_count(db: Session, document: Document):
    
    derived_count = get_page_count(document.file_path, getattr(document, "extracted_text", None))
    if derived_count:
        setattr(document, "page_count", derived_count)
        return derived_count

    page_count = (
        db.query(DocumentChunk.page_number)
        .filter(DocumentChunk.document_id == document.id)
        .filter(DocumentChunk.page_number.isnot(None))
        .order_by(DocumentChunk.page_number.desc())
        .limit(1)
        .scalar()
    )

    if page_count:
        setattr(document, "page_count", int(page_count))
        return int(page_count)

    setattr(document, "page_count", None)
    return None


def save_file(file, user_id: int):

    user_folder = os.path.join(UPLOAD_DIR, f"user_{user_id}")

    os.makedirs(user_folder, exist_ok=True)

    safe_filename = os.path.basename(file.filename).replace(" ", "_")

    file_path = os.path.join(user_folder, safe_filename)

    try:
        with open(file_path, "wb") as f:
            f.write(file.file.read())
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"File save failed: {str(e)}"
        )

    return file_path


def create_document_record(db: Session, user_id: int, filename: str, file_path: str):

    document = Document(
        user_id=user_id,
        filename=filename,
        file_path=file_path,
        status="pending",
        error_message=None
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def get_user_document(db: Session, document_id: int, user_id: int):

    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.user_id == user_id
        )
        .first()
    )

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return document


def delete_document(db: Session, document: Document):

    session_ids = [
        row[0]
        for row in (
            db.query(ChatSession.id)
            .filter(ChatSession.document_id == document.id)
            .all()
        )
    ]

    if session_ids:
        db.query(Message).filter(Message.session_id.in_(session_ids)).delete(
            synchronize_session=False
        )
        db.query(ChatSession).filter(ChatSession.id.in_(session_ids)).delete(
            synchronize_session=False
        )

    db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document.id
    ).delete(synchronize_session=False)

    delete_summary_file(document)

    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    db.delete(document)
    db.commit()


def mark_processing(db: Session, document: Document):

    document.status = "processing"
    db.commit()
    db.refresh(document)
    return document


def update_document_success(db: Session, document_id: int, text: str):

    db.query(Document).filter(Document.id == document_id).update({
        "extracted_text": text,
        "status": "processed"
    })

    db.commit()


def mark_failed(db: Session, document_id: int):

    db.query(Document).filter(Document.id == document_id).update({
        "status": "failed"
    })

    db.commit()

















