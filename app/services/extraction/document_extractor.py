from __future__ import annotations

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from PIL.Image import Image as PILImage  

try:
    from PIL import Image  
except ModuleNotFoundError:
    Image = None 

from .base import batch_items
from .config import extraction_config
from .ollama_client import ollama_client
from .text_extractors import text_extractor


class DocumentExtractor:

    def __init__(self):
        self.ocr_dpi = extraction_config.ocr_dpi
        self.ocr_batch_size = extraction_config.ocr_batch_size

    def extract_text(self, file_path: str) -> str:
        ext = file_path.lower().split(".")[-1]

        if ext == "txt":
            return text_extractor.extract_txt(file_path)
        if ext == "docx":
            return text_extractor.extract_docx(file_path)
        if ext == "pptx":
            return text_extractor.extract_pptx(file_path)

        if ext == "pdf":
            images = self._extract_pdf_images(file_path)
        elif ext in ["png", "jpg", "jpeg"]:
            images = self._extract_image(file_path)
        else:
            raise ValueError(f"Unsupported format: {ext}")

        if not images:
            return ""

        return self._process_images_with_ocr(images)

    def _extract_pdf_images(self, file_path: str) -> List[PILImage]:
        try:
            from pdf2image import convert_from_path
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "PDF extraction requires the optional 'pdf2image' package."
            ) from exc

        return convert_from_path(
            file_path,
            dpi=self.ocr_dpi,
            fmt="jpeg",
            grayscale=True,
            jpegopt={
                "quality": 85,
                "optimize": False,
                "progressive": False,
            },
            thread_count=max(1, self.ocr_batch_size),
        )

    def _extract_image(self, file_path: str) -> List[PILImage]:
        if Image is None:
            raise RuntimeError(
                "Pillow is required for image extraction but is not installed."
            )

        with Image.open(file_path) as img:
            return [img.convert("RGB").copy()]

    def _process_images_with_ocr(self, images: List[PILImage]) -> str:
        extracted_pages = []

        for batch_start_index, batch in enumerate(
            batch_items(images, self.ocr_batch_size),
            start=1,
        ):
            page_start = ((batch_start_index - 1) * self.ocr_batch_size) + 1
            result = ollama_client.extract_batch(batch, page_start)
            extracted_pages.append(result)

        return "\n".join(extracted_pages)


document_extractor = DocumentExtractor()


def extract_text(file_path: str) -> str:
    return document_extractor.extract_text(file_path)


def extract_text_llm(file_path: str) -> str:
    return extract_text(file_path)
