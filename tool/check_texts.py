import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('assets/db/sahih_muslim.db')
cur = conn.cursor()

for num in ['225', '226', '255', '256']:
    cur.execute('SELECT arabic_text, english_text FROM hadiths WHERE TRIM(hadith_number) = ?', (num,))
    res = cur.fetchall()
    print(f'--- Hadith {num} ---')
    if res:
        print('Arabic:', res[0][0][:100])
        print('English:', res[0][1][:100])
