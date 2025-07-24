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

    # Map user dietary terms to Yelp categories
    dietary_map = {
        "vegan": "vegan",
        "vegetarian": "vegetarian",
        "gluten-free": "gluten_free",
        "kosher": "kosher",
        "halal": "halal",
        "organic": "organic",
        "healthy": "healthmarkets",
        "juice": "juicebars",
        "salad": "salad",
        "seafood": "seafood",
        "bbq": "bbq",
        "pizza": "pizza",
        "desserts": "desserts"
    }

    # Filter and map terms to Yelp categories
    categories_list = []
    if terms.strip():
        for t in terms.split(","):
            key = t.strip().lower()
            if key in dietary_map:
                categories_list.append(dietary_map[key])
            else:
                categories_list.append(quote_plus(key))

    params = {
        "categories": ",".join(categories_list) if categories_list else terms,
        "limit": limit,
        "is_free": True,
        "radius": radius,
        "location": location,
        "start_date": start_date
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    yelp_events = []
    for event in response.json().get("events", []):
        # Optionally, filter events by dietary tags in the response
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