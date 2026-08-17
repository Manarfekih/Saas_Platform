import os
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self):
        self.model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
        self.base_url = os.getenv("OLLAMA_URL", "http://ollama:11434")
        self._embeddings = None

    def _get_embeddings(self):
        if self._embeddings is None:
            try:
                from langchain_ollama import OllamaEmbeddings
            except ImportError as exc:
                raise RuntimeError(
                    "langchain_ollama is not installed; Ollama-backed "
                    "embedding features are unavailable."
                ) from exc

            self._embeddings = OllamaEmbeddings(
                model=self.model,
                base_url=self.base_url,
            )

        return self._embeddings

    def embed(self, text: str) -> list[float]:
        try:
            if not text or not text.strip():
                logger.warning("Empty text for embedding, using fallback")
                return [0.0] * 768

            embedding = self._get_embeddings().embed_query(text)
            logger.info(f"Generated embedding of length {len(embedding)}")
            return embedding
        except Exception as e:
            logger.error(f"Embedding error: {str(e)}")
            return [0.0] * 768

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        valid_texts = [t for t in texts if t and t.strip()]
        if not valid_texts:
            return []

        try:
            embeddings = self._get_embeddings().embed_documents(valid_texts)
            logger.info(f"Generated {len(embeddings)} embeddings for {len(valid_texts)} chunks")

            result = []
            text_idx = 0
            for text in texts:
                if text and text.strip():
                    result.append(embeddings[text_idx])
                    text_idx += 1
                else:
                    result.append([0.0] * 768)
            return result

        except Exception as e:
            logger.error(f"Batch embedding error: {str(e)}")
            return [[0.0] * 768 for _ in texts]


embedding_service = EmbeddingService()