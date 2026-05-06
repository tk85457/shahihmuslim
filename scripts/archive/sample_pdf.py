import fitz  # PyMuPDF
import os

pdf_path = r'C:\Users\tk854\Desktop\bukhari\Sahi-Bukhari-Jilad-1.pdf'
if os.path.exists(pdf_path):
    doc = fitz.open(pdf_path)
    print(f"Total pages: {len(doc)}")

    # Extract first 20 pages
    for page_num in range(min(20, len(doc))):
        page = doc.load_page(page_num)
        text = page.get_text()
        print(f"\n--- Page {page_num + 1} ---")
        print(text[:2000]) # Print first 2000 chars of each page

    doc.close()
else:
    print(f"File not found: {pdf_path}")
