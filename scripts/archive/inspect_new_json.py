import json

file_path = r'C:\Users\tk854\Music\Downloads\urd-bukhari.min.json'
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("Top level keys:", list(data.keys()))

    if 'hadiths' in data:
        hadiths = data['hadiths']
        print(f"Total hadiths: {len(hadiths)}")
        print("Keys in first hadith:", list(hadiths[0].keys()))
        print("First hadith sample:")
        print(json.dumps(hadiths[0], indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error reading {file_path}: {e}")
