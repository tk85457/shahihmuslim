import requests
import json
import sqlite3
import time
import os

# Configuration
DB_PATH = r'C:\Users\tk854\Desktop\New folder\Shahih al-bukhari\shahihalbukhari\assets\db\sahih_bukhari.db'
OUTPUT_FILE = r'C:\Users\tk854\Desktop\New folder\Shahih al-bukhari\shahihalbukhari\ajax_urdu_data.json'
BASE_URL = "https://sunnah.com/ajax/urdu/bukhari/{}"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}

def fetch_book(book_num):
    url = BASE_URL.format(book_num)
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch Book {book_num} - Status: {response.status_code}")
    except Exception as e:
        print(f"Error fetching Book {book_num}: {e}")
    return None

def main():
    # We'll fetch all books from 1 to 97
    all_data = {}
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            try:
                all_data = json.load(f)
            except:
                all_data = {}

    for book_num in range(1, 98):
        book_key = str(book_num)
        if book_key in all_data and all_data[book_key]:
            print(f"Book {book_num} already fetched. Skipping.")
            continue

        print(f"Fetching Book {book_num}...")
        data = fetch_book(book_num)
        if data:
            all_data[book_key] = data
            # Save intermittently
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
            print(f"Successfully fetched Book {book_num} ({len(data)} hadiths).")

        time.sleep(2.0) # Polite delay

    print("Data acquisition complete.")

if __name__ == "__main__":
    main()
