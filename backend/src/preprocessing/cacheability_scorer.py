"""Cacheability scorer — decides if a query is worth caching."""

import re

# Volatile patterns — queries about real-time data should NOT be cached long
_VOLATILE_PATTERNS = [
    r'\b(today|now|current|live|latest|right now|at the moment)\b',
    r'\b(price|stock|weather|score|news|breaking)\b',
    r'\b(what time|what date|how many days until)\b',
    r'\b(my|mine|I am|I have|my account|my order)\b',
]

# High cacheability — stable factual queries
_STABLE_PATTERNS = [
    r'\b(what is|how does|explain|define|what are|history of)\b',
    r'\b(capital|population|meaning|difference between)\b',
    r'\b(how to|steps to|tutorial|guide)\b',
]

_VOLATILE = [re.compile(p, re.IGNORECASE) for p in _VOLATILE_PATTERNS]
_STABLE = [re.compile(p, re.IGNORECASE) for p in _STABLE_PATTERNS]


def score(query: str) -> float:
    """
    Return cacheability score 0.0 - 1.0.
    < 0.3 = skip cache entirely
    0.3 - 0.7 = cache with short TTL
    > 0.7 = cache normally
    """
    volatile_hits = sum(1 for p in _VOLATILE if p.search(query))
    stable_hits = sum(1 for p in _STABLE if p.search(query))

    base = 0.5
    base -= volatile_hits * 0.2
    base += stable_hits * 0.15
    return max(0.0, min(1.0, base))


def should_cache(query: str, min_score: float = 0.3) -> bool:
    """Return True if query is worth caching."""
    return score(query) >= min_score


def get_ttl_seconds(query: str) -> int:
    """Return appropriate TTL based on query volatility."""
    s = score(query)
    if s < 0.3:
        return 0        # don't cache
    elif s < 0.5:
        return 300      # 5 minutes
    elif s < 0.7:
        return 3600     # 1 hour
    else:
        return 86400    # 24 hours
