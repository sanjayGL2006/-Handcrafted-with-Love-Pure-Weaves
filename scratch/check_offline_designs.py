with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
# Find first { "id": 1, ... } or similar
m = re.search(r'const DESIGNS_PART1 = \[\s*(\{.*?\})', content, re.DOTALL)
if m:
    print("DESIGNS_PART1 first item:", m.group(1)[:500])
else:
    print("Not found")
