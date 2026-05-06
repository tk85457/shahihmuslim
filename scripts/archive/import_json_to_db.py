import sqlite3
import json
import os
import re

base_dir = r'C:\Users\tk854\Desktop\New folder\Shahih al-bukhari\shahihalbukhari'
ara_path = os.path.join(base_dir, 'ara-bukhari.json')
urd_path = os.path.join(base_dir, 'urd-bukhari.json')
db_path = os.path.join(base_dir, 'assets', 'db', 'sahih_bukhari.db')

def update_db():
    print("Loading JSON datasets...")
    with open(ara_path, 'r', encoding='utf-8') as f:
        ara_data = json.load(f)['hadiths']

    with open(urd_path, 'r', encoding='utf-8') as f:
        urd_data = json.load(f)['hadiths']

    print(f"Loaded {len(ara_data)} Arabic and {len(urd_data)} Urdu hadiths.")

    # Create dicts for easy lookup by hadith number
    ara_dict = {h['hadithnumber']: h['text'] for h in ara_data}
    urd_dict = {h['hadithnumber']: h['text'] for h in urd_data}

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Fetching existing database records...")
    cursor.execute("SELECT id, hadith_number FROM hadiths")
    rows = cursor.fetchall()

    print(f"Database contains {len(rows)} hadith records.")

    updated_count = 0
    missing_count = 0

    for row in rows:
        db_id = row[0]
        hadith_number = row[1]

        # The app DB has a hadith_number column whichmaps to hadithnumber in Sahih Bukhari
        ara_text = ara_dict.get(hadith_number)
        urd_text = urd_dict.get(hadith_number)

        if ara_text and urd_text:
            if not isinstance(urd_text, str):
                urd_text = " ".join(urd_text) if isinstance(urd_text, list) else str(urd_text)

            if not isinstance(ara_text, str):
                ara_text = " ".join(ara_text) if isinstance(ara_text, list) else str(ara_text)

            cursor.execute('''
                UPDATE hadiths
                SET arabic_text = ?, urdu_text = ?
                WHERE id = ?
            ''', (ara_text.strip(), urd_text.strip(), db_id))
            updated_count += 1

            if updated_count <= 2:
                print(f"--- Sample Update for DB ID {db_id} (Hadith {hadith_number}) ---")
                print(f"URD: {urd_text.strip()[:100]}...")

        else:
            missing_count += 1
            if missing_count <= 10:
                print(f"Missing mapping for DB ID {db_id}, Hadith {hadith_number}")

    conn.commit()
    conn.close()
    print(f"\nUpdate Complete! Updated {updated_count} hadiths. Missing mapping for {missing_count} hadiths.")

if __name__ == "__main__":
    update_db()
