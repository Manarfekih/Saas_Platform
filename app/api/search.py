from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.db.database import SessionLocal
from app.services.retrieval_service import retrieve_chunks

router = APIRouter()


class SearchRequest(BaseModel):
    query: str
    limit: int = 5


@router.post("/documents/{document_id}/search")
def search(
    document_id: int,
    request: SearchRequest,
):
    db = SessionLocal()

    try:
        results = retrieve_chunks(
            db=db,
            document_id=document_id,
            query=request.query,
            limit=request.limit,
        )

        return {
            "query": request.query,
            "results_count": len(results),
            "results": [
                {
                    "chunk_id": r.chunk_id,
                    "document_id": r.document_id,
                    "chunk_index": r.chunk_index,
                    "content": r.content,
                    "distance": float(r.distance),
                }
                for r in results
            ],
        }

    finally:
        db.close()
