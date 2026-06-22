import os
from fastapi import HTTPException

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".docx",
    ".txt",
    ".pptx"
}


def validate_file_extension(filename: str):

    extension = os.path.splitext(filename)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {extension}"
        )
