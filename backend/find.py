lines = open("src/api/routes.py", "r", encoding="utf-8").readlines()
for i, line in enumerate(lines):
    if "cache_result = await cache.get(" in line:
        print(f"{i+1}: {line}", end="")
open("src/api/routes.py", "r").close()
