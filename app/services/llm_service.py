import os

from langchain_ollama import ChatOllama


llm = ChatOllama(
    model=os.getenv("OLLAMA_MODEL", "qwen3:8b"),
    base_url=os.getenv("OLLAMA_URL", "http://ollama:11434"),
    temperature=0,
)


def ask_llm(prompt: str):
    return llm.invoke(prompt)