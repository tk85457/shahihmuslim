import sqlite3
import json

db_path = r'C:\Users\tk854\Desktop\New folder\Shahih al-bukhari\shahihalbukhari\assets\db\sahih_bukhari.db'
output_path = 'missing_urdu_translations1.json'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check for various forms of "missing"
query = """
SELECT id, hadith_number, arabic_text, english_text
FROM hadiths
WHERE urdu_text IS NULL
   OR urdu_text = ''
   OR urdu_text LIKE '%available%'
   OR urdu_text LIKE '%ترجمہ دستیاب نہیں%'
"""

cursor.execute(query)
rows = cursor.fetchall()

missing_list = []
for r in rows:
    missing_list.append({
        'id': r[0],
        'num': r[1],
        'arabic': r[2],
        'english': r[3]
    })

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(missing_list, f, ensure_ascii=False, indent=2)

print(f"Found {len(missing_list)} missing Urdu translations. Saved to {output_path}")
conn.close()
