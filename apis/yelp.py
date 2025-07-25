import json 
import os 
import requests 
from urllib.parse import quote_plus
from dotenv import load_dotenv
#from dateutil import parser

load_dotenv()


key_value = os.environ['YELP_KEY']
url = "https://api.yelp.com/v3/businesses/search"
headers = {"Authorization": f"Bearer {key_value}", "accept": "application/json"}

def format_date(iso_str):
    
    try: 

        months = []
    except:
        return "Invalid Date"


def search_yelp_businesses(location, terms, yelp_api_key, limit, radius):
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
        "categories": ",".join(categories_list) if categories_list else None,
        "term": terms,
        "limit": limit,
        "radius": radius,
        "location": location
    }
    # Remove None values
    params = {k: v for k, v in params.items() if v}

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    yelp_businesses = []
    for business in response.json().get("businesses", []):
        yelp_businesses.append(
            {
                "source": "yelp",
                "external_id": business["id"],
                "global_id": f"yelp_{business['id']}",
                "title": business["name"],
                "location": ", ".join(business["location"]["display_address"]),
                "rating": business.get("rating"),
                "tags": [cat["title"] for cat in business.get("categories", [])],
                "url": business["url"],
                "price": business.get("price", "?")
            }
        )

    return yelp_businesses