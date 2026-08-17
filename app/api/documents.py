import os
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile
from fastapi.responses import FileResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import ALGORITHM, SECRET_KEY
from app.core.deps import get_current_user
from app.core.file_validation import validate_file_extension
from app.db.session import get_db
from app.models.chat_session import ChatSession
from app.models.chat_type import ChatType
from app.models.document import Document
from app.models.message import Message
from app.models.user import User
from app.schemas.document import DocumentOut
from app.schemas.document_list import DocumentListOut
from app.schemas.document_upload import DocumentUploadOut
from app.services.chat_memory_service import create_chat_session
from app.services.classification import classify_sections, infer_document_type
from app.services.document_service import (
    create_document_record,
    delete_document,
    get_user_document,
    save_file,
    sync_document_page_count,
)
from app.services.summary import export_summary_to_markdown, generate_and_store_summary
from app.tasks.document_tasks import process_document

router = APIRouter(prefix="/documents", tags=["Documents"])

bearer_scheme = HTTPBearer(auto_error=False)


def _get_current_user_from_token(
    db: Session,
    bearer: HTTPAuthorizationCredentials | None = None,
    token: str | None = None,
):
    raw_token = token or (bearer.credentials if bearer else None)
    if not raw_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(raw_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def _ensure_document_summary(
    db: Session,
    document: Document,
):
    if document.summary:
        return

    if not document.extracted_text:
        raise HTTPException(status_code=404, detail="Summary not available")

    resolved_doc_type = infer_document_type(document.extracted_text, document.filename) or document.doc_type
    if resolved_doc_type != document.doc_type:
        document.doc_type = resolved_doc_type
        db.commit()

    classified_items = classify_sections(document.extracted_text, resolved_doc_type)
    result = generate_and_store_summary(
        db=db,
        document=document,
        classified_items=classified_items,
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate summary: {result.get('error')}",
        )


@router.post("/", response_model=DocumentUploadOut)
@router.post("/upload", response_model=DocumentUploadOut, include_in_schema=False)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    validate_file_extension(file.filename)

    file_path = save_file(file=file, user_id=current_user.id)

    document = create_document_record(
        db=db,
        user_id=current_user.id,
        filename=file.filename,
        file_path=file_path,
    )

    chat_session = create_chat_session(
        db=db,
        user_id=current_user.id,
        chat_type=ChatType.DOCUMENT,
        document_id=document.id,
    )

    process_document.delay(document.id)

    return {
        "document": document,
        "session_id": chat_session.id,
    }


@router.get("/", response_model=list[DocumentListOut])
def get_documents(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    documents = (
        db.query(Document)
        .filter(Document.user_id == current_user.id)
        .order_by(Document.id.desc())
        .all()
    )

    for document in documents:
        sync_document_page_count(db, document)

    return documents


@router.get("/{doc_id}", response_model=DocumentOut)
def get_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    document = get_user_document(db=db, document_id=doc_id, user_id=current_user.id)
    sync_document_page_count(db, document)
    return document


@router.delete("/{doc_id}")
def remove_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    document = get_user_document(db=db, document_id=doc_id, user_id=current_user.id)
    delete_document(db=db, document=document)
    return {"message": "Document deleted successfully"}


@router.get("/{doc_id}/status")
def get_document_status(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    document = get_user_document(db=db, document_id=doc_id, user_id=current_user.id)
    return {
        "id": document.id,
        "status": document.status,
        "processing_step": document.processing_step,
        "progress": document.progress,
        "error_message": document.error_message,
    }


@router.get("/{document_id}/summary")
def get_document_summary(
    document_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    document = get_user_document(db, document_id, current_user.id)

    if document.status != "processed":
        raise HTTPException(status_code=400, detail="Document is not processed yet")

    _ensure_document_summary(db, document)

    return {
        "document_id": document.id,
        "document_type": document.doc_type,
        "summary": document.summary,
        "summary_file_name": document.summary_file_name,
        "summary_generated_at": document.summary.get("statistics", {}).get("generated_at") if document.summary else None,
        "total_chunks": document.total_chunks,
        "page_count": document.page_count,
    }


@router.get("/{document_id}/summary/download")
def download_summary(
    document_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    document = get_user_document(db, document_id, current_user.id)

    if document.status != "processed":
        raise HTTPException(status_code=400, detail="Document is not processed yet")

    _ensure_document_summary(db, document)

    content = export_summary_to_markdown(document.summary)
    base_name = os.path.splitext(document.filename)[0]
    return Response(
        content=content,
        media_type="text/markdown",
        headers={
            "Content-Disposition": f"attachment; filename={base_name}_summary.md",
        },
    )


@router.post("/{document_id}/regenerate-summary")
def regenerate_summary(
    document_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    document = get_user_document(db, document_id, current_user.id)

    if document.status != "processed":
        raise HTTPException(status_code=400, detail="Document is not processed yet")

    if not document.extracted_text:
        raise HTTPException(status_code=400, detail="No extracted text available")

    resolved_doc_type = infer_document_type(document.extracted_text, document.filename) or document.doc_type
    if resolved_doc_type != document.doc_type:
        document.doc_type = resolved_doc_type
        db.commit()

    classified_items = classify_sections(document.extracted_text, resolved_doc_type)
    result = generate_and_store_summary(
        db=db,
        document=document,
        classified_items=classified_items,
    )

    if not result["success"]:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to regenerate summary: {result.get('error')}",
        )

    return {
        "message": "Summary regenerated successfully",
        "document_id": document.id,
        "document_type": document.doc_type,
        "summary_file_name": document.summary_file_name,
        "summary": document.summary,
    }


@router.get("/{doc_id}/chat-session")
def get_document_chat_session(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    document = get_user_document(db=db, document_id=doc_id, user_id=current_user.id)

    session = (
        db.query(ChatSession)
        .filter(ChatSession.document_id == document.id)
        .filter(ChatSession.user_id == current_user.id)
        .first()
    )

    if not session:
        session = create_chat_session(
            db=db,
            user_id=current_user.id,
            chat_type=ChatType.DOCUMENT,
            document_id=document.id,
        )

    return {"session_id": session.id}


@router.get("/{doc_id}/chat-history")
def get_document_chat_history(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    document = get_user_document(db=db, document_id=doc_id, user_id=current_user.id)

    session = (
        db.query(ChatSession)
        .filter(ChatSession.document_id == document.id)
        .filter(ChatSession.user_id == current_user.id)
        .first()
    )

    if not session:
        session = create_chat_session(
            db=db,
            user_id=current_user.id,
            chat_type=ChatType.DOCUMENT,
            document_id=document.id,
        )

    messages = (
        db.query(Message)
        .filter(Message.session_id == session.id)
        .order_by(Message.id.asc())
        .all()
    )

    return {
        "session_id": session.id,
        "messages": [
            {"role": m.role, "content": m.content}
            for m in messages
        ],
    }


@router.get("/{doc_id}/file")
def serve_document_file(
    doc_id: int,
    token: str | None = Query(default=None),
    bearer: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    current_user = _get_current_user_from_token(db=db, bearer=bearer, token=token)

    document = get_user_document(
        db=db,
        document_id=doc_id,
        user_id=current_user.id,
    )

    file_path = document.file_path

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    ext = file_path.rsplit(".", 1)[-1].lower()
    media_types = {
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
    }
    media_type = media_types.get(ext, "application/octet-stream")

    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=document.filename,
        headers={
            "Content-Disposition": f'inline; filename="{document.filename}"',
            "Cache-Control": "private, max-age=300",
        },
    )
