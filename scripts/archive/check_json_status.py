import json
import os

f = 'ajax_urdu_data.json'
if not os.path.exists(f):
    print("ajax_urdu_data.json nahi mila!")
else:
    d = json.load(open(f, encoding='utf-8'))
    books = sorted(d.keys(), key=lambda x: int(x))
    total_hadiths = sum(len(d[b]) for b in books)
    print(f"Books scraped: {len(books)}")
    print(f"Total hadiths in JSON: {total_hadiths}")
    if books:
        print(f"Books: {books[0]} to {books[-1]}")
    print("---")
    for b in books:
        print(f"  Book {b}: {len(d[b])} hadiths")
