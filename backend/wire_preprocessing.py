lines = open("src/api/routes.py", "r", encoding="utf-8").readlines()
for i, line in enumerate(lines):
    if "detected_language = request.language or detect_language" in line:
        insert = (
            "    clean_query, pii_found = scrub(request.query)\n"
            "    if pii_found:\n"
            "        logger.info('pii_detected_and_scrubbed', original=request.query[:30])\n"
            "    cacheable = should_cache(clean_query)\n"
            "    ttl = get_ttl_seconds(clean_query)\n"
            "    c_score = cache_score(clean_query)\n"
            "    logger.info('cacheability_scored', score=round(c_score,2), ttl=ttl, cacheable=cacheable)\n"
            "    clean_query = normalize(clean_query)\n"
        )
        lines.insert(i, insert)
        break
open("src/api/routes.py", "w", encoding="utf-8").writelines(lines)
print("Preprocessing wired!")
