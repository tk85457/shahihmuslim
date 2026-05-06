import urllib.request
import json
import os

ara_url = "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/ara-bukhari.json"
urd_url = "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/urd-bukhari.json"
base_dir = r'C:\Users\tk854\Desktop\New folder\Shahih al-bukhari\shahihalbukhari'
ara_path = os.path.join(base_dir, 'ara-bukhari.json')
urd_path = os.path.join(base_dir, 'urd-bukhari.json')

print(f"Downloading {ara_url}...")
urllib.request.urlretrieve(ara_url, ara_path)

print(f"Downloading {urd_url}...")
urllib.request.urlretrieve(urd_url, urd_path)

print(f"Downloaded Arabic and Urdu DBs")

def print_sample(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        hadiths = data.get('hadiths', [])
        print(f"\n[{path}] Total hadiths: {len(hadiths)}")
        if hadiths:
            print("Sample hadith 0:")
            print(json.dumps(hadiths[0], ensure_ascii=False, indent=2))

print_sample(ara_path)
print_sample(urd_path)
