from __future__ import annotations

from typing import Iterable, Type

from sqlalchemy import inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeMeta

from app.core.logger import logger


def validate_table_columns(engine: Engine, model: Type[DeclarativeMeta]) -> None:
    table_name = model.__tablename__
    inspector = inspect(engine)

    if not inspector.has_table(table_name):
        raise RuntimeError(f"Database table '{table_name}' does not exist")

    db_columns = {column["name"] for column in inspector.get_columns(table_name)}
    model_columns = {column.name for column in model.__table__.columns}

    missing_columns = sorted(model_columns - db_columns)
    if missing_columns:
        raise RuntimeError(
            f"Database table '{table_name}' is missing required columns: "
            f"{', '.join(missing_columns)}"
        )

    extra_columns = sorted(db_columns - model_columns)
    if extra_columns:
        logger.warning(
            "Database table '%s' has columns not declared on the model: %s",
            table_name,
            ", ".join(extra_columns),
        )


def validate_runtime_schema(engine: Engine, models: Iterable[Type[DeclarativeMeta]]) -> None:
    for model in models:
        validate_table_columns(engine, model)
