lines = open("src/api/routes.py", "r", encoding="utf-8").readlines()

for i, line in enumerate(lines):
    if "from src.preprocessing.quality_scorer" in line:
        lines[i] = line + "from src.preprocessing.model_tagger import make_model_tag\n"
        break

for i, line in enumerate(lines):
    if "llm_client = get_llm_client()" in line:
        lines[i] = line + "    model_tag = make_model_tag(llm_client.provider, llm_client.model)\n"
        break

open("src/api/routes.py", "w", encoding="utf-8").writelines(lines)
print("Model tag wired!")
