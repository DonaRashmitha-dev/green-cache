content = open("src/api/routes.py", "r", encoding="utf-8").read()
lines = content.split("\n")
new_lines = []
skip_next = False
for i, line in enumerate(lines):
    if skip_next:
        skip_next = False
        continue
    if line.strip().startswith('return "Translate to " + lang_name') and not line.strip().endswith('original_response'):
        new_lines.append('    return "Translate to " + lang_name + ". Output only the translation. " + original_response')
        skip_next = True
    else:
        new_lines.append(line)
open("src/api/routes.py", "w", encoding="utf-8").write("\n".join(new_lines))
print("Fixed!")
