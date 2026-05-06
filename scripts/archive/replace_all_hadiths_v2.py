import sqlite3
import json
import os

db_path = r'C:\Users\tk854\Desktop\New folder\Shahih al-bukhari\shahihalbukhari\assets\db\sahih_bukhari.db'
ara_path = r'C:\Users\tk854\Music\Downloads\ara-bukhari.min.json'
urd_path = r'C:\Users\tk854\Music\Downloads\urd-bukhari.min.json'
eng_path = r'C:\Users\tk854\Music\Downloads\eng-bukhari.min.json'

def load_data(path):
    print(f"Loading {path}...")
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)['hadiths']

ara_data = load_data(ara_path)
urd_data = load_data(urd_path)
eng_data = load_data(eng_path)

print(f"Loaded {len(ara_data)} Arabic, {len(urd_data)} Urdu, {len(eng_data)} English hadiths.")

hadiths_map = {}
for h in ara_data:
    n = int(h['hadithnumber'])
    hadiths_map[n] = {'arabic': h['text'], 'book': int(h['reference']['book']), 'english': '', 'urdu': ''}

for h in urd_data:
    n = int(h['hadithnumber'])
    if n in hadiths_map:
        hadiths_map[n]['urdu'] = h['text']

for h in eng_data:
    n = int(h['hadithnumber'])
    if n in hadiths_map:
        hadiths_map[n]['english'] = h['text']

# DB Connection
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT id, book_number FROM chapters")
chapter_rows = cursor.fetchall()
book_to_chapter_id = {int(row[1]): int(row[0]) for row in chapter_rows}

print("Deleting existing hadiths...")
cursor.execute("DELETE FROM hadiths")

print("Inserting new hadiths...")
insert_count = 0
errors = 0

for h_num in sorted(hadiths_map.keys()):
    h_data = hadiths_map[h_num]
    book_num = h_data['book']
    chapter_id = book_to_chapter_id.get(book_num)

    if chapter_id is None:
        chapter_id = book_to_chapter_id.get(1)

    try:
        cursor.execute('''
            INSERT INTO hadiths (id, chapter_id, hadith_number, arabic_text, urdu_text, english_text)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (int(h_num), int(chapter_id), int(h_num), str(h_data['arabic']), str(h_data['urdu']), str(h_data['english'])))
        insert_count += 1
    except Exception as e:
        if errors < 5:
            print(f"Error inserting hadith {h_num}: {e}")
            print(f"Values: id={h_num}({type(h_num)}), chapter_id={chapter_id}({type(chapter_id)}), arabic_len={len(h_data['arabic'])}")
        errors += 1

conn.commit()
conn.close()

print(f"Successfully inserted {insert_count} hadiths!")
if errors > 0:
    print(f"Encountered {errors} errors during insertion.")
