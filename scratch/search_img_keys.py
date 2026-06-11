with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
matches = re.finditer(r'\b(img|image|image_path)\b', content)
found = {}
for m in matches:
    start_pos = m.start()
    line_no = content[:start_pos].count('\n') + 1
    word = m.group(0)
    line = content[start_pos-30:start_pos+50].strip().replace('\n', ' ')
    if line_no >= 2325: # only in JS part
        print(f"Line {line_no}: ... {line} ...")
