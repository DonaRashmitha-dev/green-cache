lines = open("src/api/routes.py", "r", encoding="utf-8").readlines()
new_endpoint = '\n@router.get("/carbon")\nasync def get_carbon() -> dict:\n    from src.metrics.carbon_intensity import get_carbon_intensity\n    return await get_carbon_intensity("uk")\n\n'
for i, line in enumerate(lines):
    if '@router.get("/health")' in line:
        lines.insert(i, new_endpoint)
        break
open("src/api/routes.py", "w", encoding="utf-8").writelines(lines)
print("Carbon endpoint added!")
