from fastapi import FastAPI

from app.db.init_db import init_db
from app.api.auth import router as auth_router
from app.api.documents import router as documents_router



from sqlalchemy import text
from app.db.database import engine

app = FastAPI()


@app.on_event("startup")
def startup():

    init_db()

app.include_router(auth_router)
app.include_router(documents_router)

@app.get("/")
def root():

    return {
        "status": "running"
    }

@app.get("/health/db")
def db_health():

    with engine.connect() as conn:

        conn.execute(text("SELECT 1"))

    return {
        "database": "connected"
    }