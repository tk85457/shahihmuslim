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

# Map hadithnumber to texts - Keep as string to preserve decimals
hadiths_map = {}
for i, h in enumerate(ara_data):
    n = str(h['hadithnumber'])
    # Assign a unique ID based on index since hadith_number is no longer a unique integer primary key
    hadiths_map[i] = {
        'num': n,
        'arabic': h['text'],
        'book': int(h['reference']['book']),
        'english': '',
        'urdu': ''
    }

# Mapping by hadithnumber (string) for merging
num_to_index = {data['num']: idx for idx, data in hadiths_map.items()}

for h in urd_data:
    n = str(h['hadithnumber'])
    if n in num_to_index:
        idx = num_to_index[n]
        hadiths_map[idx]['urdu'] = h['text']

for h in eng_data:
    n = str(h['hadithnumber'])
    if n in num_to_index:
        idx = num_to_index[n]
        hadiths_map[idx]['english'] = h['text']

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

for i in sorted(hadiths_map.keys()):
    h_data = hadiths_map[i]
    h_num = h_data['num']
    book_num = h_data['book']
    chapter_id = book_to_chapter_id.get(book_num)

    if chapter_id is None:
        chapter_id = book_to_chapter_id.get(1)

    # Note: id is incremental PK, hadith_number is the string identifying number
    cursor.execute('''
        INSERT INTO hadiths (id, chapter_id, hadith_number, arabic_text, urdu_text, english_text)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (i + 1, int(chapter_id), str(h_num), str(h_data['arabic']), str(h_data['urdu']), str(h_data['english'])))
    insert_count += 1

conn.commit()
conn.close()

print(f"Successfully inserted {insert_count} hadiths!")
