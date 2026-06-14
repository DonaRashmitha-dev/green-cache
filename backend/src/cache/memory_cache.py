"""In-memory semantic cache with cosine similarity search and language awareness."""

import time
from typing import Dict, List, Optional

import structlog

from src.cache.base import BaseCache, CacheEntry, CacheResult, CacheStats
from src.config import settings
from src.embedding.embedder import get_embedder

logger = structlog.get_logger(__name__)


class MemoryCache(BaseCache):
    """Thread-safe in-memory semantic cache using cosine similarity with language awareness."""

    def __init__(self, similarity_threshold: float | None = None) -> None:
        self._cache: Dict[str, CacheEntry] = {}
        self._similarity_threshold = similarity_threshold or settings.similarity_threshold
        self._stats = CacheStats()
        self._embedder = get_embedder()
        logger.info(
            "memory_cache_initialized",
            similarity_threshold=self._similarity_threshold,
        )

    def _make_key(self, intent_fingerprint: str, quality_tier: str, language: str) -> str:
        """Create composite cache key: intent + quality + language."""
        return f"{quality_tier}:{language}:{intent_fingerprint}"

    async def get(
        self, query: str, embedding: List[float], quality_tier: str = "standard", language: str = "en"
    ) -> CacheResult:
        start_time = time.time()
        self._stats.total_requests += 1

        if not self._cache:
            self._stats.cache_misses += 1
            latency_ms = (time.time() - start_time) * 1000
            self._stats.total_latency_miss_ms += latency_ms
            return CacheResult(hit=False)

        # Step 1: Try exact language match first
        intent_fp = self._embedder.get_fingerprint(query)
        exact_key = self._make_key(intent_fp, quality_tier, language)

        if exact_key in self._cache:
            entry = self._cache[exact_key]
            entry.hit_count += 1
            self._stats.cache_hits += 1
            self._stats.total_tokens_saved += entry.tokens_generated
            latency_ms = (time.time() - start_time) * 1000
            self._stats.total_latency_hit_ms += latency_ms

            logger.info(
                "cache_hit_exact_language",
                language=language,
                similarity=1.0,
                quality_tier=quality_tier,
                hit_count=entry.hit_count,
            )

            return CacheResult(
                hit=True,
                response=entry.response,
                similarity_score=1.0,
                entry=entry,
                tokens_saved=entry.tokens_generated,
                cross_language_hit=False,
            )

        # Step 2: Semantic search across all languages
        best_match: Optional[CacheEntry] = None
        best_score = 0.0
        best_key = ""

        for key, entry in self._cache.items():
            # Check quality tier match
            if not key.startswith(f"{quality_tier}:"):
                continue

            score = self._embedder.compute_similarity(embedding, entry.embedding)
            if score > best_score:
                best_score = score
                best_match = entry
                best_key = key

        if best_match and best_score >= self._similarity_threshold:
            # Same language? Direct hit
            if best_match.language == language:
                best_match.hit_count += 1
                self._stats.cache_hits += 1
                self._stats.total_tokens_saved += best_match.tokens_generated
                latency_ms = (time.time() - start_time) * 1000
                self._stats.total_latency_hit_ms += latency_ms

                logger.info(
                    "cache_hit_same_language",
                    similarity_score=round(best_score, 4),
                    language=language,
                    quality_tier=quality_tier,
                    hit_count=best_match.hit_count,
                )

                return CacheResult(
                    hit=True,
                    response=best_match.response,
                    similarity_score=best_score,
                    entry=best_match,
                    tokens_saved=best_match.tokens_generated,
                    cross_language_hit=False,
                )

            # Different language? Cross-language hit
            best_match.hit_count += 1
            self._stats.cache_hits += 1
            self._stats.total_tokens_saved += best_match.tokens_generated
            latency_ms = (time.time() - start_time) * 1000
            self._stats.total_latency_hit_ms += latency_ms

            logger.info(
                "cache_hit_cross_language",
                similarity_score=round(best_score, 4),
                cached_language=best_match.language,
                query_language=language,
                quality_tier=quality_tier,
                hit_count=best_match.hit_count,
            )

            return CacheResult(
                hit=True,
                response=best_match.response,
                similarity_score=best_score,
                entry=best_match,
                tokens_saved=best_match.tokens_generated,
                cross_language_hit=True,
            )

        self._stats.cache_misses += 1
        latency_ms = (time.time() - start_time) * 1000
        self._stats.total_latency_miss_ms += latency_ms

        logger.info(
            "cache_miss",
            best_similarity=round(best_score, 4) if best_match else None,
            quality_tier=quality_tier,
            language=language,
        )
        return CacheResult(hit=False)

    async def set(
        self,
        query: str,
        response: str,
        embedding: List[float],
        quality_tier: str = "standard",
        language: str = "en",
        tokens_generated: int = 0,
        model_tag: str = "unknown",
    ) -> None:
        intent_fp = self._embedder.get_fingerprint(query)
        key = self._make_key(intent_fp, quality_tier, language)

        entry = CacheEntry(
            query=query,
            response=response,
            embedding=embedding,
            quality_tier=quality_tier,
            language=language,
            tokens_generated=tokens_generated,
            model_tag=model_tag,
        )

        self._cache[key] = entry
        self._stats.entries_count = len(self._cache)

        logger.info(
            "cache_entry_stored",
            key=key,
            quality_tier=quality_tier,
            language=language,
            tokens_generated=tokens_generated,
        )

    async def get_stats(self) -> CacheStats:
        self._stats.entries_count = len(self._cache)
        return self._stats

    async def clear(self) -> None:
        self._cache.clear()
        self._stats = CacheStats()
        logger.info("memory_cache_cleared")

    @property
    def backend_name(self) -> str:
        return "memory"
