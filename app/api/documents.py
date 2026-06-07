from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_user
from app.core.file_validation import validate_file_extension

from app.models.document import Document
from app.schemas.document import DocumentOut

from app.services.document_service import (
    save_file,
    create_document_record,
    get_user_document,
    delete_document,
    update_document_text,
    mark_document_failed
)

from app.services.ocr_service import extract_text

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


@router.post("/upload", response_model=DocumentOut)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    # 1. Validate file type
    validate_file_extension(file.filename)

    # 2. Save file to disk
    file_path = save_file(
        file=file,
        user_id=current_user.id
    )

    # 3. Create DB record
    document = create_document_record(
        db=db,
        user_id=current_user.id,
        filename=file.filename,
        file_path=file_path
    )

    # 4. OCR processing
    try:
        extracted_text = extract_text(document.file_path)

        document = update_document_text(
            db=db,
            document=document,
            extracted_text=extracted_text
        )

    except Exception as e:

        print(f"OCR Error: {e}")

        mark_document_failed(
            db=db,
            document=document
        )

    return document


@router.get("/", response_model=list[DocumentOut])
def get_documents(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    documents = (
        db.query(Document)
        .filter(Document.user_id == current_user.id)
        .all()
    )

    return documents


@router.get("/{doc_id}", response_model=DocumentOut)
def get_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    document = get_user_document(
        db=db,
        document_id=doc_id,
        user_id=current_user.id
    )

    return document


@router.delete("/{doc_id}")
def remove_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    document = get_user_document(
        db=db,
        document_id=doc_id,
        user_id=current_user.id
    )

    delete_document(
        db=db,
        document=document
    )

    return {
        "message": "Document deleted successfully"
    }