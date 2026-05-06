import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('assets/db/sahih_muslim.db')
cur = conn.cursor()

# 1. Add columns if not exist
try:
    cur.execute('ALTER TABLE hadiths ADD COLUMN is_primary INTEGER DEFAULT 1')
    cur.execute('ALTER TABLE hadiths ADD COLUMN primary_hadith_id INTEGER DEFAULT NULL')
    print("Columns added successfully.")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("Columns already exist, proceeding with update.")
    else:
        raise

# Heuristic keywords
chain_keywords_english = [
    'like the hadith of',
    'like the hadith reported',
    'with this chain',
    'with the same chain',
    'has been transmitted',
    'has been narrated',
    'narrated like',
    'transmitted by',
    'the same hadith',
    'This hadith has been reported',
    'This hadith has been transmitted',
]

chain_keywords_arabic = [
    'بمثل حديث',
    'بمثله',
    'بِهَذَا',
    'عَنْ هَذَا',
    'مِثْلَهُ',
    'نَحْوَهُ'
]

# 2. Iterate and mark
cur.execute('SELECT id, chapter_id, english_text, arabic_text FROM hadiths ORDER BY id ASC')
all_hadiths = cur.fetchall()

last_primary_id = None
updates = []

for h in all_hadiths:
    hid = h[0]
    chapter_id = h[1]
    eng = h[2].lower()
    arb = h[3]
    
    is_primary = 1
    
    word_count = len(eng.split())
    
    if word_count < 40 and word_count > 0:
        for kw in chain_keywords_english:
            if kw.lower() in eng:
                is_primary = 0
                break
                
    if is_primary == 1 and word_count == 0:
        # Fallback to arabic check if english text is missing temporarily
        arb_word_count = len(arb.split())
        if arb_word_count < 30:
            for kw in chain_keywords_arabic:
                if kw in arb:
                    is_primary = 0
                    break

    if is_primary == 1:
        last_primary_id = hid
    
    primary_ref = last_primary_id if is_primary == 0 else None
    updates.append((is_primary, primary_ref, hid))

# 3. Apply updates
cur.executemany('''
    UPDATE hadiths 
    SET is_primary = ?, primary_hadith_id = ? 
    WHERE id = ?
''', updates)

conn.commit()
print(f"Migration complete. Handled {len(all_hadiths)} hadiths.")

cur.execute('SELECT COUNT(*) FROM hadiths WHERE is_primary = 0')
print(f"Total secondary chain-only narrations marked: {cur.fetchone()[0]}")

conn.close()
