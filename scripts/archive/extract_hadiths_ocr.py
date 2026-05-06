import fitz
import easyocr
import re
import os
import sqlite3
from PIL import Image

pdf_dir = r'C:\Users\tk854\Desktop\bukhari'
db_path = r'c:\Users\tk854\Desktop\New folder\Shahih al-bukhari\shahihalbukhari\assets\Database\bukhari.db'

def setup_db():
    conn = sqlite3.connect(db_path)
    return conn

def extract_hadiths():
    print("Initializing Reader...")
    reader = easyocr.Reader(['ur', 'ar'], gpu=False)

    vol1_path = os.path.join(pdf_dir, 'Sahi-Bukhari-Jilad-1.pdf')
    doc = fitz.open(vol1_path)

    # Start scanning from where hadiths usually begin in Vol 1 (e.g. Page 54)
    start_page = 54
    end_page = 60

    print(f"Scanning pages {start_page} to {end_page}...")

    for p_idx in range(start_page, end_page):
        print(f"\n--- Processing Vol 1, Page {p_idx+1} ---")
        page = doc.load_page(p_idx)
        pix = page.get_pixmap(dpi=150)
        img_data = pix.tobytes("png")

        result = reader.readtext(img_data, detail=0)

        full_text = " \n".join(result)
        print(full_text[:500] + "...\n")

        # Look for numbers that might be Hadith numbers
        numbers = re.findall(r'\b\d+\b', full_text)
        if numbers:
            print(f"Potential Hadith numbers found on page: {numbers}")

    doc.close()
    conn.close()

if __name__ == "__main__":
    if os.path.exists(pdf_dir):
        extract_hadiths()
    else:
        print("Directory not found")
