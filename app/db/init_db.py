import time

from sqlalchemy.exc import OperationalError
from sqlalchemy import text

from app.db.database import engine


def init_db():
    

    for _ in range(10):
        try:
            with engine.begin() as conn:
                conn.execute(text("SELECT 1"))

                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

            print("Database connected successfully.")
            return

        except OperationalError:
            print("Database not ready. Retrying...")
            time.sleep(2)

    raise Exception("Could not connect to the database.")