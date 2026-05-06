import urllib.request
import json
import os

url = "https://huggingface.co/datasets/meeAtif/hadith_datasets/resolve/main/Sahih%20al-Bukhari.json?download=true"
output_path = r'C:\Users\tk854\Desktop\New folder\Shahih al-bukhari\shahihalbukhari\hf_sample.json'

print(f"Downloading {url}...")
urllib.request.urlretrieve(url, output_path)

print(f"Downloaded to {output_path}")

if os.path.exists(output_path):
    with open(output_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        print(f"Total entries: {len(data)}")
        if len(data) > 0:
            sample = data[0]
            print("\nSample keys:")
            print(list(sample.keys()))
            print("\nSample content:")
            for k, v in sample.items():
                print(f"{k}: {str(v)[:100]}")
