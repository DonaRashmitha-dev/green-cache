lines = open("src/api/routes.py", "r", encoding="utf-8").readlines()
for i, line in enumerate(lines):
    if "await cache.set(query=request.query, response=translated_response" in line:
        lines[i] = line.replace("query=request.query,", "query=clean_query,")
    if "await cache.set(query=request.query, response=response_text" in line:
        lines[i] = line.replace("query=request.query,", "query=clean_query,")
open("src/api/routes.py", "w", encoding="utf-8").writelines(lines)
print("Fixed!")
