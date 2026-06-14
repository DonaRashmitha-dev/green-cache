"""Pydantic models for API requests and responses."""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request model for querying the cache/LLM."""

    query: str = Field(..., min_length=1, max_length=4096, description="User query text")
    quality_tier: Literal["brief", "standard", "detailed"] = Field(
        default="standard",
        description="Desired answer quality tier",
    )
    language: Optional[str] = Field(
        default=None,
        description="ISO 639-1 language code (auto-detected if not provided)",
    )
    user_id: Optional[str] = Field(default="anonymous", description="User identifier for passport tracking")
    system_prompt: Optional[str] = Field(
        default=None,
        description="Optional system prompt for LLM context",
    )


class QueryResponse(BaseModel):
    """Response model for cache/LLM queries."""

    query: str = Field(..., description="Original query text")
    response: str = Field(..., description="Generated or cached response")
    cache_hit: bool = Field(..., description="Whether response came from cache")
    cross_language_hit: bool = Field(default=False, description="Whether this was a cross-language cache hit")
    similarity_score: Optional[float] = Field(
        default=None, description="Semantic similarity score if cache hit"
    )
    quality_tier: str = Field(..., description="Quality tier of the response")
    language: str = Field(..., description="Detected or provided language code")
    tokens_saved: int = Field(default=0, description="Estimated tokens saved by cache hit")
    water_saved_ml: float = Field(default=0.0, description="Estimated water saved in milliliters")
    energy_saved_wh: float = Field(default=0.0, description="Estimated energy saved in watt-hours")
    latency_ms: float = Field(..., description="Total response latency in milliseconds")
    cache_backend: str = Field(..., description="Active cache backend")


class CacheStats(BaseModel):
    """Cache statistics response model."""

    total_requests: int = Field(..., description="Total number of requests")
    cache_hits: int = Field(..., description="Number of cache hits")
    cache_misses: int = Field(..., description="Number of cache misses")
    hit_rate: float = Field(..., description="Cache hit rate (0.0 to 1.0)")
    total_tokens_saved: int = Field(..., description="Total tokens saved")
    total_water_saved_ml: float = Field(..., description="Total water saved in ml")
    total_energy_saved_wh: float = Field(..., description="Total energy saved in Wh")
    avg_latency_hit_ms: float = Field(..., description="Average latency on cache hits")
    avg_latency_miss_ms: float = Field(..., description="Average latency on cache misses")
    entries_count: int = Field(..., description="Number of entries in cache")
    backend: str = Field(..., description="Active cache backend")


class ImpactMetrics(BaseModel):
    """Environmental impact metrics."""

    total_queries: int = Field(..., description="Total queries processed")
    cache_hit_rate: float = Field(..., description="Overall cache hit rate")
    total_tokens_saved: int = Field(..., description="Total tokens saved")
    total_energy_saved_wh: float = Field(..., description="Total energy saved in Wh")
    total_water_saved_ml: float = Field(..., description="Total water saved in ml")
    total_water_saved_liters: float = Field(..., description="Total water saved in liters")
    equivalent_cars_km: float = Field(
        ..., description="Equivalent car kilometers avoided (assuming 120g CO2/km)"
    )
    equivalent_trees: float = Field(
        ..., description="Equivalent trees planted (assuming 22kg CO2/tree/year)"
    )
