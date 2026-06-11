import os
import re
from bs4 import BeautifulSoup

workspace_dir = r"c:\Users\skc\Desktop\Handcrafted-with-Love-Pure-Weaves-main"
index_path = os.path.join(workspace_dir, "index.html")
admin_path = os.path.join(workspace_dir, "admin.html")
login_path = os.path.join(workspace_dir, "login.html")
register_path = os.path.join(workspace_dir, "register.html")
app_path = os.path.join(workspace_dir, "app.py")

print("--- FILE SIZES ---")
for f in [index_path, admin_path, login_path, register_path, app_path]:
    if os.path.exists(f):
        print(f"{os.path.basename(f)}: {os.path.getsize(f) / 1024 / 1024:.2f} MB ({os.path.getsize(f)} bytes)")
    else:
        print(f"{os.path.basename(f)}: NOT FOUND")

# Let's inspect index.html
if os.path.exists(index_path):
    print("\n--- ANALYZING index.html ---")
    with open(index_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 1. Image count and base64 vs external
    imgs = soup.find_all('img')
    base64_imgs = 0
    external_imgs = 0
    missing_alt = 0
    empty_alt = 0
    for img in imgs:
        src = img.get('src', '')
        alt = img.get('alt', None)
        if src.startswith('data:'):
            base64_imgs += 1
        else:
            external_imgs += 1
        if alt is None:
            missing_alt += 1
        elif alt.strip() == '':
            empty_alt += 1
            
    print(f"Total img tags: {len(imgs)}")
    print(f"Base64 embedded images: {base64_imgs}")
    print(f"External/local file images: {external_imgs}")
    print(f"Images missing 'alt' attribute: {missing_alt}")
    print(f"Images with empty 'alt' attribute: {empty_alt}")
    
    # 2. Heading hierarchy
    headings: list[Any] = []  # type: ignore[unknown-name]
    for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        found = soup.find_all(tag)
        if found:
            headings.append((tag, len(found)))
            print(f"Total <{tag}>: {len(found)}")
            for h in found[:3]:
                print(f"  - {h.text.strip()}")
            if len(found) > 3:
                print(f"  - ... ({len(found) - 3} more)")

    # 3. Form fields check
    inputs = soup.find_all('input')
    buttons = soup.find_all('button')
    selects = soup.find_all('select')
    textareas = soup.find_all('textarea')
    print(f"\nForms elements:")
    print(f"  <input>: {len(inputs)}")
    print(f"  <button>: {len(buttons)}")
    print(f"  <select>: {len(selects)}")
    print(f"  <textarea>: {len(textareas)}")
    
    # Check labels associated with inputs
    def Any() -> None:
        pass
    inputs_without_labels: list[Any] = []
    for inp in inputs:
        inp_id = inp.get('id')
        inp_type = inp.get('type')
        if inp_type == 'hidden':
            continue
        if inp_id:
            label = soup.find('label', attrs={'for': inp_id})
            if not label:
                # also check parent
                parent_label = inp.find_parent('label')
                if not parent_label:
                    inputs_without_labels.append(inp_id)
        else:
            inputs_without_labels.append(f"No-ID ({inp.get('name', 'unnamed')})")
    print(f"Inputs without matching label 'for' or parent label: {len(inputs_without_labels)}")
    if inputs_without_labels:
        print(f"  Sample: {inputs_without_labels[:5]}")
        
    # 4. Search for JS scripts in index.html
    # Let's count scripts
    scripts = soup.find_all('script')
    print(f"\nTotal <script> tags: {len(scripts)}")
    for i, script in enumerate(scripts):
        src = script.get('src')
        stype = script.get('type')
        if src:
            print(f"  [{i}] External: {src}")
        else:
            print(f"  [{i}] Inline Script: type={stype}, length={len(script.text)} chars")
            # print first 100 chars
            snippet = script.text.strip()[:150].replace('\n', ' ')
            print(f"      Snippet: {snippet}...")

    # Find total size of inline styles and scripts
    styles = soup.find_all('style')
    print(f"\nTotal <style> tags: {len(styles)}")
    for i, style in enumerate(styles):
        print(f"  [{i}] Inline CSS: length={len(style.text)} chars")

# Let's search for coupon logic or product list in JS
with open(index_path, 'r', encoding='utf-8') as f:
    text = f.read()
    
# Let's look for coupon codes defined in JS using regex
coupons = re.findall(r'coupon[s]?\s*=\s*\[(.*?)\]', text, re.DOTALL | re.IGNORECASE)
if coupons:
    print("\n--- COUPONS FOUND IN JS ---")
    print(coupons[0][:500])
else:
    # let's look for coupon in text
    coupon_mentions = re.findall(r'(\bcoupon\b.*?)\n', text, re.IGNORECASE)[:10]
    print("\n--- COUPON MENTIONS ---")
    for m in coupon_mentions:
        print(" ", m.strip())

# Check admin.html
if os.path.exists(admin_path):
    print("\n--- ANALYZING admin.html ---")
    with open(admin_path, 'r', encoding='utf-8') as f:
        admin_text = f.read()
    admin_soup = BeautifulSoup(admin_text, 'html.parser')
    admin_scripts = admin_soup.find_all('script')
    print(f"Total <script> tags in admin.html: {len(admin_scripts)}")
    for i, script in enumerate(admin_scripts):
        src = script.get('src')
        if src:
            print(f"  [{i}] External: {src}")
        else:
            print(f"  [{i}] Inline Script: length={len(script.text)} chars")
            snippet = script.text.strip()[:150].replace('\n', ' ')
            print(f"      Snippet: {snippet}...")
            
    # Check if there is authentication or password verification on admin.html
    auth_check = re.findall(r'(password|login|auth|sessionStorage|localStorage|jwt)', admin_text, re.IGNORECASE)
    print(f"Authentication keyword count in admin.html: {len(auth_check)}")

# Check app.py routes
if os.path.exists(app_path):
    print("\n--- ANALYZING app.py ---")
    with open(app_path, 'r', encoding='utf-8') as f:
        app_text = f.read()
    routes = re.findall(r'@app\.route\((.*?)\)', app_text)
    print(f"Total routes: {len(routes)}")
    for r in routes:
        print(f"  Route: {r}")
