import sqlite3
import os

base_dir = r'C:\Users\tk854\Desktop\New folder\Shahih al-bukhari\shahihalbukhari'
db_path = os.path.join(base_dir, 'assets', 'db', 'sahih_bukhari.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get skipped hadiths
cursor.execute("SELECT id, hadith_number, urdu_text FROM hadiths WHERE hadith_number = 0 LIMIT 10;")
rows = cursor.fetchall()

print("Showing missing Urdu titles in hadiths table where hadith_number is 0:")
for row in rows:
    print(row)

conn.close()
