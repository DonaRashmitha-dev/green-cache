"""Grid carbon intensity — live carbon data from electricity grid APIs."""

import time
import httpx
import structlog

logger = structlog.get_logger(__name__)

_cache: dict = {}
_CACHE_TTL = 900


def _is_stale(key: str) -> bool:
    if key not in _cache:
        return True
    return time.time() - _cache[key]["fetched_at"] > _CACHE_TTL


async def get_carbon_intensity_uk() -> dict:
    key = "uk"
    if not _is_stale(key):
        return _cache[key]["data"]
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get("https://api.carbonintensity.org.uk/intensity", headers={"Accept": "application/json"})
            r.raise_for_status()
            data = r.json()
            intensity = data["data"][0]["intensity"]
            result = {
                "region": "UK",
                "actual": intensity.get("actual"),
                "forecast": intensity.get("forecast"),
                "index": intensity.get("index", "unknown"),
                "unit": "gCO2/kWh",
                "source": "carbonintensity.org.uk",
                "live": True,
            }
            _cache[key] = {"data": result, "fetched_at": time.time()}
            logger.info("carbon_intensity_fetched", region="UK", actual=result["actual"])
            return result
    except Exception as e:
        logger.warning("carbon_intensity_fetch_failed", error=str(e))
        return _get_fallback()


async def get_carbon_intensity(region: str = "uk") -> dict:
    if region.lower() == "uk":
        return await get_carbon_intensity_uk()
    return _get_fallback()


def _get_fallback() -> dict:
    return {
        "region": "global_average",
        "actual": 475,
        "forecast": 475,
        "index": "moderate",
        "unit": "gCO2/kWh",
        "source": "fallback_average",
        "live": False,
    }
