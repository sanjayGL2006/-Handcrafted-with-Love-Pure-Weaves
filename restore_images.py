#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
restore_images.py
-----------------
Extracts all product images (embedded as base64 in index.html) and:
1. Saves them as JPEG files in app/static/images/
2. Updates the SQLite database 'image_path' field for each matching product

Usage:
    python restore_images.py
"""

import re
import os
import base64
import sys
import io

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ── Config ──────────────────────────────────────────────────────
INDEX_HTML    = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html')
IMAGES_DIR    = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static', 'images')
DB_PATH       = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'pureweaves.db')

# ── Step 1: Parse product designs from index.html ───────────────
print("[1/3] Reading index.html ...")
with open(INDEX_HTML, 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

products_found = []
for line in html.splitlines():
    line = line.strip()
    if not line.startswith('{ "id":'):
        continue
    m = re.search(
        r'"id":\s*(\d+).*?"name":\s*"([^"]+)".*?"img":\s*"data:image/([a-z]+);base64,([A-Za-z0-9+/=]+)"',
        line
    )
    if m:
        prod_id   = int(m.group(1))
        prod_name = m.group(2)
        img_type  = m.group(3)   # jpeg/png/webp
        b64_data  = m.group(4)
        products_found.append((prod_id, prod_name, img_type, b64_data))

print(f"    Found {len(products_found)} products with embedded images.")

# ── Step 2: Save images to disk ─────────────────────────────────
print(f"[2/3] Saving images to {IMAGES_DIR} ...")
os.makedirs(IMAGES_DIR, exist_ok=True)

saved = []
errors = 0
for prod_id, prod_name, img_type, b64_data in products_found:
    ext = 'jpg' if img_type in ('jpeg', 'jpg') else img_type
    filename  = f"product_{prod_id}.{ext}"
    filepath  = os.path.join(IMAGES_DIR, filename)
    url_path  = f"/app/static/images/{filename}"

    try:
        img_bytes = base64.b64decode(b64_data)
        with open(filepath, 'wb') as f:
            f.write(img_bytes)
        saved.append((prod_id, prod_name, url_path))
        print(f"    [OK] Saved: {filename}  ({prod_name})")
    except Exception as e:
        print(f"    [ERR] Failed {filename}: {e}")
        errors += 1

print(f"    Saved {len(saved)} image files. Errors: {errors}")

# ── Step 3: Update database ──────────────────────────────────────
if not os.path.exists(DB_PATH):
    print(f"\n[3/3] WARNING: Database not found at {DB_PATH}")
    print("      Skipping DB update - images were saved to disk.")
    print("\nDone! To update DB, run the Flask app first so it creates the DB,")
    print("then run this script again.")
    sys.exit(0)

try:
    import sqlite3
    print(f"\n[3/3] Updating database at {DB_PATH} ...")
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    # Check what columns exist
    cur.execute("PRAGMA table_info(products)")
    cols = [row[1] for row in cur.fetchall()]
    if 'image_path' not in cols:
        print("    WARNING: Column 'image_path' not found in products table.")
        conn.close()
        sys.exit(1)

    updated = 0
    not_found = []
    for prod_id, prod_name, url_path in saved:
        # Try matching by name first
        cur.execute("SELECT id FROM products WHERE name = ?", (prod_name,))
        row = cur.fetchone()
        if row:
            cur.execute("UPDATE products SET image_path = ? WHERE id = ?", (url_path, row[0]))
            print(f"    [OK] Updated: '{prod_name}' -> {url_path}")
            updated += 1
        else:
            # Fallback: try by id
            cur.execute("SELECT id FROM products WHERE id = ?", (prod_id,))
            row = cur.fetchone()
            if row:
                cur.execute("UPDATE products SET image_path = ? WHERE id = ?", (url_path, prod_id))
                print(f"    [OK] Updated by id {prod_id}: {url_path}")
                updated += 1
            else:
                not_found.append(prod_name)

    conn.commit()
    conn.close()

    print(f"\n    Updated {updated} product image paths in database.")
    if not_found:
        print(f"    WARNING: {len(not_found)} products not found in DB (may not be seeded yet):")
        for n in not_found:
            print(f"       - {n}")

except Exception as e:
    print(f"    ERROR: Database update failed: {e}")
    print("      Images were still saved to disk successfully.")
    sys.exit(1)

print("\nImage restore complete!")
print(f"   Images folder : {IMAGES_DIR}")
print(f"   Files saved   : {len(saved)}")
print(f"   DB records    : {updated}")
print("\nNext steps:")
print("  1. Start the Flask backend: python app.py")
print("  2. Open admin.html - product images should now display.")
