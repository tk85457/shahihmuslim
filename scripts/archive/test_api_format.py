import ssl, urllib.request, json

API_KEY = '$2y$10$ySRzfrqgvtpHTUHR6iZ2NC7gu9PPdyOBTjFf1wD0Dv6PpkhHy32'
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

# Fetch page 3 with 5 hadiths (hadiths 11-15)
url = f'https://hadithapi.com/api/hadiths/?apiKey={API_KEY}&book=sahih-bukhari&page=3&limit=5'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=60, context=ssl_ctx) as resp:
    d = json.loads(resp.read().decode('utf-8'))

hadiths = d['hadiths']['data']
for h in hadiths:
    num = h.get('hadithNumber')
    urdu = (h.get('hadithUrdu') or '')[:40]
    print(f"hadithNumber={repr(num)} type={type(num).__name__} urdu={repr(urdu)}")

print("\nAll keys in a hadith:", list(hadiths[0].keys()))
