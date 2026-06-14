"""Tests for embedding service."""

from src.embedding.embedder import EmbeddingService


def test_embed():
    embedder = EmbeddingService()
    embedding = embedder.embed("Hello world")
    assert len(embedding) == embedder.dimension
    assert isinstance(embedding, list)
    assert all(isinstance(x, float) for x in embedding)


def test_similarity_same_text():
    embedder = EmbeddingService()
    emb = embedder.embed("test query")
    score = embedder.compute_similarity(emb, emb)
    assert score == 1.0


def test_similarity_different_text():
    embedder = EmbeddingService()
    emb1 = embedder.embed("What is Python?")
    emb2 = embedder.embed("How do I cook pasta?")
    score = embedder.compute_similarity(emb1, emb2)
    assert 0.0 <= score < 0.5


def test_multilingual_similarity():
    embedder = EmbeddingService()
    emb1 = embedder.embed("What is the capital of France?")
    emb2 = embedder.embed("ఫ్రాన్స్ రాజధాని ఏమిటి?")
    score = embedder.compute_similarity(emb1, emb2)
    assert score > 0.8, f"Multilingual similarity too low: {score}"
