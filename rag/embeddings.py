"""Thin LangChain adapter for a local, free FastEmbed/ONNX embedding model."""
from __future__ import annotations

from langchain_core.embeddings import Embeddings

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class MiniLMEmbeddings(Embeddings):
    """Produce 384-dimensional vectors; model is downloaded on first use."""

    def __init__(self) -> None:
        from fastembed import TextEmbedding
        self._model = TextEmbedding(model_name=MODEL_NAME)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [vector.tolist() for vector in self._model.embed(texts, batch_size=16)]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]
