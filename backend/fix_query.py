lines = open("src/api/routes.py", "r", encoding="utf-8").readlines()
for i, line in enumerate(lines):
    if "detected_language = request.language or detect_language(request.query)" in line:
        lines[i] = line.replace("detect_language(request.query)", "detect_language(clean_query)")
    if 'logger.info("language_detected", query=request.query' in line:
        lines[i] = line.replace("query=request.query", "query=clean_query")
    if "embedding = embedder.embed(request.query)" in line:
        lines[i] = line.replace("request.query", "clean_query")
    if "cache_result = await cache.get(" in line:
        pass
    if "request.query, embedding, quality_tier" in line:
        lines[i] = line.replace("request.query,", "clean_query,")
open("src/api/routes.py", "w", encoding="utf-8").writelines(lines)
print("Fixed! clean_query now used everywhere.")
