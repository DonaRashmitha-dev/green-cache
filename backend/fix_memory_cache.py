lines = open("src/cache/memory_cache.py", "r", encoding="utf-8").readlines()

for i, line in enumerate(lines):
    if "tokens_generated: int = 0," in line and i > 150:
        lines[i] = line + "        model_tag: str = \"unknown\",\n"
        break

for i, line in enumerate(lines):
    if "CacheEntry(" in line:
        if "model_tag" not in "".join(lines[i:i+10]):
            for j in range(i, i+10):
                if "tokens_generated=tokens_generated" in lines[j]:
                    lines[j] = lines[j].rstrip('\n') + "\n            model_tag=model_tag,\n"
                    break
        break

open("src/cache/memory_cache.py", "w", encoding="utf-8").writelines(lines)
print("memory_cache.py updated!")
