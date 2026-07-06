from datetime import datetime

from pydantic import BaseModel


class DocumentOut(BaseModel):

    id: int
    filename: str
    file_path: str
    status: str
    doc_type: str | None = None
    created_at: datetime
    extracted_text: str | None = None
    error_message: str | None = None


    class Config:
        from_attributes = True
