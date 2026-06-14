lines = open("src/api/routes.py", "r", encoding="utf-8").readlines()
new_imports = (
    "from src.preprocessing.pii_scrubber import scrub, is_safe_to_cache\n"
    "from src.preprocessing.cacheability_scorer import should_cache, get_ttl_seconds, score as cache_score\n"
    "from src.preprocessing.normalizer import normalize, normalize_for_cache_key\n"
)
for i, line in enumerate(lines):
    if "from src.api.models" in line:
        lines.insert(i, new_imports)
        break
open("src/api/routes.py", "w", encoding="utf-8").writelines(lines)
print("Imports added!")
