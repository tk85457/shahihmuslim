import requests
import sqlite3
import time
import re

API_KEY = '$2y$10$ySRzfrqgvtpHTUHR6iZ2NC7gu9PPdyOBTjFf1wD0Dv6PpkhHy32'
DB_PATH = r'assets\db\sahih_bukhari.db'
LIMIT = 50

session = requests.Session()
session.verify = False
session.headers.update({'User-Agent': 'Mozilla/5.0'})
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_page(page, retries=3):
    url = f'https://hadithapi.com/api/hadiths/?apiKey={API_KEY}&book=sahih-bukhari&page={page}&limit={LIMIT}'
    for attempt in range(retries):
        try:
            resp = session.get(url, timeout=40)
            resp.raise_for_status()
            return resp.json().get('hadiths', {})
        except Exception as e:
            wait = 2 ** attempt
            print(f'  Retry {attempt+1}/{retries} page {page}: {e}')
            time.sleep(wait)
    return {}

# 1. Total Check
first = fetch_page(1)
last_page = first.get('last_page', 1)
print(f"Starting fetch... Total pages: {last_page}")

# 2. Setup DB mapping
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
missing_rows = c.execute("SELECT id, hadith_number FROM hadiths WHERE urdu_text IS NULL OR LENGTH(urdu_text) < 5").fetchall()

missing_map = {}
for row_id, hn in missing_rows:
    hn_str = str(hn).strip()
    missing_map[hn_str] = row_id
    try:
        missing_map[str(int(hn))] = row_id
    except:
        pass
print(f"Missing in DB: {len(missing_rows)}")

# 3. Fetch and Accumulate
updates = []
matched_ids = set()

for page in range(1, last_page + 1):
    resp = fetch_page(page)
    hadiths = resp.get('data', [])

    for h in hadiths:
        # API can return "299, 300, 301" or "299-301"
        raw_num = str(h.get('hadithNumber', '')).strip()
        urdu = (h.get('hadithUrdu') or '').strip()

        if len(urdu) < 5: continue

        # Split by comma or hyphen to handle groupings
        # Example "299, 300, 301" -> ["299", "300", "301"]
        parts = [p.strip() for p in raw_num.replace('-', ',').split(',') if p.strip()]

        for p in parts:
            if p in missing_map:
                db_id = missing_map[p]
                if db_id not in matched_ids:
                    updates.append((urdu, db_id))
                    matched_ids.add(db_id)

    if page % 10 == 0 or page == last_page:
        print(f"  Page {page}/{last_page} | Matched so far: {len(matched_ids)}/{len(missing_rows)}")

    time.sleep(0.2)

print(f"\nFound {len(updates)} matches to update.")

# 4. Update DB
if updates:
    c.executemany("UPDATE hadiths SET urdu_text=? WHERE id=?", updates)
    conn.commit()
    print("Database updated!")

# 5. Final Print
total_db = c.execute("SELECT count(*) FROM hadiths").fetchone()[0]
has_urdu = c.execute("SELECT count(*) FROM hadiths WHERE urdu_text IS NOT NULL AND LENGTH(urdu_text) > 5").fetchone()[0]
print(f"\nFinal: {has_urdu}/{total_db} ({has_urdu/total_db*100:.1f}%) have Urdu. Missing: {total_db - has_urdu}")
conn.close()
