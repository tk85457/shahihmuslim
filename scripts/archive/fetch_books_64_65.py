import sqlite3
import json
import urllib.request
import time

DB_PATH = r'assets\db\sahih_bukhari.db'
OUTPUT_FILE = r'ajax_urdu_books_64_65.json'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://sunnah.com/bukhari',
}

def fetch_book(book_num):
    url = f'https://sunnah.com/ajax/urdutranslation/{book_num}'
    print(f'  Fetching Book {book_num} from: {url}')
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            # data is a list of hadith objects
            if isinstance(data, list):
                print(f'  -> Got {len(data)} hadiths')
                return data
            else:
                print(f'  -> Unexpected format: {type(data)}')
                return []
    except Exception as e:
        print(f'  -> Error: {e}')
        return []

# Try fetching Books 64 and 65
all_data = {}
for book_num in [64, 65]:
    print(f'\nFetching Book {book_num}...')
    hadiths = fetch_book(book_num)
    if hadiths:
        all_data[str(book_num)] = hadiths
    time.sleep(3)

if not all_data:
    print('\nNo data fetched. Trying alternate endpoint format...')
    # Try alternate approach - bukhari:{book}
    for book_num in [64, 65]:
        url = f'https://sunnah.com/ajax/urdutranslation/bukhari/{book_num}'
        print(f'  Trying: {url}')
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                if isinstance(data, list) and data:
                    all_data[str(book_num)] = data
                    print(f'  -> Got {len(data)} hadiths')
        except Exception as e:
            print(f'  -> Error: {e}')
        time.sleep(3)

# Save what we got
if all_data:
    json.dump(all_data, open(OUTPUT_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f'\nSaved to {OUTPUT_FILE}')

    # Now integrate into DB
    print('\nIntegrating into database...')
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    updates = []
    for book_num_str, hadiths in all_data.items():
        book_num = int(book_num_str)
        # Get chapter IDs for this book
        chapter_ids = [r[0] for r in c.execute(
            'SELECT id FROM chapters WHERE book_number=?', (book_num,)).fetchall()]
        print(f'  Book {book_num}: {len(chapter_ids)} chapters, {len(hadiths)} hadiths from JSON')

        for h in hadiths:
            hadith_num = str(h.get('hadithNumber', h.get('hadith_number', '')))
            urdu_text = h.get('urduText', h.get('urdu_text', h.get('body', '')))
            if urdu_text and hadith_num:
                updates.append((urdu_text, hadith_num))

    if updates:
        c.executemany(
            'UPDATE hadiths SET urdu_text=? WHERE hadith_number=? AND (urdu_text IS NULL OR LENGTH(urdu_text) < 5)',
            updates
        )
        conn.commit()
        print(f'  Updated {c.rowcount} rows')
    conn.close()
else:
    print('\nNo data fetched. Books 64 & 65 may require a different approach.')
    # Show what hadiths are missing
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    missing = c.execute('''
        SELECT h.id, h.hadith_number, ch.book_number, ch.title_urdu
        FROM hadiths h
        JOIN chapters ch ON h.chapter_id = ch.id
        WHERE (h.urdu_text IS NULL OR LENGTH(h.urdu_text) < 5)
        ORDER BY ch.book_number, h.hadith_number
        LIMIT 20
    ''').fetchall()
    print('\nFirst 20 missing hadiths:')
    for row in missing:
        print(f'  ID={row[0]}, HadithNum={row[1]}, Book={row[2]}, Chapter={row[3]}')

    total = c.execute('''SELECT COUNT(*) FROM hadiths WHERE urdu_text IS NULL OR LENGTH(urdu_text) < 5''').fetchone()[0]
    print(f'\nTotal still missing: {total}')
    conn.close()
