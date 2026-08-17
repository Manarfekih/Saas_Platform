from typing import Any, Dict

from .constants import (
    VISION_MODEL,
    OCR_DPI,
    OCR_BATCH_SIZE,
    OCR_MAX_SIDE,
    OCR_REQUEST_TIMEOUT,
    OLLAMA_URL,
    OCR_PROMPT,
)


class ExtractionConfig:

    def __init__(self):
        self.vision_model = VISION_MODEL
        self.ocr_dpi = OCR_DPI
        self.ocr_batch_size = OCR_BATCH_SIZE
        self.ocr_max_side = OCR_MAX_SIDE
        self.ocr_request_timeout = OCR_REQUEST_TIMEOUT
        self.ollama_url = OLLAMA_URL
        self.ocr_prompt = OCR_PROMPT

    def get_ollama_payload(
        self,
        page_start: int,
        page_end: int,
        image_b64s: list,
    ) -> Dict[str, Any]:
        page_markers = ", ".join(
            f"[[PAGE {page_num}]]"
            for page_num in range(page_start, page_end + 1)
        )

        return {
            "model": self.vision_model,
            "prompt": (
                f"{self.ocr_prompt}\n"
                f"The current images are pages {page_start} to {page_end}.\n"
                f"Use these markers in order: {page_markers}."
            ),
            "images": image_b64s,
            "stream": False,
            "options": {
                "temperature": 0,
                "num_ctx": 12288,
                "num_predict": 4096,
            },
        }

    @classmethod
    def get_instance(cls) -> "ExtractionConfig":
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance


extraction_config = ExtractionConfig.get_instance()
