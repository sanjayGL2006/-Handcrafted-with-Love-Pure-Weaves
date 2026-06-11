with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx in range(2320, 2400):
    if idx <= len(lines):
        line = lines[idx-1]
        if len(line) > 100:
            print(f"{idx}: {line[:100]}... [length {len(line)}]")
        else:
            print(f"{idx}: {line}", end='')
