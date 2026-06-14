import sys
sys.path.insert(0, "src")

routes_content = open("src/api/routes.py", "r", encoding="utf-8").read()

# Find line 89 area and show it
lines = routes_content.split("\n")
for i, line in enumerate(lines[85:95], start=86):
    print(f"{i}: {line}")
