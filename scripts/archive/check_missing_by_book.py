import sqlite3
import json
import urllib.request
import time

DB_PATH = r'assets\db\sahih_bukhari.db'

# Step 1: Check which books have missing Urdu
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

print("=== Missing Urdu by Book ===")
rows = c.execute('''
    SELECT h.book_number, COUNT(*) as missing
    FROM hadiths h
    JOIN chapters ch ON h.chapter_id = ch.id
    WHERE (h.urdu_text IS NULL OR LENGTH(h.urdu_text) < 5)
    GROUP BY h.book_number
    ORDER BY h.book_number
''').fetchall()

for book_num, missing in rows:
    print(f"  Book {book_num}: {missing} missing")

total_missing = sum(r[1] for r in rows)
print(f"\nTotal missing: {total_missing}")
conn.close()
