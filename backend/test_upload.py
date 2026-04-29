import requests
import json

url = "http://127.0.0.1:8000/upload"
files = {'file': open('dummy.txt', 'rb')}
response = requests.post(url, files=files)

print(json.dumps(response.json(), indent=2))
