"""FastAPI routes for Green Cache with Smart Language-Aware Cache."""

import time

import structlog
from fastapi import APIRouter, HTTPException, Response

from src.preprocessing.pii_scrubber import scrub, is_safe_to_cache
from src.preprocessing.cacheability_scorer import should_cache, get_ttl_seconds, score as cache_score
from src.preprocessing.normalizer import normalize, normalize_for_cache_key
from src.preprocessing.quality_scorer import score_response, should_cache_response
from src.preprocessing.model_tagger import make_model_tag
from src.preprocessing.user_passport import get_passport
from src.api.models import CacheStats, ImpactMetrics, QueryRequest, QueryResponse
from src.cache.base import BaseCache
from src.cache.lsh_cache import LSHCache
from src.cache.memory_cache import MemoryCache
from src.cache.redis_cache import RedisCache
from src.config import settings
from src.embedding.embedder import get_embedder
from src.llm.client import get_llm_client
from src.metrics.impact_calculator import get_impact_calculator
from src.metrics.prometheus_exporter import (
    CACHE_ENTRIES, CACHE_HIT_RATE, CARBON_SAVED_G, EMBEDDING_LATENCY,
    ENERGY_SAVED_WH, LLM_LATENCY, REQUEST_COUNT, REQUEST_LATENCY,
    TOKENS_SAVED_TOTAL, WATER_SAVED_LITERS, WATER_SAVED_ML, get_metrics,
)

logger = structlog.get_logger(__name__)
router = APIRouter()
_cache: BaseCache | None = None


def get_cache() -> BaseCache:
    global _cache
    if _cache is None:
        if settings.cache_backend == "redis":
            _cache = RedisCache()
        elif settings.cache_backend == "lsh":
            _cache = LSHCache()
        else:
            _cache = MemoryCache()
        logger.info("cache_backend_initialized", backend=settings.cache_backend)
    return _cache


def detect_language(text: str) -> str:
    """Detect language using Unicode character ranges (100% reliable for CJK/Indic)."""
    if any('\u3040' <= char <= '\u309f' or '\u30a0' <= char <= '\u30ff' for char in text):
        return "ja"
    if any('\uac00' <= char <= '\ud7af' for char in text):
        return "ko"
    if any('\u4e00' <= char <= '\u9fff' for char in text):
        return "zh"
    if any('\u0900' <= char <= '\u097f' for char in text):
        return "hi"
    if any('\u0c00' <= char <= '\u0c7f' for char in text):
        return "te"
    if any('\u0600' <= char <= '\u06ff' for char in text):
        return "ar"
    if any('\u0400' <= char <= '\u04ff' for char in text):
        return "ru"
    try:
        from langdetect import detect_langs
        probs = detect_langs(text)
        if probs:
            lang = probs[0].lang
            lang_map = {"zh-cn": "zh", "zh-tw": "zh", "zh-hk": "zh",
                        "es": "es", "en": "en", "fr": "fr", "de": "de",
                        "it": "it", "pt": "pt"}
            return lang_map.get(lang, lang[:2])
    except Exception:
        pass
    return "en"


def translate_prompt(original_response: str, target_language: str) -> str:
    lang_names = {
        "zh": "Simplified Chinese",
        "ja": "Japanese",
        "es": "Spanish",
        "ko": "Korean",
        "en": "English",
        "hi": "Hindi",
        "te": "Telugu",
        "fr": "French",
        "de": "German",
    }
    lang_name = lang_names.get(target_language, target_language)
    return "Translate the following text to " + lang_name + ". Output only the translation, nothing else:\n\n" + original_response


@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    start_time = time.time()
    cache = get_cache()
    embedder = get_embedder()
    llm_client = get_llm_client()
    model_tag = make_model_tag(llm_client.provider, llm_client.model)
    impact_calc = get_impact_calculator()
    passport = get_passport()

    clean_query, pii_found = scrub(request.query)
    if pii_found:
        logger.info('pii_detected_and_scrubbed', original=request.query[:30])
    cacheable = should_cache(clean_query)
    ttl = get_ttl_seconds(clean_query)
    c_score = cache_score(clean_query)
    logger.info('cacheability_scored', score=round(c_score,2), ttl=ttl, cacheable=cacheable)
    clean_query = normalize(clean_query)
    detected_language = request.language or detect_language(clean_query)
    logger.info("language_detected", query=clean_query[:50], language=detected_language)

    embed_start = time.time()
    embedding = embedder.embed(clean_query)
    embed_latency = time.time() - embed_start
    EMBEDDING_LATENCY.observe(embed_latency)

    cache_result = await cache.get(
        clean_query, embedding, quality_tier=request.quality_tier, language=detected_language
    )

    if cache_result.hit and cache_result.entry:
        total_latency_ms = (time.time() - start_time) * 1000

        if cache_result.cross_language_hit:
            logger.info("cross_language_translation_needed",
                        from_lang=cache_result.entry.language, to_lang=detected_language)

            translate_start = time.time()
            try:
                translated_response, translate_tokens = llm_client.generate(
                    translate_prompt(cache_result.entry.response, detected_language),
                    system_prompt="You are a precise translator. Output only the translation, nothing else.",
                    quality_tier="brief",
                )
                translated_response = translated_response.strip()
            except RuntimeError as e:
                logger.error("translation_failed", error=str(e))
                translated_response = cache_result.entry.response

            translate_latency = (time.time() - translate_start) * 1000
            logger.info("translation_complete",
                        translate_latency_ms=round(translate_latency, 2), translate_tokens=translate_tokens)

            await cache.set(query=clean_query, response=translated_response, embedding=embedding,
                          quality_tier=request.quality_tier, language=detected_language,
                          tokens_generated=translate_tokens)

            full_tokens = cache_result.tokens_saved
            actual_tokens_saved = int(full_tokens * 0.9)
            savings = impact_calc.calculate_savings(actual_tokens_saved)

            REQUEST_COUNT.labels(cache_backend=cache.backend_name, cache_hit="true",
                               quality_tier=request.quality_tier).inc()
            REQUEST_LATENCY.labels(cache_backend=cache.backend_name, cache_hit="true").observe(total_latency_ms / 1000)
            TOKENS_SAVED_TOTAL.labels(cache_backend=cache.backend_name).inc(actual_tokens_saved)
            ENERGY_SAVED_WH.labels(cache_backend=cache.backend_name).inc(savings["energy_saved_wh"])
            WATER_SAVED_ML.labels(cache_backend=cache.backend_name).inc(savings["water_saved_ml"])
            CARBON_SAVED_G.labels(cache_backend=cache.backend_name).inc(savings["carbon_saved_g"])

            stats = await cache.get_stats()
            total_water_ml = stats.total_tokens_saved * savings["water_saved_ml"] / max(actual_tokens_saved, 1)
            WATER_SAVED_LITERS.labels(cache_backend=cache.backend_name).set(total_water_ml / 1000)

            return QueryResponse(
                query=request.query, response=translated_response, cache_hit=True, cross_language_hit=True,
                similarity_score=cache_result.similarity_score, quality_tier=request.quality_tier,
                language=detected_language, tokens_saved=actual_tokens_saved,
                water_saved_ml=round(savings["water_saved_ml"], 4),
                energy_saved_wh=round(savings["energy_saved_wh"], 6),
                latency_ms=round(total_latency_ms, 2), cache_backend=cache.backend_name,
            )

        savings = impact_calc.calculate_savings(cache_result.tokens_saved)
        REQUEST_COUNT.labels(cache_backend=cache.backend_name, cache_hit="true",
                           quality_tier=request.quality_tier).inc()
        REQUEST_LATENCY.labels(cache_backend=cache.backend_name, cache_hit="true").observe(total_latency_ms / 1000)
        TOKENS_SAVED_TOTAL.labels(cache_backend=cache.backend_name).inc(cache_result.tokens_saved)
        ENERGY_SAVED_WH.labels(cache_backend=cache.backend_name).inc(savings["energy_saved_wh"])
        WATER_SAVED_ML.labels(cache_backend=cache.backend_name).inc(savings["water_saved_ml"])
        CARBON_SAVED_G.labels(cache_backend=cache.backend_name).inc(savings["carbon_saved_g"])

        stats = await cache.get_stats()
        total_water_ml = stats.total_tokens_saved * savings["water_saved_ml"] / max(cache_result.tokens_saved, 1)
        WATER_SAVED_LITERS.labels(cache_backend=cache.backend_name).set(total_water_ml / 1000)

        passport.record(request.user_id or "anonymous", cache_hit=True, tokens_saved=cache_result.tokens_saved, water_saved_ml=savings.get("water_saved_ml",0), energy_saved_wh=savings.get("energy_saved_wh",0), carbon_saved_g=savings.get("carbon_saved_g",0))
        return QueryResponse(
            query=request.query, response=cache_result.response, cache_hit=True, cross_language_hit=False,
            similarity_score=cache_result.similarity_score, quality_tier=request.quality_tier,
            language=detected_language, tokens_saved=cache_result.tokens_saved,
            water_saved_ml=round(savings["water_saved_ml"], 4),
            energy_saved_wh=round(savings["energy_saved_wh"], 6),
            latency_ms=round(total_latency_ms, 2), cache_backend=cache.backend_name,
        )

    llm_start = time.time()
    try:
        response_text, output_tokens = llm_client.generate(
            clean_query, system_prompt=request.system_prompt, quality_tier=request.quality_tier)
    except RuntimeError as e:
        logger.error("llm_call_failed", error=str(e))
        raise HTTPException(status_code=503, detail=str(e))

    llm_latency = time.time() - llm_start
    LLM_LATENCY.observe(llm_latency)

    await cache.set(query=clean_query, response=response_text, embedding=embedding,
                  quality_tier=request.quality_tier, language=detected_language, tokens_generated=output_tokens, model_tag=model_tag)

    total_latency_ms = (time.time() - start_time) * 1000
    REQUEST_COUNT.labels(cache_backend=cache.backend_name, cache_hit="false",
                       quality_tier=request.quality_tier).inc()
    REQUEST_LATENCY.labels(cache_backend=cache.backend_name, cache_hit="false").observe(total_latency_ms / 1000)

    passport.record(request.user_id or "anonymous", cache_hit=False)
    return QueryResponse(
        query=request.query, response=response_text, cache_hit=False, cross_language_hit=False,
        similarity_score=None, quality_tier=request.quality_tier, language=detected_language,
        tokens_saved=0, water_saved_ml=0.0, energy_saved_wh=0.0,
        latency_ms=round(total_latency_ms, 2), cache_backend=cache.backend_name,
    )


@router.get("/stats", response_model=CacheStats)
async def get_cache_stats() -> CacheStats:
    cache = get_cache()
    stats = await cache.get_stats()
    CACHE_HIT_RATE.labels(cache_backend=cache.backend_name).set(stats.hit_rate)
    CACHE_ENTRIES.labels(cache_backend=cache.backend_name).set(stats.entries_count)
    return CacheStats(
        total_requests=stats.total_requests, cache_hits=stats.cache_hits, cache_misses=stats.cache_misses,
        hit_rate=stats.hit_rate, total_tokens_saved=stats.total_tokens_saved,
        total_water_saved_ml=0.0, total_energy_saved_wh=0.0,
        avg_latency_hit_ms=stats.avg_latency_hit_ms, avg_latency_miss_ms=stats.avg_latency_miss_ms,
        entries_count=stats.entries_count, backend=cache.backend_name,
    )


@router.get("/impact", response_model=ImpactMetrics)
async def get_impact_metrics() -> ImpactMetrics:
    cache = get_cache()
    stats = await cache.get_stats()
    impact_calc = get_impact_calculator()
    avg_tokens = 500
    total_tokens = stats.total_tokens_saved if stats.total_tokens_saved > 0 else stats.cache_hits * avg_tokens
    savings = impact_calc.calculate_savings(total_tokens)
    context = impact_calc.contextualize(savings["energy_saved_wh"], savings["carbon_saved_g"])
    return ImpactMetrics(
        total_queries=stats.total_requests, cache_hit_rate=stats.hit_rate, total_tokens_saved=total_tokens,
        total_energy_saved_wh=round(savings["energy_saved_wh"], 4),
        total_water_saved_ml=round(savings["water_saved_ml"], 4),
        total_water_saved_liters=round(savings["water_saved_ml"] / 1000, 6),
        equivalent_cars_km=context["equivalent_car_km"], equivalent_trees=context["equivalent_trees_year"],
    )



@router.get("/passport/{user_id}")
async def get_user_passport(user_id: str) -> dict:
    passport = get_passport()
    data = passport.get(user_id)
    if not data:
        return {"user_id": user_id, "message": "No data yet", "total_queries": 0}
    return data


@router.get("/passport")
async def get_leaderboard() -> dict:
    passport = get_passport()
    return {"leaderboard": passport.leaderboard(top_n=10), "total_users": len(passport._users)}

@router.get("/carbon")
async def get_carbon() -> dict:
    from src.metrics.carbon_intensity import get_carbon_intensity
    return await get_carbon_intensity("uk")

@router.get("/carbon")
async def get_carbon() -> dict:
    from src.metrics.carbon_intensity import get_carbon_intensity
    return await get_carbon_intensity("uk")

@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "backend": settings.cache_backend}


@router.get("/metrics")
async def metrics() -> Response:
    return Response(content=get_metrics(), media_type="text/plain")


@router.delete("/cache")
async def clear_cache() -> dict[str, str]:
    cache = get_cache()
    await cache.clear()
    logger.info("cache_cleared", backend=cache.backend_name)
    return {"status": "cleared", "backend": cache.backend_name}