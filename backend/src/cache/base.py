"""Base cache interface and shared types."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CacheEntry:
    """Represents a single cache entry."""

    query: str
    response: str
    embedding: List[float]
    quality_tier: str = "standard"
    language: str = "en"
    hit_count: int = 0
    tokens_generated: int = 0
    model_tag: str = "unknown"
    created_at: float = field(default_factory=lambda: __import__("time").time())


@dataclass
class CacheResult:
    """Result of a cache lookup operation."""

    hit: bool
    response: str = ""
    similarity_score: Optional[float] = None
    entry: Optional[CacheEntry] = None
    tokens_saved: int = 0
    cross_language_hit: bool = False


@dataclass
class CacheStats:
    """Statistics for cache performance."""

    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    total_tokens_saved: int = 0
    total_latency_hit_ms: float = 0.0
    total_latency_miss_ms: float = 0.0
    entries_count: int = 0

    @property
    def hit_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.cache_hits / self.total_requests

    @property
    def avg_latency_hit_ms(self) -> float:
        if self.cache_hits == 0:
            return 0.0
        return self.total_latency_hit_ms / self.cache_hits

    @property
    def avg_latency_miss_ms(self) -> float:
        if self.cache_misses == 0:
            return 0.0
        return self.total_latency_miss_ms / self.cache_misses


class BaseCache(ABC):
    """Abstract base class for all cache backends."""

    @abstractmethod
    async def get(
        self, query: str, embedding: List[float], quality_tier: str = "standard", language: str = "en"
    ) -> CacheResult:
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def get_stats(self) -> CacheStats:
        pass

    @abstractmethod
    async def clear(self) -> None:
        pass

    @property
    @abstractmethod
    def backend_name(self) -> str:
        pass
