import sqlite3
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\tk854\Downloads\muslim.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

hadiths = data['hadiths']
json_numbers = set()
for h in hadiths:
    json_numbers.add(str(h['idInBook']).strip())
    json_numbers.add(str(h['id']).strip()) # sometimes id is the global number

conn = sqlite3.connect('assets/db/sahih_muslim.db')
cur = conn.cursor()
cur.execute('SELECT hadith_number FROM hadiths')
db_numbers = {str(n[0]).strip() for n in cur.fetchall()}

missing_in_db = set()
# Let's assume idInBook map to hadith_number
for h in hadiths:
    num = str(h['idInBook']).strip()
    if num not in db_numbers:
        missing_in_db.add(num)

print(f"Missing idInBook in DB: {len(missing_in_db)}")
if missing_in_db:
    print(list(missing_in_db)[:20])

missing_id = set()
for h in hadiths:
    num = str(h['id']).strip()
    if num not in db_numbers:
        missing_id.add(num)
        
print(f"Missing global id in DB: {len(missing_id)}")
if missing_id:
    print(list(missing_id)[:20])
