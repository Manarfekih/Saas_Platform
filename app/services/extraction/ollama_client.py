import json
from urllib import error, request

from .config import extraction_config
from .image_processor import ImageProcessor


class OllamaClient:

    def __init__(self):
        self.base_url = extraction_config.ollama_url.rstrip("/")
        self.timeout = extraction_config.ocr_request_timeout

    def extract_text_from_images(
        self,
        images: list,
        page_start: int,
    ) -> str:
        image_b64s = ImageProcessor.images_to_base64(images)

        page_end = page_start + len(images) - 1
        payload = extraction_config.get_ollama_payload(
            page_start, page_end, image_b64s
        )

        req = request.Request(
            url=f"{self.base_url}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            text = data.get("response", "")
            done_reason = data.get("done_reason")

            if done_reason == "length":
                raise RuntimeError(
                    f"OCR output truncated by length limit for pages "
                    f"{page_start}-{page_end} (done_reason=length, "
                    f"{len(text)} chars generated). Increase num_predict "
                    f"or reduce OCR_BATCH_SIZE further."
                )

            return text.strip()

        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(
                f"Ollama OCR request failed with HTTP {exc.code}: {detail}"
            ) from exc
        except error.URLError as exc:
            raise RuntimeError(
                f"Ollama OCR request failed: {exc.reason}"
            ) from exc

    def extract_batch(
        self,
        images: list,
        page_start: int,
    ) -> str:
        try:
            prepared_batch = ImageProcessor.prepare_images(images)
            cleaned = self.extract_text_from_images(
                prepared_batch,
                page_start=page_start,
            ).strip()

            if not cleaned:
                raise ValueError("Empty OCR output")

            page_end = page_start + len(images) - 1
            return f"\n--- PAGES {page_start}-{page_end} ---\n{cleaned}"

        except Exception as e:
            page_end = page_start + len(images) - 1
            return f"\n--- PAGES {page_start}-{page_end} FAILED ---\n{str(e)}"


ollama_client = OllamaClient()
