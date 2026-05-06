import fitz
import os

pdf_path = r'C:\Users\tk854\Desktop\bukhari\Sahi-Bukhari-Jilad-1.pdf'
if os.path.exists(pdf_path):
    doc = fitz.open(pdf_path)

    # Check page 100
    p_idx = 100
    if p_idx < len(doc):
        page = doc.load_page(p_idx)
        print(f"\n--- Page {p_idx + 1} ---")
        print(f"Text length: {len(page.get_text().strip())}")
        print(page.get_text()[:1000])

        print("\n--- Fonts ---")
        print(page.get_fonts())

        print("\n--- Images ---")
        print(page.get_images())

    doc.close()
else:
    print(f"File not found: {pdf_path}")
