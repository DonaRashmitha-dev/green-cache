"""Tests for cache backends."""

import pytest

from src.cache.lsh_cache import LSHCache
from src.cache.memory_cache import MemoryCache
from src.embedding.embedder import EmbeddingService


@pytest.fixture
def embedder():
    return EmbeddingService()


@pytest.fixture
async def memory_cache():
    cache = MemoryCache(similarity_threshold=0.85)
    yield cache
    await cache.clear()


@pytest.fixture
async def lsh_cache():
    cache = LSHCache(threshold=0.7, similarity_threshold=0.85)
    yield cache
    await cache.clear()


class TestMemoryCache:
    async def test_basic_hit_miss(self, memory_cache, embedder):
        query = "What is Python?"
        embedding = embedder.embed(query)
        response = "Python is a programming language."

        result = await memory_cache.get(query, embedding)
        assert not result.hit

        await memory_cache.set(query, response, embedding, tokens_generated=50)

        result = await memory_cache.get(query, embedding)
        assert result.hit
        assert result.response == response

    async def test_semantic_similarity(self, memory_cache, embedder):
        q1 = "How do I reset my password?"
        q2 = "I forgot my password, how can I recover it?"

        emb1 = embedder.embed(q1)
        emb2 = embedder.embed(q2)

        await memory_cache.set(q1, "Go to settings and click reset.", emb1, tokens_generated=30)

        result = await memory_cache.get(q2, emb2)
        assert result.hit
        assert result.similarity_score > 0.85


class TestLSHCache:
    async def test_lsh_multilingual_match(self, lsh_cache, embedder):
        queries = {
            "en": "What is the capital of France?",
            "te": "ఫ్రాన్స్ రాజధాని ఏమిటి?",
            "hi": "फ्रांस की राजधानी क्या है?",
        }

        embeddings = {lang: embedder.embed(q) for lang, q in queries.items()}

        await lsh_cache.set(
            queries["en"], "Paris", embeddings["en"], language="en", tokens_generated=10
        )

        result_te = await lsh_cache.get(queries["te"], embeddings["te"])
        assert result_te.hit, "Telugu query should match English cache entry"

        result_hi = await lsh_cache.get(queries["hi"], embeddings["hi"])
        assert result_hi.hit, "Hindi query should match English cache entry"
