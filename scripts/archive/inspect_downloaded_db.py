import sqlite3

db_path = r'C:\Users\tk854\Desktop\New folder\Shahih al-bukhari\shahihalbukhari\temp_data\albukhari.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# List tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", tables)

for table in tables:
    table_name = table[0]
    print(f"\n--- Columns in {table_name} ---")
    cursor.execute(f"PRAGMA table_info({table_name});")
    print(cursor.fetchall())

    print(f"\n--- Sample data from {table_name} (first 2 rows) ---")
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 2;")
    print(cursor.fetchall())

conn.close()
