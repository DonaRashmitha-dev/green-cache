"""PII scrubber — strips personal data before cache lookup."""

import re

# Patterns to detect and redact
_PATTERNS = [
    (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]'),
    (r'\b(?:\+?\d{1,3}[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b', '[PHONE]'),
    (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]'),
    (r'\b4[0-9]{12}(?:[0-9]{3})?\b', '[CARD]'),
    (r'\b5[1-5][0-9]{14}\b', '[CARD]'),
    (r'\b(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b', '[IP]'),
    (r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', '[NAME]'),
    (r'\b\d{1,5}\s+\w+\s+(?:St|Ave|Rd|Blvd|Dr|Ln|Way|Court|Ct|Place|Pl)\b', '[ADDRESS]'),
]

_COMPILED = [(re.compile(p), r) for p, r in _PATTERNS]


def scrub(text: str) -> tuple[str, bool]:
    """
    Scrub PII from text.
    Returns (scrubbed_text, was_modified).
    """
    modified = False
    result = text
    for pattern, replacement in _COMPILED:
        new = pattern.sub(replacement, result)
        if new != result:
            modified = True
            result = new
    return result, modified


def is_safe_to_cache(text: str) -> bool:
    """Return False if text contains PII that should not be cached."""
    scrubbed, modified = scrub(text)
    return not modified
