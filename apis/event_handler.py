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
    terms_lower = terms.lower() if terms else ""
    # If user is searching for free food/events, use Reddit only
    if "free food" in terms_lower or terms_lower.strip() == "free":
        reddit_events = search_reddit_events(
            location=location,
            terms=terms,
            reddit_client_id=REDDIT_CLIENT_ID,
            reddit_client_secret=REDDIT_CLIENT_SECRET,
            reddit_user_agent=REDDIT_USER_AGENT
        )
        all_events.extend(reddit_events)
    else:
        yelp_events = search_yelp_businesses(
            location=location,
            terms=terms,
            yelp_api_key=YELP_API_KEY,
            limit=10,
            radius=40000,
        )
        all_events.extend(yelp_events)
    return all_events