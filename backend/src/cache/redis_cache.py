"""Redis-backed semantic cache with vector similarity search."""

import json
import time
from typing import List, Optional

import redis.asyncio as redis
import structlog

from src.cache.base import BaseCache, CacheEntry, CacheResult, CacheStats
from src.config import settings
from src.embedding.embedder import get_embedder

logger = structlog.get_logger(__name__)

REDIS_KEY_PREFIX = "greencache:entry"


class RedisCache(BaseCache):
    """Production-grade Redis-backed semantic cache."""

    def __init__(
        self,
        redis_url: str | None = None,
        similarity_threshold: float | None = None,
        ttl_seconds: int | None = None,
    ) -> None:
        self._redis_url = redis_url or settings.redis_url
        self._similarity_threshold = similarity_threshold or settings.similarity_threshold
        self._ttl = ttl_seconds or settings.redis_ttl_seconds
        self._embedder = get_embedder()
        self._redis: redis.Redis | None = None
        self._local_stats = CacheStats()

    async def _get_redis(self) -> redis.Redis:
        if self._redis is None:
            self._redis = redis.from_url(self._redis_url, decode_responses=True)
        return self._redis

    async def get(
        self, query: str, embedding: List[float], quality_tier: str = "standard"
    ) -> CacheResult:
        start_time = time.time()
        self._local_stats.total_requests += 1

        r = await self._get_redis()

        pattern = f"{REDIS_KEY_PREFIX}:*:{quality_tier}"
        keys = []
        async for key in r.scan_iter(match=pattern):
            keys.append(key)

        if not keys:
            self._local_stats.cache_misses += 1
            latency_ms = (time.time() - start_time) * 1000
            self._local_stats.total_latency_miss_ms += latency_ms
            return CacheResult(hit=False)

        best_match: Optional[CacheEntry] = None
        best_score = 0.0
        best_key = ""

        for key in keys:
            data = await r.hgetall(key)
            if not data:
                continue

            cached_embedding = json.loads(data.get("embedding", "[]"))
            score = self._embedder.compute_similarity(embedding, cached_embedding)

            if score > best_score:
                best_score = score
                best_key = key
                best_match = CacheEntry(
                    query=data.get("query", ""),
                    response=data.get("response", ""),
                    embedding=cached_embedding,
                    quality_tier=data.get("quality_tier", "standard"),
                    language=data.get("language", "en"),
                    tokens_generated=int(data.get("tokens_generated", 0)),
                    hit_count=int(data.get("hit_count", 0)),
                )

        if best_match and best_score >= self._similarity_threshold:
            await r.hincrby(best_key, "hit_count", 1)
            best_match.hit_count += 1

            self._local_stats.cache_hits += 1
            self._local_stats.total_tokens_saved += best_match.tokens_generated
            latency_ms = (time.time() - start_time) * 1000
            self._local_stats.total_latency_hit_ms += latency_ms

            logger.info(
                "redis_cache_hit",
                similarity_score=round(best_score, 4),
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

        self._local_stats.cache_misses += 1
        latency_ms = (time.time() - start_time) * 1000
        self._local_stats.total_latency_miss_ms += latency_ms

        logger.info(
            "redis_cache_miss",
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
        r = await self._get_redis()

        key = f"{REDIS_KEY_PREFIX}:{self._embedder.get_fingerprint(query)}:{quality_tier}"
        data = {
            "query": query,
            "response": response,
            "embedding": json.dumps(embedding),
            "quality_tier": quality_tier,
            "language": language,
            "tokens_generated": str(tokens_generated),
            "hit_count": "0",
            "created_at": str(time.time()),
        }

        await r.hset(key, mapping=data)
        await r.expire(key, self._ttl)

        logger.info(
            "redis_cache_entry_stored",
            key=key,
            quality_tier=quality_tier,
            language=language,
            ttl=self._ttl,
        )

    async def get_stats(self) -> CacheStats:
        r = await self._get_redis()
        pattern = f"{REDIS_KEY_PREFIX}:*"
        count = 0
        async for _ in r.scan_iter(match=pattern):
            count += 1
        self._local_stats.entries_count = count
        return self._local_stats

    async def clear(self) -> None:
        r = await self._get_redis()
        pattern = f"{REDIS_KEY_PREFIX}:*"
        async for key in r.scan_iter(match=pattern):
            await r.delete(key)
        self._local_stats = CacheStats()
        logger.info("redis_cache_cleared")

    @property
    def backend_name(self) -> str:
        return "redis"
