import json 
import os 
import requests 
from dotenv import load_dotenv

load_dotenv()

key_value = os.environ['YELP_KEY']
url = "https://api.yelp.com/v3/events"

headers = {"Authorization" : f"Bearer {key_value}", "accept" : "application/json"}

# defining query parameters 
location = "Washington, DC"
radius = 100
categories = ["free food", "free samples"]
limit = 1
# Unix date
start_date = "1752598519"

params = {
    "categories" : categories,
    "limit" : 1,
    "is_free" : True,
    "radius" : radius,
    "location" : location,
    "start_date" : start_date
}

response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    try: 
        data = response.json()
        print(json.dumps(data, indent=4))
    except json.JSONDecodeError:
        print("error with decoding JSON")
        print("raw text:", response.text)
else:
    print(f"API request failed with: {response.status_code}")
    print("raw text:", response.text)
