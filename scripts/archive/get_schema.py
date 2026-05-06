import sqlite3
import os

db_path = r'c:\Users\tk854\Desktop\New folder\Shahih al-bukhari\shahihalbukhari\assets\db\sahih_bukhari.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables:", tables)
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name});")
        info = cursor.fetchall()
        print(f"\nSchema for {table_name}:")
        for col in info:
            print(col)
    conn.close()
else:
    print(f"Database not found at {db_path}")
