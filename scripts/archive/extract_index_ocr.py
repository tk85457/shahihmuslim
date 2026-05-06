import fitz
import easyocr
import re
import os
import sqlite3

pdf_dir = r'C:\Users\tk854\Desktop\bukhari'
db_path = r'c:\Users\tk854\Desktop\New folder\Shahih al-bukhari\shahihalbukhari\assets\database\bukhari.db'

def extract_index():
    print("Initializing Reader...")
    reader = easyocr.Reader(['ur', 'ar'], gpu=False)

    # We will just process the first volume's index as a proof of concept
    vol1_path = os.path.join(pdf_dir, 'Sahi-Bukhari-Jilad-1.pdf')
    doc = fitz.open(vol1_path)

    # Pages 9-16 seem to contain the index for Vol 1
    extracted_titles = []

    for p_idx in range(9, 13):
        print(f"Processing Vol 1, Page {p_idx+1}...")
        page = doc.load_page(p_idx)
        pix = page.get_pixmap(dpi=150)
        img_data = pix.tobytes("png")

        result = reader.readtext(img_data, detail=0)

        # Simple heuristic: lines containing a dash might be index entries
        for line in result:
            line = line.strip()
            if '-' in line or 'بّاب' in line or 'إب' in line:
                extracted_titles.append(line)
                print(f"Index Entry Found: {line}")

    doc.close()

    print(f"\nExtracted {len(extracted_titles)} potential titles.")
    return extracted_titles

if __name__ == "__main__":
    if os.path.exists(pdf_dir):
        extract_index()
    else:
        print("Directory not found")
