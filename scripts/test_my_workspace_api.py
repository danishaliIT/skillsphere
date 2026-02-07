import sys
import requests

if len(sys.argv) < 2:
    print('Usage: test_my_workspace_api.py <ACCESS_TOKEN>')
    sys.exit(1)

token = sys.argv[1]
url = 'http://127.0.0.1:8000/api/courses/my-workspace/'
headers = {'Authorization': f'Bearer {token}'}

resp = requests.get(url, headers=headers)
print('Status:', resp.status_code)
try:
    print('JSON:', resp.json())
except Exception:
    print('Text:', resp.text)
