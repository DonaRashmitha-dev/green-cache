"""Cross-model tag — tracks which LLM model generated each cache entry."""


def make_model_tag(provider: str, model: str) -> str:
    """Create a standardized model tag string."""
    return f"{provider}:{model}"


def parse_model_tag(tag: str) -> tuple[str, str]:
    """Parse model tag into (provider, model)."""
    if ":" in tag:
        parts = tag.split(":", 1)
        return parts[0], parts[1]
    return "unknown", tag
