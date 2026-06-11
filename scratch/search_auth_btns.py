with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
matches = re.finditer(r'(?i)login|logout', content)
for m in matches:
    start_pos = m.start()
    line_no = content[:start_pos].count('\n') + 1
    # Only print markup lines
    if line_no < 2325 and ('button' in content[start_pos-30:start_pos+70] or 'btn' in content[start_pos-30:start_pos+70] or 'nav' in content[start_pos-30:start_pos+70]):
        print(f"Line {line_no}: {content[start_pos-40:start_pos+80].strip().replace('\n', ' ')}")
