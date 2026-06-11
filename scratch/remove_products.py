import sys, re

targets_to_remove = [
    'Blue Silk Jewelry Set',
    'Purple Crystal Blouse Border',
    'Red Crystal Blouse Border',
    'Blue Silk Necklace Set',
    'Purple Pearl Wave Kuchu'
]

with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f'Total lines: {len(lines)}')

new_lines: list[Any] = []  # type: ignore[unknown-name]
skip_count = 0

for i, line in enumerate(lines):
    line_num = i + 1
    
    # Check if this line is a product data entry for one of the targets
    is_data_line = False
    for target in targets_to_remove:
        if f'"name": "{target}"' in line:
            is_data_line = True
            print(f'Removing data line {line_num}: {target}')
            break
    
    if is_data_line:
        skip_count += 1
        continue
    
    # Check if this is a REMOVED_NAMES or REMOVED_DESIGNS filter line containing target names
    is_filter_line = False
    for target in targets_to_remove:
        if f'"{target}"' in line:
            # Check it's not in a data entry (data entries have "name": before them)
            # Filter lines are simple array entries like: "Purple Pearl Wave Kuchu",
            stripped = line.strip()
            if stripped.startswith(f'"{target}"') or stripped.startswith(f', "{target}"'):
                is_filter_line = True
                print(f'Removing filter line {line_num}: {target}')
                break
    
    if is_filter_line:
        skip_count += 1
        continue
    
    new_lines.append(line)

print(f'Removed {skip_count} lines')
print(f'New total: {len(new_lines)} lines')

# Fix any trailing comma issues in arrays after removal
# Find the REMOVED_NAMES array and clean up trailing commas
result_content = ''.join(new_lines)

# Fix the misplaced comma issue from previous: "Blue Silk Jewelry Set"\n        ,
# Now the array may have a line like: "Purple Gold Tiny Kuchu"\n        ,\n if next item was removed
# Actually since we removed those lines, we just need the remaining array to be valid

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(result_content)

print('Done! index.html updated.')
