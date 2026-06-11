with open('admin.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
patterns = [r'Blue Silk', r'Blouse Border', r'Wave Kuchu']
for pat in patterns:
    matches = re.finditer(pat, content)
    for m in matches:
        start_pos = m.start()
        line_no = content[:start_pos].count('\n') + 1
        print(f"admin.html Line {line_no}: {content[start_pos-30:start_pos+70].strip().replace('\n', ' ')}")
