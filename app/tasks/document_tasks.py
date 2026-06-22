from celery.exceptions import MaxRetriesExceededError

from app.celery_app import celery_app
from app.db.database import SessionLocal
from app.models.document import Document

from app.services.extraction_service import extract_text_llm
from app.services.document_classifier import detect_document_type
from app.services.chunking_service import chunk_text
from app.services.chunk_storage_service import save_chunks
from app.services.embedding_service import embedding_service

from app.core.logger import logger


@celery_app.task(
    bind=True,
    name="app.tasks.document_tasks.process_document",
    max_retries=3,
    default_retry_delay=5,
)
def process_document(self, document_id: int):

    db = SessionLocal()
    document = None

    try:
        logger.info(f"Starting pipeline for document {document_id}")

        document = db.query(Document).filter(
            Document.id == document_id
        ).first()

        if not document:
            return

        # STEP 1
        document.status = "processing"
        document.processing_step = "started"
        document.progress = 5
        db.commit()

        # =========================
        # STEP 2 - LLM EXTRACTION (REPLACES OCR)
        # =========================
        text = extract_text_llm(document.file_path)

        if not text or len(text.strip()) < 20:
            raise ValueError("LLM extraction failed or returned too little text")

        document.extracted_text = text
        document.processing_step = "extracted"
        document.progress = 30
        db.commit()

        # =========================
        # STEP 3 - CLASSIFICATION (LLAMA3 8B)
        # =========================
        doc_type = detect_document_type(text)

        document.doc_type = doc_type
        document.processing_step = "classified"
        document.progress = 45
        db.commit()

        # =========================
        # STEP 4 - CHUNKING
        # =========================
        chunks = chunk_text(text)

        document.processing_step = "chunking"
        document.progress = 60
        db.commit()

        saved_chunks = save_chunks(db, document_id, chunks)

        # =========================
        # STEP 5 - EMBEDDINGS
        # =========================
        document.processing_step = "embedding"
        document.progress = 85
        db.commit()

        vectors = embedding_service.embed_many(
            [chunk.content for chunk in saved_chunks]
        )

        if len(vectors) != len(saved_chunks):
            raise ValueError("Embedding count mismatch")

        for chunk, vector in zip(saved_chunks, vectors):
            if not vector:
                raise ValueError("Invalid embedding")

            chunk.embedding = vector

        db.commit()

        # =========================
        # FINAL
        # =========================
        document.total_chunks = len(saved_chunks)
        document.status = "processed"
        document.processing_step = "completed"
        document.progress = 100

        db.commit()

        logger.info(f"SUCCESS document={document_id}")

    except Exception as e:
        db.rollback()
        logger.error(f"FAILED document={document_id}: {str(e)}")

        if document:
            document.status = "failed"
            document.error_message = str(e)
            db.commit()

        try:
            raise self.retry(exc=e)

        except MaxRetriesExceededError:
            logger.error(f"MAX RETRIES document={document_id}")

    finally:
        db.close()
