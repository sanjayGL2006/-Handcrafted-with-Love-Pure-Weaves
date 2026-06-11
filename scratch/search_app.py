with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines, 1):
    if '/api/products' in line or 'def get_products' in line:
        print(f"Line {idx}: {line.strip()}")
        # print next 20 lines
        for j in range(idx, min(idx+25, len(lines))):
            print(f"  {j+1}: {lines[j]}", end='')
