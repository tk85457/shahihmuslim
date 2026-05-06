import json
import os

base_dir = r'C:\Users\tk854\Desktop\New folder\Shahih al-bukhari\shahihalbukhari'
urd_path = os.path.join(base_dir, 'urd-bukhari.json')

with open(urd_path, 'r', encoding='utf-8') as f:
    urd_data = json.load(f)['hadiths']

print("Keys in a single hadith object:")
print(list(urd_data[0].keys()))

print("\nSample Object:")
print(json.dumps(urd_data[0], ensure_ascii=False, indent=2))
