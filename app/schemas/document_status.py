from pydantic import BaseModel


class DocumentStatusOut(BaseModel):

    id: int

    status: str

    processing_step: str | None

    progress: int
    error_message: str | None = None

    class Config:
        from_attributes = True
