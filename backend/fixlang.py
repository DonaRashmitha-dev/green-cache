lines = open("src/api/routes.py", "r", encoding="utf-8").readlines()
for i, line in enumerate(lines):
    if "Translate this to" in line:
        lines[i] = '    return "Translate the following text to " + lang_name + ". Write ONLY in " + lang_name + ". Do not use any other language:\\n\\n" + original_response\n'
        print(f"Fixed line {i+1}")
open("src/api/routes.py", "w", encoding="utf-8").writelines(lines)
