from pydantic import BaseModel


class DocumentOut(BaseModel):

    id: int
    filename: str
    file_path: str
    status: str
    doc_type: str | None = None

    class Config:
        from_attributes = True