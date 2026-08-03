import json
import urllib.request
payload = json.dumps({'kullanici_adi': 'admin', 'sifre': 'Admin123!'}).encode()
req = urllib.request.Request('http://127.0.0.1:8000/admin/giris', data=payload, headers={'Content-Type': 'application/json'}, method='POST')
with urllib.request.urlopen(req) as response:
    print(response.read().decode())
