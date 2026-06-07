import os

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.document import Document


def save_file(file, user_id: int):

    user_folder = f"uploads/user_{user_id}"

    os.makedirs(user_folder, exist_ok=True)

    file_path = f"{user_folder}/{file.filename}"

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    return file_path


def create_document_record(
    db: Session,
    user_id: int,
    filename: str,
    file_path: str
):

    doc = Document(
        user_id=user_id,
        filename=filename,
        file_path=file_path,
        status="pending"
    )

    db.add(doc)
    db.commit()
    db.refresh(doc)

    return doc


def get_user_document(
    db: Session,
    document_id: int,
    user_id: int
):

    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.user_id == user_id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return document


def delete_document(
    db: Session,
    document: Document
):

    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    db.delete(document)
    db.commit()


def update_document_text(
    db: Session,
    document: Document,
    extracted_text: str
):

    document.extracted_text = extracted_text

    document.status = "processed"

    db.commit()

    db.refresh(document)

    return document



def mark_document_failed(
    db: Session,
    document: Document
):

    document.status = "failed"

    db.commit()