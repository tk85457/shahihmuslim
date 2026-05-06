import sqlite3

db_path = r'C:\Users\tk854\Desktop\New folder\Shahih al-bukhari\shahihalbukhari\temp_data\albukhari.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(ahadith);")
columns = cursor.fetchall()
print("Columns in 'ahadith':")
for col in columns:
    print(col)

# Also check for any other tables that might have translation
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("\nAll tables:", tables)

conn.close()
