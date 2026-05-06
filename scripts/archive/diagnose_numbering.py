import ssl
import urllib.request
import json
import sqlite3

API_KEY = '$2y$10$ySRzfrqgvtpHTUHR6iZ2NC7gu9PPdyOBTjFf1wD0Dv6PpkhHy32'
DB_PATH = r'assets\db\sahih_bukhari.db'

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

# Check API format - what does hadithNumber look like?
url = f'https://hadithapi.com/api/hadiths/?apiKey={API_KEY}&book=sahih-bukhari&page=1&limit=5'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=30, context=ssl_ctx) as resp:
    data = json.loads(resp.read().decode('utf-8'))

hadiths = data['hadiths']['data']
print("=== API Sample (first 5) ===")
for h in hadiths:
    print(f"  hadithNumber={repr(h.get('hadithNumber'))}, chapterNo={repr(h.get('chapterNumber'))}, bookSlug={repr(h.get('bookSlug'))}")
    print(f"  urduText (first 50)={repr((h.get('hadithUrdu') or '')[:50])}")

# Check DB format
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
print("\n=== DB Missing hadiths (first 5) ===")
rows = c.execute('''
    SELECT h.id, h.hadith_number, h.chapter_id, ch.book_number
    FROM hadiths h
    JOIN chapters ch ON h.chapter_id = ch.id
    WHERE (h.urdu_text IS NULL OR LENGTH(h.urdu_text) < 5)
    LIMIT 5
''').fetchall()
for row in rows:
    print(f"  db_id={row[0]}, hadith_number={repr(row[1])}, chapter_id={row[2]}, book_number={row[3]}")

conn.close()
