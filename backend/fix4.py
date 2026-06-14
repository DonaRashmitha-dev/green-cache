lines = open("src/api/routes.py", "r", encoding="utf-8").readlines()
lines[88] = '    return "Translate this to " + lang_name + " language only. No other language allowed:\\n\\n" + original_response\n'
open("src/api/routes.py", "w", encoding="utf-8").writelines(lines)
print("Fixed!")
