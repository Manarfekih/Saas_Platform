from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Text,
    Index
)

from pgvector.sqlalchemy import Vector

from app.db.database import Base



class DocumentChunk(Base):


    __tablename__="document_chunks"



    id=Column(
        Integer,
        primary_key=True
    )



    document_id=Column(
        Integer,
        ForeignKey(
            "documents.id"
        ),
        nullable=False
    )



    chunk_index=Column(
        Integer,
        nullable=False
    )



    content=Column(
        Text,
        nullable=False
    )



    embedding=Column(
        Vector(768)
    )



Index(
    "chunk_embedding_index",

    DocumentChunk.embedding,

    postgresql_using="ivfflat",

    postgresql_with={
        "lists":100
    }
)