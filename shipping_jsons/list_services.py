import requests

url = "https://api.shipengine.com/v1/carriers/se-660215/services"

payload={}
headers = {
  'Host': 'api.shipengine.com',
  'API-Key': 'TEST_pTjqOjvNiKsTgNXKGtLi1jWEzUuDadyhO4uLfQSzXWw'
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
