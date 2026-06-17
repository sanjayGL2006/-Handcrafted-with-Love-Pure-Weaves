import sqlite3
import os

db_path = 'instance/pureweaves.db'
if os.path.exists(db_path):
    print(f"=== Tables in {db_path} ===")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cur.fetchall()]
    for t in tables:
        cur.execute(f"PRAGMA table_info({t})")
        columns = [c[1] for c in cur.fetchall()]
        print(f"Table: {t} -> Columns: {columns}")
    conn.close()
else:
    print(f"{db_path} does not exist")

db_path2 = 'instance/app.db'
if os.path.exists(db_path2):
    print(f"\n=== Tables in {db_path2} ===")
    conn = sqlite3.connect(db_path2)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cur.fetchall()]
    for t in tables:
        cur.execute(f"PRAGMA table_info({t})")
        columns = [c[1] for c in cur.fetchall()]
        print(f"Table: {t} -> Columns: {columns}")
    conn.close()
else:
    print(f"\n{db_path2} does not exist")
