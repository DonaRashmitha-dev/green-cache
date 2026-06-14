lines = open("src/api/routes.py", "r", encoding="utf-8").readlines()

for i, line in enumerate(lines):
    if "from src.preprocessing.normalizer" in line:
        lines[i] = line + "from src.preprocessing.quality_scorer import score_response, should_cache_response\n"
        break

for i, line in enumerate(lines):
    if "await cache.set(query=clean_query, response=response_text" in line:
        insert = (
            "    quality = score_response(clean_query, response_text)\n"
            "    logger.info('response_quality_scored', score=quality, will_cache=quality>=0.4)\n"
            "    if quality >= 0.4:\n"
            "        "
        )
        lines[i] = insert + line.lstrip()
        break

open("src/api/routes.py", "w", encoding="utf-8").writelines(lines)
print("Quality scorer wired!")
