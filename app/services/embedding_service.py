from langchain_ollama import OllamaEmbeddings
import os


class EmbeddingService:

    def __init__(self):
        self.embeddings = OllamaEmbeddings(
            model=os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text"),
            base_url=os.getenv("OLLAMA_URL", "http://ollama:11434"),
        )

    def embed(self, text: str) -> list[float]:
        return self.embeddings.embed_query(text)

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        if hasattr(self.embeddings, "embed_documents"):
            return self.embeddings.embed_documents(texts)

        return [self.embeddings.embed_query(text) for text in texts]


embedding_service = EmbeddingService()
