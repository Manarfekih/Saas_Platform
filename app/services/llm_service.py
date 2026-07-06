import os
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_llm():
    try:
        from langchain_ollama import ChatOllama
    except ImportError as exc:
        raise RuntimeError(
            "langchain_ollama is not installed; Ollama-backed LLM "
            "features are unavailable."
        ) from exc

    return ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "qwen3:8b"),
        base_url=os.getenv("OLLAMA_URL", "http://ollama:11434"),
        temperature=0,
        num_ctx=4096,
        num_predict=1024,
        model_kwargs={
            "think": False
        }
    )


def ask_llm(prompt: str):
    try:
        llm = get_llm()
        response = llm.invoke(prompt)

        if hasattr(response, "content"):
            return response.content
        return str(response)

    except Exception as e:
        logger.error(f"LLM error: {str(e)}")
        raise
