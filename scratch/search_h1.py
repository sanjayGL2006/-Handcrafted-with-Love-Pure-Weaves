with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
matches = re.finditer(r'<h1\b', content)
for m in matches:
    start_pos = m.start()
    line_no = content[:start_pos].count('\n') + 1
    # Print the line and its tag content
    print(f"Line {line_no}: {content[start_pos:start_pos+100].strip().replace('\n', ' ')}")
