import os
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.chat_session import ChatSession
from app.models.message import Message
from app.models.document_chunk import DocumentChunk

UPLOAD_DIR = "/app/uploads"


def save_file(file, user_id: int):

    user_folder = os.path.join(UPLOAD_DIR, f"user_{user_id}")

    os.makedirs(user_folder, exist_ok=True)

    # Keep only the base filename to avoid path traversal or nested paths.
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

    # Remove dependent chat data first to satisfy FK constraints.
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
