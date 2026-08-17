from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.chat_session import ChatSession
from app.models.chat_type import ChatType
from app.services.agent.agent_service import agent_answer_global
from app.services.chat_memory_service import create_global_chat_session, get_history

router = APIRouter()


class GlobalChatRequest(BaseModel):
    session_id: int
    question: str


@router.post("/chat/global")
def chat_global(
    request: GlobalChatRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    session = create_global_chat_session(db, current_user.id)

    if request.session_id != session.id:
        raise HTTPException(status_code=400, detail="Invalid global chat session")

    return agent_answer_global(
        db=db,
        session_id=session.id,
        user_id=current_user.id,
        question=request.question,
    )


@router.get("/chat/all/session")
def get_global_chat_session(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    session = create_global_chat_session(db, current_user.id)
    return {"session_id": session.id}


@router.get("/chat/all/history")
def get_global_chat_history(
    session_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id)
        .filter(ChatSession.user_id == current_user.id)
        .filter(ChatSession.chat_type == ChatType.GLOBAL)
        .first()
    )

    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    messages = get_history(db=db, session_id=session.id, limit=200)

    return {
        "session_id": session.id,
        "messages": [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in messages
        ],
    }
