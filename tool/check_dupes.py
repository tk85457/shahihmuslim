import sqlite3
import sys

# Windows console encoding fix
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('assets/db/sahih_muslim.db')
cur = conn.cursor()

for num in ['225', '226', '255', '256', '256a', '256b']:
    cur.execute('SELECT id, chapter_id, hadith_number, arabic_text FROM hadiths WHERE TRIM(hadith_number) = ?', (num,))
    res = cur.fetchall()
    if res:
        for r in res:
            print(f'Match for {num}: id={r[0]}, {r[2]}')
            
cur.execute('SELECT hadith_number, arabic_text FROM hadiths WHERE arabic_text LIKE "%بمثل حديث%" LIMIT 5')
for r in cur.fetchall():
    print(f'Chain-only example: {r[0]} | {r[1][:50]}')
