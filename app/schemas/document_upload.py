from pydantic import BaseModel

from app.schemas.document import DocumentOut


class DocumentUploadOut(BaseModel):
    document: DocumentOut
    session_id: int
