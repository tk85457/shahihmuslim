import json

file_path = r'C:\Users\tk854\Music\Downloads\urd-bukhari.min.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("Metadata:", json.dumps(data.get('metadata', {}), indent=2, ensure_ascii=False))

first_hadith = data['hadiths'][0]
print("\nFirst hadith typing:")
for k, v in first_hadith.items():
    print(f"{k}: {type(v)} = {v}")

if 'reference' in first_hadith:
    print("\nReference typing:")
    for k, v in first_hadith['reference'].items():
        print(f"{k}: {type(v)} = {v}")
