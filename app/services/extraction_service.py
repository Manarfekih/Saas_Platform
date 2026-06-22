import os
import io
import json
import base64
from urllib import error, request

from PIL import Image
from pdf2image import convert_from_path

from docx import Document as DocxDocument
from pptx import Presentation


VISION_MODEL = os.getenv(
    "VISION_MODEL",
    "qwen2.5vl:7b"
)

OCR_DPI = int(os.getenv("OCR_DPI", "120"))
OCR_BATCH_SIZE = max(1, int(os.getenv("OCR_BATCH_SIZE", "4")))
OCR_MAX_SIDE = int(os.getenv("OCR_MAX_SIDE", "1000"))
OCR_REQUEST_TIMEOUT = int(os.getenv("OCR_REQUEST_TIMEOUT", "240"))

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://ollama:11434"
)


OCR_PROMPT = """
You are reading pages from the same document.
Transcribe all visible text exactly as it appears.
Keep tables, labels, and bullet points as plain text.
Do not summarize and do not invent text.
If a page is blank, return only [BLANK].
For each page, start with a marker like [[PAGE 1]] on its own line.
""".strip()


# =========================
# Vision helpers
# =========================

def _image_to_base64(img: Image.Image) -> str:

    if img.mode != "RGB":
        img = img.convert("RGB")

    buffer = io.BytesIO()
    img.save(
        buffer,
        format="JPEG",
        quality=85,
        optimize=True,
    )

    return base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")


def _prepare_image_for_ocr(img: Image.Image) -> Image.Image:

    prepared = img.copy()

    max_side = OCR_MAX_SIDE
    prepared.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)

    if prepared.mode != "RGB":
        prepared = prepared.convert("RGB")

    return prepared


def _batch_items(items: list, batch_size: int):
    for index in range(0, len(items), batch_size):
        yield items[index:index + batch_size]


def _extract_from_images(
    images: list[Image.Image],
    page_start: int,
) -> str:

    image_b64s = [
        _image_to_base64(image)
        for image in images
    ]

    page_end = page_start + len(images) - 1
    page_markers = ", ".join(
        f"[[PAGE {page_num}]]"
        for page_num in range(page_start, page_end + 1)
    )

    payload = {
        "model": VISION_MODEL,
        "prompt": (
            f"{OCR_PROMPT}\n"
            f"The current images are pages {page_start} to {page_end}.\n"
            f"Use these markers in order: {page_markers}."
        ),
        "images": image_b64s,
        "stream": False,
        "options": {
            "temperature": 0,
            "num_ctx": 4096,
        },
    }

    req = request.Request(
        url=f"{OLLAMA_URL.rstrip('/')}/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=OCR_REQUEST_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        text = data.get("response", "")
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


# =========================
# Native text extractors
# =========================

def _extract_txt(file_path: str) -> str:

    with open(
        file_path,
        "r",
        encoding="utf-8",
        errors="ignore",
    ) as f:
        return f.read()


def _extract_docx(file_path: str) -> str:

    doc = DocxDocument(file_path)

    text = []

    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            text.append(paragraph.text.strip())

    for table in doc.tables:
        for row in table.rows:

            row_text = " | ".join(
                cell.text.strip()
                for cell in row.cells
            )

            if row_text.strip():
                text.append(row_text)

    return "\n".join(text)


def _extract_pptx(file_path: str) -> str:

    prs = Presentation(file_path)

    text_runs = []

    for slide in prs.slides:
        for shape in slide.shapes:

            if hasattr(shape, "text"):
                text = shape.text.strip()

                if text:
                    text_runs.append(text)

    return "\n".join(text_runs)


# =========================
# Main extraction entry
# =========================

def extract_text_llm(file_path: str) -> str:

    ext = file_path.lower().split(".")[-1]

    # Native extraction

    if ext == "txt":
        return _extract_txt(file_path)

    if ext == "docx":
        return _extract_docx(file_path)

    if ext == "pptx":
        return _extract_pptx(file_path)

    # Vision extraction only

    if ext == "pdf":

        images = convert_from_path(
            file_path,
            dpi=OCR_DPI,
            fmt="jpeg",
            grayscale=True,
            jpegopt={
                "quality": 85,
                "optimize": False,
                "progressive": False,
            },
            thread_count=max(1, OCR_BATCH_SIZE),
        )

    elif ext in ["png", "jpg", "jpeg"]:

        with Image.open(file_path) as img:
            images = [img.convert("RGB").copy()]

    else:
        raise ValueError(
            f"Unsupported format: {ext}"
        )

    if not images:
        return ""

    extracted_pages = []

    for batch_start_index, batch in enumerate(
        _batch_items(images, OCR_BATCH_SIZE),
        start=1,
    ):
        page_start = ((batch_start_index - 1) * OCR_BATCH_SIZE) + 1
        page_end = page_start + len(batch) - 1

        try:
            prepared_batch = [
                _prepare_image_for_ocr(image)
                for image in batch
            ]

            cleaned = _extract_from_images(
                prepared_batch,
                page_start=page_start,
            ).strip()

            if not cleaned:
                raise ValueError("Empty OCR output")

            extracted_pages.append(
                f"\n--- PAGES {page_start}-{page_end} ---\n{cleaned}"
            )

        except Exception as e:
            extracted_pages.append(
                f"\n--- PAGES {page_start}-{page_end} FAILED ---\n{str(e)}"
            )

    return "\n".join(extracted_pages)
