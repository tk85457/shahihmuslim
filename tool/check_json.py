import sqlite3
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Open the new JSON file
try:
    with open(r'C:\Users\tk854\Downloads\muslim.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
except Exception as e:
    print(f"Error opening json: {e}")
    sys.exit(1)

# Check structure of json
print(f"Keys in JSON: {list(data.keys())[:10]}")
if isinstance(data, list):
    print(f"Total list items: {len(data)}")
    if len(data) > 0:
        print(f"First item: {data[0].keys()}")
elif 'hadiths' in data:
    hadithsList = data['hadiths']
    print(f"Total hadiths inside 'hadiths' key: {len(hadithsList)}")
    if len(hadithsList) > 0:
        print(f"First item: {hadithsList[0].keys()}")

conn = sqlite3.connect('assets/db/sahih_muslim.db')
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM hadiths')
db_count = cur.fetchone()[0]
print(f"Current DB Hadiths Count: {db_count}")

# Check missing by mapping global numbers
cur.execute('SELECT hadith_number FROM hadiths')
db_numbers = {str(n[0]).strip() for n in cur.fetchall()}

# We need to adapt this depending on what structure the JSON actually has.
