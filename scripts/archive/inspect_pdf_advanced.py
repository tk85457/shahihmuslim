import fitz
import os

pdf_path = r'C:\Users\tk854\Desktop\bukhari\Sahi-Bukhari-Jilad-1.pdf'
if os.path.exists(pdf_path):
    doc = fitz.open(pdf_path)
    print(f"Metadata: {doc.metadata}")
    print(f"Table of Contents: {doc.get_toc()}")

    # Try different extraction on page 5 (usually content starts around here)
    for p_idx in [4, 5, 6, 7, 8, 9, 10]:
        if p_idx < len(doc):
            page = doc.load_page(p_idx)
            print(f"\n--- Page {p_idx + 1} Blocks ---")
            blocks = page.get_text("blocks")
            for b in blocks[:10]: # Print first 10 blocks
                print(b[4].strip())

    doc.close()
else:
    print(f"File not found: {pdf_path}")
