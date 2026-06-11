import sys, re

sys.stdout.reconfigure(encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.splitlines()

targets = [
    'Blue Silk Jewelry Set',
    'Purple Crystal Blouse Border',
    'Red Crystal Blouse Border',
    'Blue Silk Necklace Set',
    'Purple Pearl Wave Kuchu'
]

print('=== Checking for remaining target product names ===')
for i, line in enumerate(lines, 1):
    for t in targets:
        if t in line:
            print(f'Line {i}: {line.strip()[:100]}')

print()
print('=== REMOVED_NAMES array (context) ===')
idx = content.find('REMOVED_NAMES')
if idx >= 0:
    print(content[idx:idx+300])

print()
print('=== REMOVED_DESIGNS array (context) ===')
idx2 = content.find('REMOVED_DESIGNS')
if idx2 >= 0:
    print(content[idx2:idx2+300])

print()
print('=== Checking for orphaned commas (lines that are just commas) ===')
for i, line in enumerate(lines, 1):
    stripped = line.strip()
    if stripped == ',':
        print(f'Line {i}: orphaned comma found')
