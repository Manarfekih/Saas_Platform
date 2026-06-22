import os
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.document import Document

UPLOAD_DIR = "/app/uploads" 

def save_file(file, user_id: int):

    user_folder = os.path.join(UPLOAD_DIR, f"user_{user_id}")

    os.makedirs(user_folder, exist_ok=True)

    # safer filename (avoid spaces/issues in Docker/Linux)
    safe_filename = file.filename.replace(" ", "_")

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
