import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Let's search for function definitions inside the script
functions = re.findall(r'function\s+(\w+)\s*\(', html)
print("Functions found in index.html:")
for f_name in set(functions):
    # find where they are defined (first match)
    pos = html.find(f"function {f_name}")
    if pos != -1:
        line_no = html[:pos].count('\n') + 1
        print(f"  - {f_name} at line {line_no}")
    else:
        pos = html.find(f"function  {f_name}")
        if pos != -1:
            line_no = html[:pos].count('\n') + 1
            print(f"  - {f_name} at line {line_no}")

# Also check for key variables or elements in HTML
for item in ['productDetailsModal', 'productDetailModal', 'privacyModal', 'faq-content', 'reviews-list']:
    pos = html.find(item)
    if pos != -1:
        line_no = html[:pos].count('\n') + 1
        print(f"Found element/class '{item}' at line {line_no}")
