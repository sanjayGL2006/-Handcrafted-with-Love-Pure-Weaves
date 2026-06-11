import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's find all function definitions that have -> None: and their line numbers
lines = content.split('\n')
for idx, line in enumerate(lines, 1):
    if 'def ' in line and '-> None:' in line:
        print(f"Line {idx}: {line.strip()}")
