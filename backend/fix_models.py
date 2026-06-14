lines = open("src/api/models.py", "r", encoding="utf-8").readlines()
for i, line in enumerate(lines):
    if "system_prompt: Optional[str] = Field(" in line:
        lines.insert(i, '    user_id: Optional[str] = Field(default="anonymous", description="User identifier for passport tracking")\n')
        break
open("src/api/models.py", "w", encoding="utf-8").writelines(lines)
print("user_id added!")
