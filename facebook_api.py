import requests

ACCESS_TOKEN = 'EAAR5WFWEVbEBPP9J6MBZBmwZCNDNcIJzAH1kanHvzAZCsFjQIeY29ukgTLTx3mOsLSNylr8ZAItZBb8WRBeJvXAlt9VLRmAPtJS6yWystpGV69nmKZAW2wPhC9cryYiDO0beYdmLpbmY9S6yMoaRe1X14vwKdMJcHngeFSaGLOYljhXqPfj72ZBd4byZC87pbnOcbB8N7jqyZBSwEZBFtsZAzZBq0LCU5u8ZCHWU9BFWtMrsZBH46BbSeLuY4mKeQJkYZBAAkwxWYDdzKae1PU7gSDQ3g4ZD'
PAGE_USERNAME = "nycfreeevents"

url = f"https://graph.facebook.com/v18.0/{PAGE_USERNAME}"
params = {
    "access_token": ACCESS_TOKEN,
    "fields": "id,name"
}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    print(f"Page ID: {data['id']} | Name: {data['name']}")
else:
    print("Error:", response.status_code, response.text)
