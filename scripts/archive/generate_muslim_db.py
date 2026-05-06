import sqlite3
import json
import os

db_path = r'C:\Users\tk854\Desktop\app\shahihmuslim\assets\db\sahih_muslim.db'
ara_path = r'C:\Users\tk854\Music\Downloads\hadith-api-1\hadith-api-1\editions\ara-muslim.min.json'
urd_path = r'C:\Users\tk854\Music\Downloads\hadith-api-1\hadith-api-1\editions\urd-muslim.min.json'
eng_path = r'C:\Users\tk854\Music\Downloads\hadith-api-1\hadith-api-1\editions\eng-muslim.min.json'

def load_data(path):
    print(f"Loading {path}...")
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

ara_json = load_data(ara_path)
urd_json = load_data(urd_path)
eng_json = load_data(eng_path)

ara_data = ara_json['hadiths']
urd_data = urd_json['hadiths']
eng_data = eng_json['hadiths']

print(f"Loaded {len(ara_data)} Arabic, {len(urd_data)} Urdu, {len(eng_data)} English hadiths.")

# Map hadithnumber to texts - Keep as string to preserve decimals
hadiths_map = {}
for i, h in enumerate(ara_data):
    n = str(h['hadithnumber'])
    hadiths_map[i] = {
        'num': n,
        'arabic': h['text'],
        'book': int(h['reference']['book']),
        'english': '',
        'urdu': ''
    }

# Mapping by hadithnumber (string) for merging
num_to_index = {data['num']: idx for idx, data in hadiths_map.items()}

for h in urd_data:
    n = str(h['hadithnumber'])
    if n in num_to_index:
        idx = num_to_index[n]
        hadiths_map[idx]['urdu'] = h['text']

for h in eng_data:
    n = str(h['hadithnumber'])
    if n in num_to_index:
        idx = num_to_index[n]
        hadiths_map[idx]['english'] = h['text']

# DB Connection
if os.path.exists(db_path):
    os.remove(db_path)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create Tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS chapters (
  id INTEGER PRIMARY KEY,
  book_number INTEGER NOT NULL,
  title_arabic TEXT NOT NULL,
  title_urdu TEXT NOT NULL,
  title_english TEXT NOT NULL,
  hadith_count INTEGER NOT NULL DEFAULT 0
)''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS hadiths (
  id INTEGER PRIMARY KEY,
  chapter_id INTEGER NOT NULL,
  hadith_number TEXT NOT NULL,
  arabic_text TEXT NOT NULL,
  urdu_text TEXT NOT NULL,
  english_text TEXT NOT NULL,
  FOREIGN KEY (chapter_id) REFERENCES chapters (id)
)''')

# Insert Chapters
print("Inserting chapters...")
ara_sections = ara_json['metadata']['sections']
urd_sections = urd_json['metadata']['sections']
eng_sections = eng_json['metadata']['sections']

translation_map = {
    '0': {'ar': 'المقدمة', 'ur': 'مقدمہ'},
    '1': {'ar': 'كتاب الإيمان', 'ur': 'کتاب الایمان'},
    '2': {'ar': 'كتاب الطهارة', 'ur': 'کتاب الطہارت'},
    '3': {'ar': 'كتاب الحيض', 'ur': 'کتاب حیض'},
    '4': {'ar': 'كتاب الصلاة', 'ur': 'کتاب الصلوٰۃ'},
    '5': {'ar': 'كتاب المساجد ومواضع الصلاة', 'ur': 'کتاب المساجد'},
    '6': {'ar': 'كتاب صلاة المسافرين وقصرها', 'ur': 'کتاب مسافروں کی نماز'},
    '7': {'ar': 'كتاب الجمعة', 'ur': 'کتاب جمعہ'},
    '8': {'ar': 'كتاب صلاة العيدين', 'ur': 'کتاب عیدین'},
    '9': {'ar': 'كتاب صلاة الاستسقاء', 'ur': 'کتاب صلوٰۃ الاستسقاء'},
    '10': {'ar': 'كتاب الكسوف', 'ur': 'کتاب کسوف'},
    '11': {'ar': 'كتاب الجنائز', 'ur': 'کتاب جنائز'},
    '12': {'ar': 'كتاب الزكاة', 'ur': 'کتاب زکوٰۃ'},
    '13': {'ar': 'كتاب الصيام', 'ur': 'کتاب روزے'},
    '14': {'ar': 'كتاب الاعتكاف', 'ur': 'کتاب اعتکاف'},
    '15': {'ar': 'كتاب الحج', 'ur': 'کتاب حج'},
    '16': {'ar': 'كتاب النكاح', 'ur': 'کتاب نکاح'},
    '17': {'ar': 'كتاب الرضاع', 'ur': 'کتاب رضاعت'},
    '18': {'ar': 'كتاب الطلاق', 'ur': 'کتاب طلاق'},
    '19': {'ar': 'كتاب اللعان', 'ur': 'کتاب لعان'},
    '20': {'ar': 'كتاب العتق', 'ur': 'کتاب غلام آزاد کرنے کے مسائل'},
    '21': {'ar': 'كتاب البيوع', 'ur': 'کتاب خرید و فروخت'},
    '22': {'ar': 'كتاب المساقاة', 'ur': 'کتاب مساقات'},
    '23': {'ar': 'كتاب الفرائض', 'ur': 'کتاب وراثت'},
    '24': {'ar': 'كتاب الهبات', 'ur': 'کتاب تحفے'},
    '25': {'ar': 'كتاب الوصية', 'ur': 'کتاب وصیت'},
    '26': {'ar': 'كتاب النذور', 'ur': 'کتاب نذریں'},
    '27': {'ar': 'كتاب الأيمان', 'ur': 'کتاب قسمیں'},
    '28': {'ar': 'كتاب القسامة والمحاربين والقصاص والديات', 'ur': 'کتاب قصاص و دیت'},
    '29': {'ar': 'كتاب الحدود', 'ur': 'کتاب حدود'},
    '30': {'ar': 'كتاب الأقضية', 'ur': 'کتاب فیصلے'},
    '31': {'ar': 'كتاب اللقطة', 'ur': 'کتاب گمشدہ چیزیں'},
    '32': {'ar': 'كتاب الجهاد والسير', 'ur': 'کتاب جہاد'},
    '33': {'ar': 'كتاب الإمارة', 'ur': 'کتاب حکومت و قیادت'},
    '34': {'ar': 'كتاب الصيد والذبائح وما يؤكل من الحيوان', 'ur': 'کتاب شکار اور ذبیحہ'},
    '35': {'ar': 'كتاب الأضاحي', 'ur': 'کتاب قربانی'},
    '36': {'ar': 'كتاب الأشربة', 'ur': 'کتاب مشروبات'},
    '37': {'ar': 'كتاب اللباس والزينة', 'ur': 'کتاب لباس اور زینت'},
    '38': {'ar': 'كتاب الآداب', 'ur': 'کتاب آداب'},
    '39': {'ar': 'كتاب السلام', 'ur': 'کتاب سلام'},
    '40': {'ar': 'كتاب الألفاظ من الأدب وغيرها', 'ur': 'کتاب الفاظ کا ادب'},
    '41': {'ar': 'كتاب الشعر', 'ur': 'کتاب شاعری'},
    '42': {'ar': 'كتاب الرؤيا', 'ur': 'کتاب خواب'},
    '43': {'ar': 'كتاب الفضائل', 'ur': 'کتاب فضائل'},
    '44': {'ar': 'كتاب فضائل الصحابة رضي الله تعالى عنهم', 'ur': 'کتاب صحابہ کے فضائل'},
    '45': {'ar': 'كتاب البر والصلة والآداب', 'ur': 'کتاب نیکی اور صلہ رحمی'},
    '46': {'ar': 'كتاب القدر', 'ur': 'کتاب تقدیر'},
    '47': {'ar': 'كتاب العلم', 'ur': 'کتاب علم'},
    '48': {'ar': 'كتاب الذكر والدعاء والتوبة والاستغفار', 'ur': 'کتاب ذکر و دعا'},
    '49': {'ar': 'كتاب الرقاق', 'ur': 'کتاب رقت انگیز باتیں'},
    '50': {'ar': 'كتاب التوبة', 'ur': 'کتاب توبہ'},
    '51': {'ar': 'كتاب صفة القيامة والجنة والنار', 'ur': 'کتاب قیامت کی صفات'},
    '52': {'ar': 'كتاب الجنة وصفة نعيمها وأهلها', 'ur': 'کتاب جنت اور اس کی نعمتیں'},
    '53': {'ar': 'كتاب الفتن وأشراط الساعة', 'ur': 'کتاب فتنے'},
    '54': {'ar': 'كتاب الزهد والرقائق', 'ur': 'کتاب زہد'},
    '55': {'ar': 'كتاب التفسير', 'ur': 'کتاب تفسیر'},
    '56': {'ar': 'كتاب التفسير', 'ur': 'کتاب تفسیر'},
}

# Book 0 corresponds to Introduction, and 1 to 56. We iterate string keys.
chapter_id_map = {} # map book_number -> db chapter_id
chapter_idx = 1
for book_str in sorted(ara_sections.keys(), key=lambda x: int(x) if x.isdigit() else 999):
    if not book_str.isdigit(): continue
    book_num = int(book_str)

    title_en = eng_sections.get(book_str, f"Book {book_num}")

    # Use translation map if available, otherwise fallback to English
    if book_str in translation_map:
        title_ar = translation_map[book_str]['ar']
        title_ur = translation_map[book_str]['ur']
    else:
        title_ar = ara_sections.get(book_str, title_en)
        title_ur = urd_sections.get(book_str, title_ar)

    cursor.execute('''
        INSERT INTO chapters (id, book_number, title_arabic, title_urdu, title_english, hadith_count)
        VALUES (?, ?, ?, ?, ?, 0)
    ''', (chapter_idx, book_num, title_ar, title_ur, title_en))

    chapter_id_map[book_num] = chapter_idx
    chapter_idx += 1

print("Inserting new hadiths...")
insert_count = 0
chapter_counts = {cid: 0 for cid in chapter_id_map.values()}

for i in sorted(hadiths_map.keys()):
    h_data = hadiths_map[i]
    h_num = h_data['num']
    book_num = h_data['book']
    chapter_id = chapter_id_map.get(book_num)

    if chapter_id is None:
        # Fallback if a book number is missing from the sections metadata
        if 1 in chapter_id_map:
            chapter_id = chapter_id_map[1]
        else:
            continue

    chapter_counts[chapter_id] += 1

    # Insert into DB
    cursor.execute('''
        INSERT INTO hadiths (id, chapter_id, hadith_number, arabic_text, urdu_text, english_text)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (i + 1, int(chapter_id), str(h_num), str(h_data['arabic']), str(h_data['urdu']), str(h_data['english'])))
    insert_count += 1

# Update chapters with hadith counts
print("Updating chapter hadith counts...")
for cid, count in chapter_counts.items():
    cursor.execute('UPDATE chapters SET hadith_count = ? WHERE id = ?', (count, cid))

# Create Indexes
print("Creating Indexes...")
cursor.execute('CREATE INDEX IF NOT EXISTS idx_hadiths_chapter ON hadiths(chapter_id)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_hadiths_number ON hadiths(hadith_number)')

conn.commit()
conn.close()

print(f"Successfully created DB with {chapter_idx - 1} chapters and {insert_count} hadiths!")
