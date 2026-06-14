import re

with open("src/api/routes.py", "r", encoding="utf-8") as f:
    content = f.read()

new_func = (
    "def translate_prompt(original_response: str, target_language: str) -> str:\n"
    "    lang_names = {\n"
    '        "zh": "Simplified Chinese",\n'
    '        "ja": "Japanese",\n'
    '        "es": "Spanish",\n'
    '        "ko": "Korean",\n'
    '        "en": "English",\n'
    '        "hi": "Hindi",\n'
    '        "te": "Telugu",\n'
    '        "fr": "French",\n'
    '        "de": "German",\n'
    "    }\n"
    "    lang_name = lang_names.get(target_language, target_language)\n"
    '    return "Translate to " + lang_name + ". Output only the translation.\\n\\n" + original_response\n'
)

content = re.sub(r"def translate_prompt.*?(?=\n\n@router|\ndef )", new_func + "\n\n", content, flags=re.DOTALL)

with open("src/api/routes.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed!")
