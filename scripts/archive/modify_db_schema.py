import sqlite3

db_path = r'C:\Users\tk854\Desktop\New folder\Shahih al-bukhari\shahihalbukhari\assets\db\sahih_bukhari.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Altering hadiths table to support TEXT hadith_number...")
# In SQLite, we can't easily change column types with ALTER TABLE.
# We'll create a new table and copy data, but since we are re-importing everything,
# we can just drop and recreate with the new schema.

cursor.execute("DROP TABLE IF EXISTS hadiths")
cursor.execute('''
CREATE TABLE hadiths (
  id INTEGER PRIMARY KEY,
  chapter_id INTEGER NOT NULL,
  hadith_number TEXT NOT NULL,
  arabic_text TEXT NOT NULL,
  urdu_text TEXT NOT NULL,
  english_text TEXT NOT NULL,
  FOREIGN KEY (chapter_id) REFERENCES chapters (id)
)''')

conn.commit()
conn.close()
print("Done.")
