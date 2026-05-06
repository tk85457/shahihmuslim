import json
import sqlite3
import os

# Configuration
DB_PATH = r'C:\Users\tk854\Desktop\New folder\Shahih al-bukhari\shahihalbukhari\assets\db\sahih_bukhari.db'
INPUT_FILE = r'C:\Users\tk854\Desktop\New folder\Shahih al-bukhari\shahihalbukhari\ajax_urdu_data.json'

def integrate():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        all_data = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create a mapping of sunnah_book_number -> chapters.id
    cursor.execute("SELECT book_number, id FROM chapters")
    book_to_id = {row[0]: row[1] for row in cursor.fetchall()}

    update_data = [] # List of (urdu_text, chapter_id, hadith_number)

    stats_processed = 0

    for book_num_str, hadiths_list in all_data.items():
        book_num = int(book_num_str)
        chapter_id = book_to_id.get(book_num)

        if not chapter_id:
            continue

        for h in hadiths_list:
            hadith_num = str(h['hadithNumber'])
            sanad = h.get('hadithSanad', '')
            text = h.get('hadithText', '')

            full_urdu = f"{sanad}\n\n{text}".strip()
            full_urdu = full_urdu.replace('</b>', '').replace('<b>', '')
            full_urdu = full_urdu.replace('<p>', '').replace('</p>', '\n')
            full_urdu = full_urdu.replace('<br>', '\n').replace('<br/>', '\n')

            if not full_urdu or len(full_urdu) < 5:
                continue

            # We'll update only if urdu_text is null or empty in DB
            # To avoid slow row-by-row checks, we can use a COALESCE logic in WHERE or just UPDATE
            # But the requirement is to fill MISSING ones.
            # Best way: UPDATE hadiths SET urdu_text = ? WHERE chapter_id = ? AND hadith_number = ? AND (urdu_text IS NULL OR LENGTH(urdu_text) < 5)
            update_data.append((full_urdu, chapter_id, hadith_num))
            stats_processed += 1

    if update_data:
        print(f"Updating {len(update_data)} entries...")
        cursor.executemany("""
            UPDATE hadiths
            SET urdu_text = ?
            WHERE chapter_id = ? AND hadith_number = ?
            AND (urdu_text IS NULL OR LENGTH(urdu_text) < 10)
        """, update_data)
        conn.commit()
        print(f"Update applied. Rows affected: {cursor.rowcount}")

    conn.close()
    print(f"Integration complete.")

if __name__ == "__main__":
    integrate()
