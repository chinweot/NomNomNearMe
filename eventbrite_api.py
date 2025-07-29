
import requests
from datetime import datetime, timezone

token = "H5CD7QVC2V6ZCF5XBU2B"

url = "https://www.eventbriteapi.com/v3/events/search/"
headers = {
    "Authorization": f"Bearer {token}"
}
params = {
    "location.address": "new york",
    "expand": "venue",
    "start_date.range_start": datetime.now(timezone.utc).isoformat()
}

response = requests.get(url, headers=headers, params=params)

if response.status_code != 200:
    print("Error:", response.status_code)
    print(response.text)
else:
    data = response.json()
    events = data.get("events", [])
    if not events:
        print("No events found.")
    else:
        for event in events:
            print(f"{event['name']['text']} — {event['start']['local']}")


