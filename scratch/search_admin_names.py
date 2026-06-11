with open('admin.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
names = ["Blue Silk Jewelry Set", "Purple Crystal Blouse Border", "Red Crystal Blouse Border", "Blue Silk Necklace Set", "Purple Pearl Wave Kuchu"]
for name in names:
    matches = re.finditer(re.escape(name), content)
    for m in matches:
        start_pos = m.start()
        line_no = content[:start_pos].count('\n') + 1
        print(f"admin.html Line {line_no}: {content[start_pos-30:start_pos+70].strip().replace('\n', ' ')}")
