import json
import os

log_path = r"C:\Users\skc\.gemini\antigravity-ide\brain\edb0c628-7577-413a-adf0-8f3b3d36c7da\.system_generated\logs\transcript.jsonl"
if not os.path.exists(log_path):
    print("Log file not found at", log_path)
    exit(1)

with open(log_path, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        if data.get('type') == 'USER_INPUT':
            content = data.get('content', '')
            if 'Bug Report' in content or '18' in content:
                # Write to scratch/user_input.md
                with open('scratch/user_input.md', 'w', encoding='utf-8') as out:
                    out.write(content)
                print("Wrote complete user input to scratch/user_input.md")
                break
