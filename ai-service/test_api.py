import requests

url = "http://localhost:5000/describe"

data = {
    "input": "online banking system"
}

response = requests.post(url, json=data)

print("Status:", response.status_code)
print("Response:", response.json())