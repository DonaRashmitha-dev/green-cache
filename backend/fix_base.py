lines = open("src/cache/base.py", "r", encoding="utf-8").readlines()

for i, line in enumerate(lines):
    if "tokens_generated: int = 0" in line and "CacheEntry" in "".join(lines[max(0,i-10):i]):
        lines[i] = line + "    model_tag: str = \"unknown\"\n"
        break

for i, line in enumerate(lines):
    if "tokens_generated: int = 0," in line and "async def set" in "".join(lines[max(0,i-10):i]):
        lines[i] = line + "        model_tag: str = \"unknown\",\n"
        break

open("src/cache/base.py", "w", encoding="utf-8").writelines(lines)
print("base.py updated!")
