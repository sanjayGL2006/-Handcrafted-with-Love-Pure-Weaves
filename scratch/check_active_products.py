import sqlite3

db_path = r"c:\Users\skc\Desktop\Handcrafted-with-Love-Pure-Weaves-main\instance\pureweaves.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Get column names of products
cur.execute("PRAGMA table_info(products);")
cols = cur.fetchall()
print("Columns of products:", [c[1] for c in cols])

# Count active products
try:
    cur.execute("SELECT is_active, COUNT(*) FROM products GROUP BY is_active;")
    print("Products counts by is_active:", cur.fetchall())
except Exception as e:
    print("Error:", e)

# Count is_active null or whatever
cur.execute("SELECT COUNT(*) FROM products;")
total = cur.fetchone()[0]
print("Total count:", total)

conn.close()
