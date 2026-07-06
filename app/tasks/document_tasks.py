from app.celery_app import celery_app

from app.db.database import SessionLocal

from app.models.document import Document

from app.services.extraction_service import extract_text

from app.services.classification_service import (
    classify_sections,
    render_classified_block,
)

from app.services.chunking_service import (
    chunk_text,
    combine_with_classification,
)

from app.services.chunk_storage_service import save_chunks

from app.services.embedding_service import embedding_service


@celery_app.task(
    bind=True,
    max_retries=3
)
def process_document(
    self,
    document_id: int
):

    db = SessionLocal()
    document = None

    try:
        document = db.query(
            Document
        ).filter(
            Document.id == document_id
        ).first()

        if not document:
            return

        document.status = "processing"
        document.progress = 10
        db.commit()

        text = extract_text(
            document.file_path
        )

        if not text:
            raise Exception(
                "Empty document"
            )

        document.extracted_text = text
        document.progress = 40
        db.commit()

        try:
            classified_items = classify_sections(
                text,
                doc_type=None
            )

            classified_block = render_classified_block(
                classified_items,
                doc_type=None
            )

        except Exception:
            classified_block = ""

        text_for_chunking = combine_with_classification(
            text,
            classified_block
        )

        document.progress = 55
        db.commit()

        chunks = chunk_text(
            text_for_chunking
        )

        saved = save_chunks(
            db,
            document_id,
            chunks
        )

        document.progress = 70
        db.commit()

        vectors = embedding_service.embed_many(
            [
                c.content
                for c in saved
            ]
        )

        for chunk, vector in zip(
            saved,
            vectors
        ):
            chunk.embedding = vector

        document.total_chunks = len(saved)
        document.status = "processed"
        document.progress = 100
        db.commit()

    except Exception as e:
        db.rollback()

        if document:
            document.status = "failed"
            document.error_message = str(e)
            db.commit()

        raise

    finally:
        db.close()
