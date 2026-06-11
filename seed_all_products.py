#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
seed_all_products.py
--------------------
Seeds ALL 72 products from index.html into the database with their images.
Uses direct SQLite access (no Flask dependency needed).

Usage:
    python seed_all_products.py
"""

import re
import os
import sys
import io
import base64
import sqlite3
import datetime

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ── Config ──────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
INDEX_HTML = os.path.join(BASE_DIR, 'index.html')
IMAGES_DIR = os.path.join(BASE_DIR, 'app', 'static', 'images')
DB_PATH    = os.path.join(BASE_DIR, 'instance', 'pureweaves.db')

# ── Parse products from index.html ──────────────────────────────
print("[1/3] Reading products from index.html ...")
with open(INDEX_HTML, 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

products_data = []
for line in html.splitlines():
    line = line.strip()
    if not line.startswith('{ "id":'):
        continue
    m = re.search(
        r'"id":\s*(\d+).*?"name":\s*"([^"]+)".*?"category":\s*"([^"]+)".*?"desc":\s*"([^"]*)".*?"price":\s*"[^0-9]*([0-9]+)".*?"img":\s*"data:image/([a-z]+);base64,([A-Za-z0-9+/=]+)"',
        line
    )
    if m:
        products_data.append({
            'id'      : int(m.group(1)),
            'name'    : m.group(2),
            'category': m.group(3),
            'desc'    : m.group(4),
            'price'   : float(m.group(5)),
            'img_type': m.group(6),
            'b64'     : m.group(7),
        })

print(f"    Found {len(products_data)} products.")

# ── Save images to disk ──────────────────────────────────────────
print(f"[2/3] Saving images to {IMAGES_DIR} ...")
os.makedirs(IMAGES_DIR, exist_ok=True)

for p in products_data:
    ext = 'jpg' if p['img_type'] in ('jpeg', 'jpg') else p['img_type']
    filename = f"product_{p['id']}.{ext}"
    filepath = os.path.join(IMAGES_DIR, filename)
    p['image_path'] = f"/app/static/images/{filename}"
    try:
        img_bytes = base64.b64decode(p['b64'])
        with open(filepath, 'wb') as f:
            f.write(img_bytes)
    except Exception as e:
        print(f"    [ERR] Image {filename}: {e}")

print(f"    Saved {len(products_data)} images.")

# ── Seed database via direct SQLite ─────────────────────────────
print(f"[3/3] Seeding database at {DB_PATH} ...")

if not os.path.exists(DB_PATH):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    print(f"    Creating new database...")

conn = sqlite3.connect(DB_PATH)
cur  = conn.cursor()

# Create products table if not exists (mirrors the Flask model)
cur.execute("""
CREATE TABLE IF NOT EXISTS products (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    code        TEXT    UNIQUE,
    category    TEXT    NOT NULL,
    description TEXT    NOT NULL,
    price_min   REAL    NOT NULL,
    price_max   REAL    NOT NULL,
    price       REAL,
    image_path  TEXT,
    is_active   INTEGER DEFAULT 1,
    stock       INTEGER DEFAULT 100,
    quantity    INTEGER DEFAULT 100,
    created_at  TEXT    DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

added   = 0
updated = 0
now     = datetime.datetime.utcnow().isoformat()

for p in products_data:
    name      = p['name']
    code      = f"PW{p['id']:04d}"
    category  = p['category']
    desc      = p['desc'] or f"Handcrafted {category} design by Pure Weaves, Shivamogga."
    price     = p['price']
    img_path  = p['image_path']

    cur.execute("SELECT id FROM products WHERE name = ?", (name,))
    row = cur.fetchone()

    if row:
        cur.execute(
            "UPDATE products SET image_path = ?, category = ?, description = ?, price_min = ?, price_max = ?, price = ?, is_active = 1 WHERE id = ?",
            (img_path, category, desc, price, price + 100, price, row[0])
        )
        print(f"    [UPDATE] {name}")
        updated += 1
    else:
        cur.execute(
            "INSERT INTO products (name, code, category, description, price_min, price_max, price, image_path, is_active, stock, quantity, created_at) VALUES (?,?,?,?,?,?,?,?,1,100,100,?)",
            (name, code, category, desc, price, price + 100, price, img_path, now)
        )
        print(f"    [ADD]    {name}")
        added += 1

conn.commit()

cur.execute("SELECT COUNT(*) FROM products")
total = cur.fetchone()[0]
conn.close()

print(f"\n    Added   : {added} new products")
print(f"    Updated : {updated} existing products")
print(f"    Total   : {total} products in database")

print("\n=== Image Restore Complete! ===")
print(f"  Images saved  : {len(products_data)} files in app/static/images/")
print(f"  DB updated    : {total} products total")
print("\nNext steps:")
print("  1. Start Flask backend : python app.py")
print("  2. Open admin.html -> Products -> all images now visible!")
