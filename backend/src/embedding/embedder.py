"""Embedding service for query vectorization."""

import hashlib
from typing import List

import numpy as np
import structlog
from sentence_transformers import SentenceTransformer

from src.config import settings

logger = structlog.get_logger(__name__)


class EmbeddingService:
    """Service for generating multilingual text embeddings."""

    _instance: "EmbeddingService | None" = None
    _model: SentenceTransformer | None = None

    def __new__(cls) -> "EmbeddingService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._model is None:
            logger.info(
                "loading_embedding_model",
                model=settings.embedding_model,
            )
            self._model = SentenceTransformer(settings.embedding_model)
            self._dimension = self._model.get_sentence_embedding_dimension()
            logger.info(
                "embedding_model_loaded",
                model=settings.embedding_model,
                dimension=self._dimension,
            )

    @property
    def dimension(self) -> int:
        if self._model is None:
            raise RuntimeError("Embedding model not initialized")
        return self._model.get_sentence_embedding_dimension() or 384

    def embed(self, text: str) -> List[float]:
        if self._model is None:
            raise RuntimeError("Embedding model not initialized")

        embedding = self._model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
        return embedding.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if self._model is None:
            raise RuntimeError("Embedding model not initialized")

        embeddings = self._model.encode(
            texts, convert_to_numpy=True, normalize_embeddings=True, batch_size=32
        )
        return embeddings.tolist()

    def compute_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        a = np.array(vec1, dtype=np.float32)
        b = np.array(vec2, dtype=np.float32)
        dot = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(dot / (norm_a * norm_b))

    def get_fingerprint(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()


_embedder: EmbeddingService | None = None


def get_embedder() -> EmbeddingService:
    global _embedder
    if _embedder is None:
        _embedder = EmbeddingService()
    return _embedder
