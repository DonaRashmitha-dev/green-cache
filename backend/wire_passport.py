lines = open("src/api/routes.py", "r", encoding="utf-8").readlines()
for i, line in enumerate(lines):
    if "from src.preprocessing.model_tagger" in line:
        lines[i] = line + "from src.preprocessing.user_passport import get_passport\n"
        break
for i, line in enumerate(lines):
    if "impact_calc = get_impact_calculator()" in line:
        lines[i] = line + "    passport = get_passport()\n"
        break
open("src/api/routes.py", "w", encoding="utf-8").writelines(lines)
print("Passport wired!")
