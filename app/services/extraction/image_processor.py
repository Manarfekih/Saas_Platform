from __future__ import annotations

import base64
import io
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from PIL.Image import Image as PILImage  

try:
    from PIL import Image  
except ModuleNotFoundError:
    Image = None  
from .config import extraction_config


class ImageProcessor:

    @staticmethod
    def image_to_base64(img: PILImage) -> str:
        if Image is None:
            raise RuntimeError(
                "Pillow is required for image processing but is not installed."
            )

        if img.mode != "RGB":
            img = img.convert("RGB")

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85, optimize=True)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    @staticmethod
    def prepare_for_ocr(img: PILImage) -> PILImage:
        if Image is None:
            raise RuntimeError(
                "Pillow is required for image processing but is not installed."
            )

        prepared = img.copy()
        max_side = extraction_config.ocr_max_side
        prepared.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)

        if prepared.mode != "RGB":
            prepared = prepared.convert("RGB")

        return prepared

    @staticmethod
    def images_to_base64(images: List[PILImage]) -> List[str]:
        if Image is None:
            raise RuntimeError(
                "Pillow is required for image processing but is not installed."
            )

        return [ImageProcessor.image_to_base64(img) for img in images]

    @staticmethod
    def prepare_images(images: List[PILImage]) -> List[PILImage]:
        if Image is None:
            raise RuntimeError(
                "Pillow is required for image processing but is not installed."
            )

        return [ImageProcessor.prepare_for_ocr(img) for img in images]
