import os
from dotenv import load_dotenv 
from apis.yelp import search_yelp_businesses
from apis.reddit_api import search_reddit_events

# getting keys 
YELP_API_KEY = os.environ.get('YELP_KEY')
REDDIT_CLIENT_ID = os.environ.get('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.environ.get('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.environ.get('REDDIT_USER_AGENT')

def search_all_events(location: str, terms: str = ""):
    all_events = []

    # ---- SEARCH YELP EVENTS ----
    yelp_events = search_yelp_businesses(
            location=location,
            terms=terms,
            yelp_api_key=YELP_API_KEY,
            limit=10, # You can adjust this limit
            radius=40000, # Max radius for Yelp is ~25 miles (40000 meters)
            # start_date_unix (optional, Yelp defaults to current time if not provided)
        )
    all_events.extend(yelp_events)

    # ---- SEARCH REDDIT EVENTS ----
    reddit_events = search_reddit_events(
            location=location,
            terms=terms,
            reddit_client_id=REDDIT_CLIENT_ID,
            reddit_client_secret=REDDIT_CLIENT_SECRET,
            reddit_user_agent=REDDIT_USER_AGENT
        )
    all_events.extend(reddit_events)

    return all_events