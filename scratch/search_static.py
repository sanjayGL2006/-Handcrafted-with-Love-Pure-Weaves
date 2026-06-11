with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re
matches = re.finditer(r'send_from_directory|static', content)
for m in matches:
    start_pos = m.start()
    line_no = content[:start_pos].count('\n') + 1
    print(f"Line {line_no}: {content[max(0, start_pos-50):min(len(content), start_pos+100)].strip().replace('\n', ' ')}")
