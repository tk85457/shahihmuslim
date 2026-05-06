import sqlite3
import json

db_path = r'C:\Users\tk854\Desktop\New folder\Shahih al-bukhari\shahihalbukhari\assets\db\sahih_bukhari.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT id, book_number, title_english, hadith_count FROM chapters LIMIT 10")
chapters = cursor.fetchall()

print("Chapters schema: id, book_number, title_english, hadith_count")
for c in chapters:
    print(c)

conn.close()

# Also check the highest book number in the JSON to ensure it matches
file_path = r'C:\Users\tk854\Music\Downloads\urd-bukhari.min.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

max_book = 0
for h in data['hadiths']:
    book = h['reference']['book']
    if book > max_book:
        max_book = book

print(f"Max book in JSON: {max_book}")
