import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

celery_app = Celery(
    "worker",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND"),
    include=["app.tasks.document_tasks"]
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True
)


# Initialize database on worker startup
@celery_app.on_after_configure.connect
def setup_db(sender, **kwargs):
    # Import all models first to register them with SQLAlchemy Base
    from app.models import User, Document, DocumentChunk, ChatSession, Message  # noqa: F401
    from app.db.init_db import init_db
    init_db()