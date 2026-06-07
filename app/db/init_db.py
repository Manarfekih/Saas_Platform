import time
from sqlalchemy.exc import OperationalError

from app.db.database import Base
from app.db.database import engine

from app.models.user import User
from app.models.document import Document


def init_db():
    for i in range(10):
        try:
            Base.metadata.create_all(bind=engine)
            print("DB connected")
            return
        except OperationalError:
            print("DB not ready, retrying...")
            time.sleep(2)

    raise Exception("DB connection failed")