from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.chat_session import ChatSession
from app.models.message import Message
from app.models.chat_type import ChatType



def save_message(
    db: Session,
    session_id: int,
    role: str,
    content: str,
):
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Chat session not found",
        )

    message = Message(
        session_id=session_id,
        role=role,
        content=content,
    )

    db.add(message)
    db.commit()
    db.refresh(message)
    return message




def create_chat_session(
    db: Session,
    user_id: int,
    chat_type: ChatType,
    document_id: int | None = None,
):
    
    query = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id)
        .filter(ChatSession.chat_type == chat_type)
    )

    if chat_type == ChatType.DOCUMENT:
        query = query.filter(ChatSession.document_id == document_id)
    else:
        query = query.filter(ChatSession.document_id.is_(None))

    existing = query.first()

    if existing:
        return existing

    session = ChatSession(
        user_id=user_id,
        document_id=document_id,
        chat_type=chat_type,
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


def create_global_chat_session(db: Session, user_id: int):
    existing = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id)
        .filter(ChatSession.chat_type == ChatType.GLOBAL)
        .first()
    )

    if existing:
        return existing

    session = ChatSession(
        user_id=user_id,
        document_id=None,
        chat_type=ChatType.GLOBAL,
    )

    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def get_history(
    db: Session,
    session_id: int,
    limit: int = 4,
):
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Chat session not found",
        )

    messages = (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.id.desc())
        .limit(limit)
        .all()
    )

    return list(reversed(messages))
