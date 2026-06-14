lines = open("src/api/routes.py", "r", encoding="utf-8").readlines()
for i, line in enumerate(lines):
    if "await cache.set(query=clean_query, response=response_text" in line:
        lines[i] = line.rstrip('\n').rstrip(')') + ", model_tag=model_tag)\n"
        break
open("src/api/routes.py", "w", encoding="utf-8").writelines(lines)
print("routes.py updated!")
