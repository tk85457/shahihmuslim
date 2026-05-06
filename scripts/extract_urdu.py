import json
import os

# Paths
missing_json_path = r'C:\Users\tk854\Desktop\New folder\Shahih al-bukhari\shahihalbukhari\missing_urdu_translations.json'
source_urdu_json_path = r'C:\Users\tk854\Music\Downloads\urd-bukhari.min.json'
output_recovered_path = r'C:\Users\tk854\Desktop\New folder\Shahih al-bukhari\shahihalbukhari\recovered_urdu_translations.json'

def extract_translations():
    # Load missing translations list
    with open(missing_json_path, 'r', encoding='utf-8') as f:
        missing_data = json.load(f)

    missing_numbers = set()
    for item in missing_data:
        # Using 'num' as seen in missing_urdu_translations.json
        missing_numbers.add(str(item.get('num')))

    print(f"Total missing: {len(missing_numbers)}")

    # Load source Urdu data
    # Note: The file is large (10MB), so reading it once is fine.
    with open(source_urdu_json_path, 'r', encoding='utf-8') as f:
        source_data = json.load(f)

    hadiths = source_data.get('hadiths', [])
    recovered = {}

    found_count = 0
    empty_in_source = 0
    not_in_source = 0
    recovered = {}

    # Create a mapping for quick lookup
    lookup = {}
    for h in hadiths:
        h_num = str(h.get('hadithnumber'))
        a_num = str(h.get('arabicnumber'))
        text = h.get('text', '').strip()
        if h_num not in lookup or text:
            lookup[h_num] = text
        if a_num not in lookup or text:
            lookup[a_num] = text

    for num in missing_numbers:
        if num in lookup:
            text = lookup[num]
            if text:
                recovered[num] = text
                found_count += 1
            else:
                empty_in_source += 1
        else:
            not_in_source += 1

    print(f"Total missing: {len(missing_numbers)}")
    print(f"Found and recovered: {found_count}")
    print(f"Found but empty in source: {empty_in_source}")
    print(f"Not found in source: {not_in_source}")

    # Save recovered translations
    with open(output_recovered_path, 'w', encoding='utf-8') as f:
        json.dump(recovered, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    extract_translations()
