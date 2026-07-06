from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_user
from app.services.agent_service import agent_answer, agent_answer_global
from app.services.chat_memory_service import create_chat_session
from app.models.chat_type import ChatType
from app.services.document_service import get_user_document

router = APIRouter()


class ChatRequest(BaseModel):
    session_id: int
    question: str


@router.post("/documents/{document_id}/chat")
def chat(
    document_id: int,
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    document = get_user_document(
        db=db,
        document_id=document_id,
        user_id=current_user.id,
    )

    if not document:
        raise HTTPException(404, "Document not found")

    return agent_answer(
        db=db,
        document_id=document_id,
        session_id=request.session_id,
        question=request.question,
    )


@router.get("/chat/all/session")
def get_global_chat_session(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    session = create_chat_session(
        db=db,
        user_id=current_user.id,
        chat_type=ChatType.GLOBAL,
        document_id=None,
    )
    return {"session_id": session.id}


class GlobalChatRequest(BaseModel):
    session_id: int
    question: str


@router.post("/chat/all")
def global_chat(
    request: GlobalChatRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return agent_answer_global(
        db=db,
        session_id=request.session_id,
        user_id=current_user.id,
        question=request.question,
    )