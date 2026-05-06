import urllib.request
import json

API_KEY = '$2y$10$ySRzfrqgvtpHTUHR6iZ2NC7gu9PPdyOBTjFf1wD0Dv6PpkhHy32'

# First check the API format
url = f'https://hadithapi.com/api/hadiths/?apiKey={API_KEY}&book=sahih-bukhari&page=1&limit=5'
print(f'Testing URL: {url}')

try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print('Keys:', list(data.keys()))
        if 'hadiths' in data:
            print('hadiths keys:', list(data['hadiths'].keys()) if isinstance(data['hadiths'], dict) else 'list')
            if isinstance(data['hadiths'], dict) and 'data' in data['hadiths']:
                sample = data['hadiths']['data'][0]
                print('Sample hadith keys:', list(sample.keys()))
                print('Sample hadith_urdu:', str(sample.get('hadithUrdu', ''))[:100])
                print('Sample hadithNumber:', sample.get('hadithNumber'))
                print('Total hadiths available:', data['hadiths'].get('total'))
except Exception as e:
    print(f'Error: {e}')
