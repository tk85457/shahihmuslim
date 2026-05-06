import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('assets/db/sahih_muslim.db')
cur = conn.cursor()

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
]

chain_keywords_arabic = [
    'بمثل حديث',
    'بمثله',
    'بِهَذَا',
    'عَنْ هَذَا',
    'مِثْلَهُ',
    'نَحْوَهُ'
]

cur.execute('SELECT id, hadith_number, english_text FROM hadiths')
all_hadiths = cur.fetchall()

secondary_count = 0
for h in all_hadiths:
    text = h[2].lower()
    
    is_secondary = False
    
    # Check if text is extremely short (e.g. just a chain, no actual content)
    # usually chain-only texts are very short in English or Arabic, but let's stick to keywords
    if len(text.split()) < 40:
        for kw in chain_keywords_english:
            if kw.lower() in text:
                is_secondary = True
                break
                
    if is_secondary:
        secondary_count += 1
        if secondary_count <= 5:
            print(f'Secondary Found [{h[1]}]: {h[2][:100]}')

print(f'\nTotal secondary candidates found out of {len(all_hadiths)}: {secondary_count}')
