import sqlite3
import json

# First, just check DB - what do our missing hadiths look like?
DB_PATH = r'assets\db\sahih_bukhari.db'
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

print("=== DB Missing hadiths (first 20) ===")
rows = c.execute('''
    SELECT h.id, h.hadith_number, h.chapter_id, ch.book_number, ch.title_urdu
    FROM hadiths h
    JOIN chapters ch ON h.chapter_id = ch.id
    WHERE (h.urdu_text IS NULL OR LENGTH(h.urdu_text) < 5)
    ORDER BY ch.book_number, CAST(h.hadith_number AS INTEGER)
    LIMIT 20
''').fetchall()

for row in rows:
    print(f"  id={row[0]}, hadith_num={repr(row[1])}, ch_id={row[2]}, book={row[3]}, chapter={row[4]}")

print("\n=== By Book ===")
book_rows = c.execute('''
    SELECT ch.book_number, COUNT(*) as cnt
    FROM hadiths h
    JOIN chapters ch ON h.chapter_id = ch.id
    WHERE (h.urdu_text IS NULL OR LENGTH(h.urdu_text) < 5)
    GROUP BY ch.book_number
    ORDER BY ch.book_number
''').fetchall()
for bk, cnt in book_rows:
    print(f"  Book {bk}: {cnt} missing")

# Also check a hadith that HAS urdu - what does its hadith_number look like?
print("\n=== Sample WITH Urdu ===")
with_urdu = c.execute('''
    SELECT h.id, h.hadith_number, ch.book_number
    FROM hadiths h
    JOIN chapters ch ON h.chapter_id = ch.id
    WHERE h.urdu_text IS NOT NULL AND LENGTH(h.urdu_text) > 5
    LIMIT 5
''').fetchall()
for row in with_urdu:
    print(f"  id={row[0]}, hadith_num={repr(row[1])}, book={row[2]}")

conn.close()
