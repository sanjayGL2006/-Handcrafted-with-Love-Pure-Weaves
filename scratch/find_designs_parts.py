with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
matches = re.finditer(r'DESIGNS_PART\d+|REMOVED_NAMES', content)
for m in matches:
    start_pos = m.start()
    line_no = content[:start_pos].count('\n') + 1
    print(f"Line {line_no}: {m.group(0)}")
