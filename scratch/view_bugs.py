import re

with open('scratch/user_input.md', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace base64 data patterns to make it clean
clean_text = re.sub(r'data:image/[^;]+;base64,[A-Za-z0-9+/=\s\n\r]+', 'data:image/...[base64]...', text)

with open('scratch/user_input_clean.md', 'w', encoding='utf-8') as f:
    f.write(clean_text)

print("Cleaned file written to scratch/user_input_clean.md")
