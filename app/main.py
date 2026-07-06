from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.db.init_db import init_db
from app.db.database import engine

from app.api.auth import router as auth_router
from app.api.documents import router as documents_router
from app.api.search import router as search_router
from app.api.rag import router as rag_router
from app.api.global_chat import router as global_chat_router

from app.api.dashboard import router as dashboard_router

app = FastAPI(title="AI SaaS Platform")


# CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.on_event("startup")
def startup():
    init_db()


# ROUTERS

app.include_router(auth_router, tags=["Auth"])
app.include_router(documents_router, tags=["Documents"])
app.include_router(search_router, tags=["Search"])
app.include_router(rag_router, tags=["RAG"])
app.include_router(global_chat_router, tags=["Global Chat"])
app.include_router(dashboard_router, tags=["Dashboard"])

# ROOT


@app.get("/")
def root():
    return {
        "status": "running",
        "version": "1.0"
    }


# HEALTH CHECK for db connection

@app.get("/health/db")
def db_health():

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        return {
            "database": "connected"
        }

    except Exception as e:
        return {
            "database": "disconnected",
            "error": str(e)
        }