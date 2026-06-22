from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_user
from app.core.file_validation import validate_file_extension

from app.models.document import Document
from app.schemas.document import DocumentOut
from app.schemas.document_upload import DocumentUploadOut

from app.services.document_service import (
    save_file,
    create_document_record,
    get_user_document,
    delete_document,
)
from app.services.chat_memory_service import create_chat_session

from app.tasks.document_tasks import process_document

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


@router.post("/", response_model=DocumentUploadOut)
@router.post("/upload", response_model=DocumentUploadOut, include_in_schema=False)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    # Validate file type
    validate_file_extension(file.filename)

    # Save file
    file_path = save_file(
        file=file,
        user_id=current_user.id
    )

    # Create DB record
    document = create_document_record(
        db=db,
        user_id=current_user.id,
        filename=file.filename,
        file_path=file_path
    )

    chat_session = create_chat_session(
        db=db,
        user_id=current_user.id,
        document_id=document.id,
    )

    # Send background task
    process_document.delay(
        document.id
    )

    # Return immediately
    return {
        "document": document,
        "session_id": chat_session.id,
    }


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

@router.get("/{doc_id}/status")
def get_document_status(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    document = get_user_document(
        db=db,
        document_id=doc_id,
        user_id=current_user.id
    )

    return {
        "id": document.id,
        "status": document.status,
        "processing_step": document.processing_step,
        "progress": document.progress,
        "error_message": document.error_message
    }
