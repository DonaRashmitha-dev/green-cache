lines = open("src/api/routes.py", "r", encoding="utf-8").readlines()
for i, line in enumerate(lines):
    if "request.query, system_prompt=request.system_prompt" in line:
        lines[i] = line.replace("request.query,", "clean_query,")
open("src/api/routes.py", "w", encoding="utf-8").writelines(lines)
print("LLM now uses clean_query!")
