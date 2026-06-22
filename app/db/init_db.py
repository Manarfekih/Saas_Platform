import time

from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.db.database import Base
from app.db.database import engine

from app.models.user import User
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.message import Message
from app.models.chat_session import ChatSession

def init_db():
    for i in range(10):
        try:
            with engine.connect():
                pass

            print("DB connected")

            with engine.begin() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

            Base.metadata.create_all(bind=engine)
            return
        except OperationalError:
            print("DB not ready, retrying...")
            time.sleep(2)

    raise Exception("DB connection failed")
