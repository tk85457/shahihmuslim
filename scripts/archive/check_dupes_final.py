import json

base_dir = r'C:\Users\tk854\Music\Downloads'
ara_path = f'{base_dir}\\ara-bukhari.min.json'

with open(ara_path, 'r', encoding='utf-8') as f:
    data = json.load(f)['hadiths']

nums = [h['hadithnumber'] for h in data]
int_nums = [int(n) for n in nums]

print(f"Total: {len(nums)}")
print(f"Unique strings: {len(set(nums))}")
print(f"Unique ints: {len(set(int_nums))}")

# Find duplicates as ints
from collections import Counter
counts = Counter(int_nums)
dupes = [n for n, c in counts.items() if c > 1]
print(f"Duplicate ints: {len(dupes)}")
if dupes:
    print(f"Sample dupes: {dupes[:5]}")
