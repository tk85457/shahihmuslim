import sqlite3
import os

base_dir = r'C:\Users\tk854\Desktop\New folder\Shahih al-bukhari\shahihalbukhari'
db_path = os.path.join(base_dir, 'assets', 'db', 'sahih_bukhari.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Fetching existing database records...")
cursor.execute("SELECT id, book_number, title_arabic, title_urdu, title_english, hadith_count FROM chapters LIMIT 5")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
