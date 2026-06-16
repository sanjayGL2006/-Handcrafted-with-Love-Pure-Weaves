"""
seed_all_to_app_db.py
---------------------
Migrates ALL products from pureweaves.db (old schema) into app.db (Flask blueprint schema).
This ensures all 72+ products appear in the catalog page.

Usage:
    python seed_all_to_app_db.py
"""

import sqlite3
import os
import io
import sys
import random

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PW_DB = os.path.join(BASE_DIR, 'instance', 'pureweaves.db')
APP_DB = os.path.join(BASE_DIR, 'instance', 'app.db')

print(f"Source DB: {PW_DB} (exists: {os.path.exists(PW_DB)})")
print(f"Target DB: {APP_DB} (exists: {os.path.exists(APP_DB)})")

if not os.path.exists(PW_DB):
    print("ERROR: pureweaves.db not found. Run seed_all_products.py first.")
    sys.exit(1)

# ── Step 1: Read all products from pureweaves.db ──
print("\n[1/3] Reading products from pureweaves.db ...")
pw_conn = sqlite3.connect(PW_DB)
pw_cur = pw_conn.cursor()
pw_cur.execute("SELECT id, name, category, description, price, image_path, is_active, stock FROM products")
pw_products = pw_cur.fetchall()
pw_conn.close()
print(f"    Found {len(pw_products)} products")

# Collect unique categories from source
categories_set = set()
for p in pw_products:
    categories_set.add(p[2])  # category column
print(f"    Categories: {sorted(categories_set)}")

# ── Step 2: Connect to app.db and ensure tables exist ──
print("\n[2/3] Setting up app.db ...")
app_conn = sqlite3.connect(APP_DB)
app_cur = app_conn.cursor()

# Create categories table if not exists
app_cur.execute("""
CREATE TABLE IF NOT EXISTS categories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
)
""")

# Create products table if not exists (matching Flask model schema)
app_cur.execute("""
CREATE TABLE IF NOT EXISTS products (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        VARCHAR(200) NOT NULL,
    category_id INTEGER REFERENCES categories(id),
    description TEXT NOT NULL,
    price       REAL NOT NULL,
    image_path  VARCHAR(500),
    is_active   BOOLEAN DEFAULT 1,
    stock       INTEGER DEFAULT 100,
    rating      REAL DEFAULT 0.0,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
app_conn.commit()

# ── Step 3: Insert categories ──
cat_map: dict[str, Any] = {}  # type: ignore[unknown-name]
for cat_name in sorted(categories_set):
    app_cur.execute("SELECT id FROM categories WHERE name = ?", (cat_name,))
    row = app_cur.fetchone()
    if row:
        cat_map[cat_name] = row[0]
    else:
        app_cur.execute("INSERT INTO categories (name, description) VALUES (?, ?)", 
                       (cat_name, f"Handcrafted {cat_name} designs by Pure Weaves"))
        cat_map[cat_name] = app_cur.lastrowid
        print(f"    [NEW CAT] {cat_name} -> id {cat_map[cat_name]}")
app_conn.commit()

# ── Step 4: Insert/update products ──
print("\n[3/3] Inserting products into app.db ...")
added = 0
updated = 0

for p in pw_products:
    pw_id, name, category, description, price, image_path, is_active, stock = p
    category_id = cat_map.get(category)
    
    if not category_id:
        print(f"    [SKIP] {name} - category '{category}' not found")
        continue
    
    # Fix image path if needed (ensure it starts with /static/)
    if image_path and image_path.startswith('/app/'):
        image_path = image_path.replace('/app/', '/')
    
    # Generate a reasonable rating
    rating = round(random.uniform(3.5, 5.0), 1)
    
    # Check if product already exists by name
    app_cur.execute("SELECT id FROM products WHERE name = ?", (name,))
    existing = app_cur.fetchone()
    
    if existing:
        app_cur.execute("""
            UPDATE products SET category_id=?, description=?, price=?, image_path=?, 
            is_active=?, stock=?, rating=? WHERE id=?
        """, (category_id, description, price, image_path, is_active or 1, stock or 100, rating, existing[0]))
        updated += 1
    else:
        app_cur.execute("""
            INSERT INTO products (name, category_id, description, price, image_path, is_active, stock, rating)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, category_id, description, price, image_path, 1, stock or 100, rating))
        added += 1
        
app_conn.commit()

# ── Summary ──
app_cur.execute("SELECT COUNT(*) FROM products")
total = app_cur.fetchone()[0]
app_cur.execute("SELECT COUNT(*) FROM categories")
total_cats = app_cur.fetchone()[0]

print(f"\n{'='*50}")
print(f"  Added   : {added} new products")
print(f"  Updated : {updated} existing products")
print(f"  Total   : {total} products in app.db")
print(f"  Cats    : {total_cats} categories")
print(f"{'='*50}")

# Show final data
print("\nCategories in app.db:")
app_cur.execute("SELECT id, name FROM categories ORDER BY id")
for r in app_cur.fetchall():
    app_cur.execute("SELECT COUNT(*) FROM products WHERE category_id = ?", (r[0],))
    count = app_cur.fetchone()[0]
    print(f"  [{r[0]}] {r[1]} ({count} products)")

app_conn.close()
print("\nDone! Restart Flask app (python run.py) to see all products.")
