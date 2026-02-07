import sys
import requests

if len(sys.argv) < 2:
    print('Usage: debug_request.py <ACCESS_TOKEN>')
    sys.exit(1)

token = sys.argv[1]
url = 'http://127.0.0.1:8000/api/courses/my-workspace/'
headers = {'Authorization': f'Bearer {token}'}

r = requests.get(url, headers=headers)
print('Status:', r.status_code)
print('\n--- RESPONSE START ---\n')
print(r.text[:8000])
print('\n--- RESPONSE END ---\n')
