from fastapi import APIRouter
from pydantic import BaseModel

from app.db.database import SessionLocal
from app.services.rag_service import answer_question


router = APIRouter()



class ChatRequest(BaseModel):

    session_id: int

    question: str




@router.post("/documents/{document_id}/chat")
def chat(
    document_id: int,
    request: ChatRequest
):

    db = SessionLocal()


    try:

        result = answer_question(

            db=db,

            document_id=document_id,

            session_id=request.session_id,

            question=request.question

        )


        return result


    finally:

        db.close()