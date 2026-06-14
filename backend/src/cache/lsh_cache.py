"""LSH-based intent fingerprinting cache for multilingual queries."""

import time
from typing import Dict, List, Optional, Set

import structlog
from datasketch import MinHash, MinHashLSH

from src.cache.base import BaseCache, CacheEntry, CacheResult, CacheStats
from src.config import settings
from src.embedding.embedder import get_embedder

logger = structlog.get_logger(__name__)


def _tokenize(text: str) -> List[str]:
    """Simple tokenization for LSH shingles."""
    words = text.lower().strip().split()
    if len(words) < 2:
        return words
    return [f"{words[i]}_{words[i+1]}" for i in range(len(words) - 1)]


class LSHCache(BaseCache):
    """Locality-Sensitive Hashing cache for fast multilingual intent matching."""

    def __init__(
        self,
        num_perm: int | None = None,
        threshold: float | None = None,
        similarity_threshold: float | None = None,
    ) -> None:
        self._num_perm = num_perm or settings.lsh_num_perm
        self._lsh_threshold = threshold or settings.lsh_threshold
        self._similarity_threshold = similarity_threshold or settings.similarity_threshold
        self._embedder = get_embedder()

        self._lsh = MinHashLSH(threshold=self._lsh_threshold, num_perm=self._num_perm)
        self._entries: Dict[str, CacheEntry] = {}
        self._minhashes: Dict[str, MinHash] = {}
        self._stats = CacheStats()

        logger.info(
            "lsh_cache_initialized",
            num_perm=self._num_perm,
            lsh_threshold=self._lsh_threshold,
            similarity_threshold=self._similarity_threshold,
        )

    def _create_minhash(self, text: str) -> MinHash:
        """Create a MinHash fingerprint from text."""
        m = MinHash(num_perm=self._num_perm)
        tokens = _tokenize(text)
        for token in tokens:
            m.update(token.encode("utf-8"))
        return m

    async def get(
        self, query: str, embedding: List[float], quality_tier: str = "standard"
    ) -> CacheResult:
        start_time = time.time()
        self._stats.total_requests += 1

        if not self._entries:
            self._stats.cache_misses += 1
            latency_ms = (time.time() - start_time) * 1000
            self._stats.total_latency_miss_ms += latency_ms
            return CacheResult(hit=False)

        query_minhash = self._create_minhash(query)
        candidate_keys: Set[str] = set()

        try:
            lsh_results = self._lsh.query(query_minhash)
            candidate_keys = set(lsh_results)
        except Exception as e:
            logger.warning("lsh_query_failed", error=str(e))

        if not candidate_keys:
            self._stats.cache_misses += 1
            latency_ms = (time.time() - start_time) * 1000
            self._stats.total_latency_miss_ms += latency_ms
            return CacheResult(hit=False)

        best_match: Optional[CacheEntry] = None
        best_score = 0.0

        for key in candidate_keys:
            entry = self._entries.get(key)
            if not entry or entry.quality_tier != quality_tier:
                continue

            score = self._embedder.compute_similarity(embedding, entry.embedding)
            if score > best_score:
                best_score = score
                best_match = entry

        if best_match and best_score >= self._similarity_threshold:
            best_match.hit_count += 1
            self._stats.cache_hits += 1
            self._stats.total_tokens_saved += best_match.tokens_generated
            latency_ms = (time.time() - start_time) * 1000
            self._stats.total_latency_hit_ms += latency_ms

            logger.info(
                "lsh_cache_hit",
                similarity_score=round(best_score, 4),
                lsh_candidates=len(candidate_keys),
                quality_tier=quality_tier,
                hit_count=best_match.hit_count,
            )

            return CacheResult(
                hit=True,
                response=best_match.response,
                similarity_score=best_score,
                entry=best_match,
                tokens_saved=best_match.tokens_generated,
            )

        self._stats.cache_misses += 1
        latency_ms = (time.time() - start_time) * 1000
        self._stats.total_latency_miss_ms += latency_ms

        logger.info(
            "lsh_cache_miss",
            lsh_candidates=len(candidate_keys),
            best_similarity=round(best_score, 4) if best_match else None,
            quality_tier=quality_tier,
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
    ) -> None:
        key = f"{quality_tier}:{self._embedder.get_fingerprint(query)}"

        entry = CacheEntry(
            query=query,
            response=response,
            embedding=embedding,
            quality_tier=quality_tier,
            language=language,
            tokens_generated=tokens_generated,
        )

        minhash = self._create_minhash(query)

        if key in self._entries:
            old_minhash = self._minhashes.get(key)
            if old_minhash:
                self._lsh.remove(key)

        self._lsh.insert(key, minhash)
        self._entries[key] = entry
        self._minhashes[key] = minhash
        self._stats.entries_count = len(self._entries)

        logger.info(
            "lsh_cache_entry_stored",
            key=key,
            quality_tier=quality_tier,
            language=language,
            lsh_buckets=len(self._lsh.keys),
        )

    async def get_stats(self) -> CacheStats:
        self._stats.entries_count = len(self._entries)
        return self._stats

    async def clear(self) -> None:
        self._lsh = MinHashLSH(threshold=self._lsh_threshold, num_perm=self._num_perm)
        self._entries.clear()
        self._minhashes.clear()
        self._stats = CacheStats()
        logger.info("lsh_cache_cleared")

    @property
    def backend_name(self) -> str:
        return "lsh"
