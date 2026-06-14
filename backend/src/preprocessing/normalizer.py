"""Language + codemix normalizer."""

import re
import unicodedata


def normalize(text: str) -> str:
    text = unicodedata.normalize('NFC', text)
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'[!?]{2,}', '?', text)
    text = re.sub(r'\.{2,}', '.', text)
    return text


def normalize_for_cache_key(text: str) -> str:
    return normalize(text).lower()
