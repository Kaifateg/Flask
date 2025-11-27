import requests

res = requests.get("127.0.0.1:5000/api/get")
print(res.json())
