import fitz
import os

pdf_path = r'C:\Users\tk854\Desktop\bukhari\Sahi-Bukhari-Jilad-1.pdf'
if os.path.exists(pdf_path):
    doc = fitz.open(pdf_path)

    # Check pages 3 to 15 for index
    for p_idx in range(2, 15):
        page = doc.load_page(p_idx)
        print(f"\n--- Page {p_idx + 1} ---")
        text = page.get_text()
        print(text)

        # Check for images
        imgs = page.get_images()
        if imgs:
            print(f"Page {p_idx+1} has {len(imgs)} images.")

    doc.close()
else:
    print(f"File not found: {pdf_path}")
