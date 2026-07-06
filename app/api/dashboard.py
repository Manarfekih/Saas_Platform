from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_user

from app.models.document import Document
from app.models.chat_session import ChatSession
from app.models.message import Message

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/stats")
def dashboard_stats(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    # Documents
    total_documents = (
        db.query(Document)
        .filter(Document.user_id == current_user.id)
        .count()
    )

    # Processed
    processed_documents = (
        db.query(Document)
        .filter(
            Document.user_id == current_user.id,
            Document.status.in_(["completed", "processed"])
        )
        .count()
    )

    # In Queue
    queued_documents = (
        db.query(Document)
        .filter(
            Document.user_id == current_user.id,
            Document.status.in_(["pending", "processing"])
        )
        .count()
    )

    # Failed
    failed_documents = (
        db.query(Document)
        .filter(
            Document.user_id == current_user.id,
            Document.status == "failed"
        )
        .count()
    )

    # Chats (count user messages only, not assistant replies or sessions)
    total_chats = (
        db.query(Message)
        .join(ChatSession)
        .filter(
            ChatSession.user_id == current_user.id,
            Message.role == "user"
        )
        .count()
    )

    return {
        "documents": total_documents,
        "processed": processed_documents,
        "in_queue": queued_documents,
        "failed": failed_documents,
        "chats": total_chats
    }
