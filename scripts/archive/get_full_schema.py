import sqlite3
import os

db_path = r'c:\Users\tk854\Desktop\New folder\Shahih al-bukhari\shahihalbukhari\assets\db\sahih_bukhari.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get table list
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Tables: {tables}")

    for table_name in tables:
        print(f"\n--- Schema for {table_name} ---")
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        for col in columns:
            print(col)

        # Also get a sample row
        try:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 1;")
            row = cursor.fetchone()
            print(f"Sample row: {row}")
        except Exception as e:
            print(f"Could not get sample row: {e}")

    conn.close()
else:
    print(f"Database not found at {db_path}")
