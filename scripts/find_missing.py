import json
import sqlite3
import sys
import os
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Paths
JSON_PATH = r'C:\Users\tk854\Downloads\muslim.json'
DB_PATH = r'C:\Users\tk854\Desktop\app\shahihmuslim\assets\db\sahih_muslim.db'

# Load JSON
with open(JSON_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

json_hadiths = data['hadiths']
print(f"JSON file has {len(json_hadiths)} hadiths")
print(f"Sample keys: {list(json_hadiths[0].keys())}")

# Check english structure
h0 = json_hadiths[0]
eng = h0.get('english','')
if isinstance(eng, dict):
    print(f"english is dict with keys: {list(eng.keys())}")
elif isinstance(eng, list):
    print(f"english is list, len={len(eng)}")
else:
    print(f"english is {type(eng).__name__}")

print(f"id={h0.get('id')}, idInBook={h0.get('idInBook')}, chapterId={h0.get('chapterId')}, bookId={h0.get('bookId')}")

# Collect JSON hadith numbers
json_numbers_idb = set()
json_numbers_id = set()
for h in json_hadiths:
    json_numbers_idb.add(str(h.get('idInBook', '')))
    json_numbers_id.add(str(h.get('id', '')))

print(f"\nJSON unique idInBook values: {len(json_numbers_idb)}")
print(f"JSON unique id values: {len(json_numbers_id)}")

# Connect to DB
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM hadiths")
db_count = cur.fetchone()[0]
print(f"\nDB has {db_count} hadiths")

cur.execute("SELECT COUNT(*) FROM chapters")
print(f"DB has {cur.fetchone()[0]} chapters")

# Get all hadith numbers from DB
cur.execute("SELECT TRIM(hadith_number) FROM hadiths")
db_numbers = set(row[0] for row in cur.fetchall())
print(f"DB unique hadith numbers: {len(db_numbers)}")

# Number ranges
db_numeric = sorted([int(x) for x in db_numbers if x.isdigit()])
json_id_nums = sorted([h.get('id',0) for h in json_hadiths if isinstance(h.get('id'),int)])
json_idb_nums = sorted([h.get('idInBook',0) for h in json_hadiths if isinstance(h.get('idInBook'),int)])

if db_numeric:
    print(f"\nDB number range: {db_numeric[0]} to {db_numeric[-1]}")
if json_id_nums:
    print(f"JSON id range: {json_id_nums[0]} to {json_id_nums[-1]}")
if json_idb_nums:
    print(f"JSON idInBook range: {json_idb_nums[0]} to {json_idb_nums[-1]}")

# Find missing: JSON hadiths where idInBook NOT in DB
missing = []
for h in json_hadiths:
    num = str(h.get('idInBook', ''))
    if num and num not in db_numbers:
        missing.append(h)

print(f"\nMissing hadiths (JSON idInBook not in DB): {len(missing)}")

# Also try by global id
missing_by_id = []
for h in json_hadiths:
    num = str(h.get('id', ''))
    if num and num not in db_numbers:
        missing_by_id.append(h)
print(f"Missing hadiths (JSON id not in DB): {len(missing_by_id)}")

# Show first 15 missing
if missing:
    print(f"\nFirst 15 missing hadiths (by idInBook):")
    for h in missing[:15]:
        print(f"  id={h.get('id')} idInBook={h.get('idInBook')} chapterId={h.get('chapterId')} bookId={h.get('bookId')}")

# Check which DB has but JSON doesn't
extra_in_db = db_numbers - json_numbers_idb - json_numbers_id
print(f"\nDB numbers NOT in JSON at all: {len(extra_in_db)}")
if extra_in_db:
    sample = sorted(list(extra_in_db)[:20], key=lambda x: int(x) if x.isdigit() else 0)
    print(f"  Sample: {sample}")

# Check the bookId/chapterId structure in JSON
book_ids = set(h.get('bookId') for h in json_hadiths)
chapter_ids = set(h.get('chapterId') for h in json_hadiths)
print(f"\nJSON bookId values: {sorted(book_ids)[:20]}... (total: {len(book_ids)})")
print(f"JSON chapterId range: {min(chapter_ids)} to {max(chapter_ids)} (total: {len(chapter_ids)})")

# Check DB chapter structure
cur.execute("SELECT DISTINCT book_number FROM chapters ORDER BY book_number")
db_books = [r[0] for r in cur.fetchall()]
print(f"\nDB book_number values: {db_books[:20]}... (total: {len(db_books)})")

conn.close()
