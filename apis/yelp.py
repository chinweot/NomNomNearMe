import json 
import os 
import requests 
from urllib.parse import quote_plus
from dotenv import load_dotenv
#from dateutil import parser

load_dotenv()

key_value = os.environ['YELP_KEY']
url = "https://api.yelp.com/v3/events"

headers = {"Authorization" : f"Bearer {key_value}", "accept" : "application/json"}

# defining query parameters 
location = "Washington, DC"
radius = 100
categories = ["free food", "free samples", "free food events"]
limit = 5

# Unix date
start_date = "1746140230"

def format_date(iso_str):
    
    try: 

        months = []
    except:
        return "Invalid Date"

def search_yelp_events(location, terms, yelp_api_key, limit, radius):

    params = {
        "categories" : terms,
        "limit" : limit,
        "is_free" : True,
        "radius" : radius,
        "location" : location,
        "start_date" : start_date
    }
    if terms.strip():
        params["categories"] = ",".join(
            quote_plus(t.strip()) for t in terms.split(",") if t.strip()
        )

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    yelp_events = []
    for event in response.json().get("events", []):
        yelp_events.append(
            {
                "source": "yelp",                     
                "external_id": event["id"],            
                "global_id": f"yelp_{event['id']}",
                "title" : event["name"],
                "location" : event["location"]["display_address"][0],
                "date" : event["time_start"],
                "tags" : event.get("category", []),
                "url" : event["event_site_url"]
            }
        )

    return yelp_events