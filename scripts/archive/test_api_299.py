import requests
import json
import sqlite3
import urllib3

urllib3.disable_warnings()
API_KEY = '$2y$10$ySRzfrqgvtpHTUHR6iZ2NC7gu9PPdyOBTjFf1wD0Dv6PpkhHy32'
DB_PATH = r'assets\db\sahih_bukhari.db'

with open('debug_output.txt', 'w', encoding='utf-8') as f:
    url = f'https://hadithapi.com/api/hadiths/?apiKey={API_KEY}&book=sahih-bukhari&hadithNumber=299'
    r = requests.get(url, verify=False)
    data = r.json()

    if 'hadiths' in data and data['hadiths']['data']:
        h = data['hadiths']['data'][0]
        num = str(h.get('hadithNumber')).strip()
        f.write(f"API returned: hadithNumber={repr(num)}\n")
        f.write(f"API urdu: {repr((h.get('hadithUrdu') or '')[:50])}\n")
    else:
        f.write(f"API returned no hadiths for 299: {list(data.keys())}\n")

    conn = sqlite3.connect(DB_PATH)
    missing = [str(r[0]).strip() for r in conn.execute("SELECT hadith_number FROM hadiths WHERE urdu_text IS NULL OR LENGTH(urdu_text) < 5 LIMIT 10").fetchall()]
    f.write(f"First 10 missing in DB: {missing}\n")

    if num in missing:
        f.write("MATCH SHOULD WORK!\n")
    else:
        f.write(f"Mismatch: API returned {repr(num)}, DB has {missing}\n")
