lines = open("src/api/routes.py", "r", encoding="utf-8").readlines()

for i, line in enumerate(lines):
    if "cache_hit=True, cross_language_hit=False," in line or "cache_hit=True, cross_language_hit=False" in line:
        for j in range(i-1, max(0,i-5), -1):
            if "return QueryResponse(" in lines[j]:
                lines.insert(j, '        passport.record(request.user_id or "anonymous", cache_hit=True, tokens_saved=cache_result.tokens_saved, water_saved_ml=savings.get("water_saved_ml",0), energy_saved_wh=savings.get("energy_saved_wh",0), carbon_saved_g=savings.get("carbon_saved_g",0))\n')
                break
        break

for i, line in enumerate(lines):
    if "cache_hit=False, cross_language_hit=False," in line:
        for j in range(i-1, max(0,i-5), -1):
            if "return QueryResponse(" in lines[j]:
                lines.insert(j, '    passport.record(request.user_id or "anonymous", cache_hit=False)\n')
                break
        break

open("src/api/routes.py", "w", encoding="utf-8").writelines(lines)
print("Passport record calls added!")
