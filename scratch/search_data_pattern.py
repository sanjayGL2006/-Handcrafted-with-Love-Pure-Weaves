with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
matches = re.finditer(r'data:', content)
for m in matches:
    start_pos = m.start()
    line_no = content[:start_pos].count('\n') + 1
    # Only print if it's inside script tags or around line 2500-3300
    if 2440 <= line_no <= 3400:
        print(f"Line {line_no}: {content[start_pos-50:start_pos+100].strip().replace('\n', ' ')}")
