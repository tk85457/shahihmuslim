import sqlite3
import json

db_path = r'C:\Users\tk854\Desktop\New folder\Shahih al-bukhari\shahihalbukhari\assets\db\sahih_bukhari.db'
ara_path = r'C:\Users\tk854\Music\Downloads\ara-bukhari.min.json'
urd_path = r'C:\Users\tk854\Music\Downloads\urd-bukhari.min.json'
eng_path = r'C:\Users\tk854\Music\Downloads\eng-bukhari.min.json'

print("Loading JSON files...")
with open(ara_path, 'r', encoding='utf-8') as f:
    ara_data = json.load(f)['hadiths']
with open(urd_path, 'r', encoding='utf-8') as f:
    urd_data = json.load(f)['hadiths']
with open(eng_path, 'r', encoding='utf-8') as f:
    eng_data = json.load(f)['hadiths']

print(f"Loaded {len(ara_data)} Arabic, {len(urd_data)} Urdu, {len(eng_data)} English hadiths.")

# Map hadithnumber to texts
hadiths_map = {}
for h in ara_data:
    n = h['hadithnumber']
    hadiths_map[n] = {'arabic': h['text'], 'book': h['reference']['book'], 'english': '', 'urdu': ''}

for h in urd_data:
    n = h['hadithnumber']
    if n in hadiths_map:
        hadiths_map[n]['urdu'] = h['text']

for h in eng_data:
    n = h['hadithnumber']
    if n in hadiths_map:
        hadiths_map[n]['english'] = h['text']

# DB Connection
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get chapter book_number to id mapping
cursor.execute("SELECT id, book_number FROM chapters")
chapter_rows = cursor.fetchall()
book_to_chapter_id = {row[1]: row[0] for row in chapter_rows}

print("Deleting existing hadiths...")
cursor.execute("DELETE FROM hadiths")

print("Inserting new hadiths...")
insert_count = 0
for h_num in sorted(hadiths_map.keys()):
    h_data = hadiths_map[h_num]
    book_num = h_data['book']
    chapter_id = book_to_chapter_id.get(book_num)

    if chapter_id is None:
        # Fallback to book 1 if not found, though we checked up to 97 exists
        chapter_id = book_to_chapter_id.get(1)

    cursor.execute('''
        INSERT INTO hadiths (id, chapter_id, hadith_number, arabic_text, urdu_text, english_text)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (h_num, chapter_id, h_num, h_data['arabic'], h_data['urdu'], h_data['english']))

    insert_count += 1

conn.commit()
conn.close()

print(f"Successfully inserted {insert_count} hadiths!")
