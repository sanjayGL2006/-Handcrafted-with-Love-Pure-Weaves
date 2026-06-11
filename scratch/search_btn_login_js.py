with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
matches = re.finditer(r'btn-login', content)
for m in matches:
    start_pos = m.start()
    line_no = content[:start_pos].count('\n') + 1
    if line_no >= 2325:
        print(f"Line {line_no}: {content[start_pos-30:start_pos+70].strip().replace('\n', ' ')}")
