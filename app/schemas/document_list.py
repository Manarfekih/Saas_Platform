from datetime import datetime

from pydantic import BaseModel


class DocumentListOut(BaseModel):
    id: int
    filename: str
    status: str
    doc_type: str | None = None
    created_at: datetime
    error_message: str | None = None

    class Config:
        from_attributes = True