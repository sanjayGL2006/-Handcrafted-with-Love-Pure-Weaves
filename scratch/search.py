import os

with open('index.html', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        if 'reviews' in line.lower() and ('id=' in line or 'class=' in line or 'list' in line):
            print(f"{i}: {line.strip()[:120]}")
