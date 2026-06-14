"""Answer quality scorer — scores LLM responses before caching."""

import re


def score_response(query: str, response: str) -> float:
    if not response or not response.strip():
        return 0.0

    s = 0.5
    words = len(response.split())
    if words < 10:
        s -= 0.4
    elif words < 30:
        s -= 0.2
    elif words > 50:
        s += 0.1
    elif words > 100:
        s += 0.2

    refusal_patterns = [
        r"i (can't|cannot|won't|will not|am not able to)",
        r"i('m| am) sorry",
        r"i don't (know|have|understand)",
        r"as an ai",
        r"i need more (information|context|details)",
        r"please (clarify|provide|specify)",
        r"i('m| am) unable to",
    ]
    for p in refusal_patterns:
        if re.search(p, response.lower()):
            s -= 0.25
            break

    quality_patterns = [
        r'\b(because|therefore|however|furthermore|additionally)\b',
        r'\b(first|second|third|finally)\b',
        r'\d+',
    ]
    for p in quality_patterns:
        if re.search(p, response.lower()):
            s += 0.05

    sentences = [x.strip() for x in response.split('.') if x.strip()]
    if len(sentences) > 2:
        unique = len(set(sentences))
        if unique / len(sentences) < 0.7:
            s -= 0.2

    return max(0.0, min(1.0, round(s, 2)))


def should_cache_response(query: str, response: str, min_score: float = 0.4) -> bool:
    return score_response(query, response) >= min_score
