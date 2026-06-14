"""Prometheus metrics exporter for monitoring."""

from prometheus_client import Counter, Gauge, Histogram, Info, generate_latest

from src.config import settings

APP_INFO = Info("greencache", "Green Cache application information")
APP_INFO.info({"version": "0.1.0", "backend": settings.cache_backend})

REQUEST_COUNT = Counter(
    "greencache_requests_total",
    "Total number of requests",
    ["cache_backend", "cache_hit", "quality_tier"],
)

REQUEST_LATENCY = Histogram(
    "greencache_request_latency_seconds",
    "Request latency in seconds",
    ["cache_backend", "cache_hit"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

CACHE_HIT_RATE = Gauge(
    "greencache_hit_rate",
    "Current cache hit rate",
    ["cache_backend"],
)

CACHE_ENTRIES = Gauge(
    "greencache_entries_count",
    "Number of entries in cache",
    ["cache_backend"],
)

TOKENS_SAVED_TOTAL = Counter(
    "greencache_tokens_saved_total",
    "Total tokens saved by cache hits",
    ["cache_backend"],
)

ENERGY_SAVED_WH = Counter(
    "greencache_energy_saved_wh_total",
    "Total energy saved in watt-hours",
    ["cache_backend"],
)

WATER_SAVED_ML = Counter(
    "greencache_water_saved_ml_total",
    "Total water saved in milliliters",
    ["cache_backend"],
)

WATER_SAVED_LITERS = Gauge(
    "greencache_water_saved_liters",
    "Total water saved in liters (live counter)",
    ["cache_backend"],
)

CARBON_SAVED_G = Counter(
    "greencache_carbon_saved_g_total",
    "Total carbon saved in grams CO2e",
    ["cache_backend"],
)

EMBEDDING_LATENCY = Histogram(
    "greencache_embedding_latency_seconds",
    "Embedding generation latency",
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5],
)

LLM_LATENCY = Histogram(
    "greencache_llm_latency_seconds",
    "LLM API call latency",
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0],
)


def get_metrics() -> bytes:
    return generate_latest()
