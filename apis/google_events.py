import os
import requests
import json
import time

CACHE_FILE = os.path.join(os.path.dirname(__file__), 'google_events_cache.json')
CACHE_TTL = 24 * 3600  # 24 hours

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

def get_google_events(location, query=None, hl='en', gl='us'):
    api_key = os.getenv('SERPAPI_KEY')
    if not api_key:
        raise ValueError('SERPAPI_KEY not set in environment')
    if not query:
        # Try to use user interests from environment/session if available
        user_interests = os.getenv('USER_INTERESTS')
        if user_interests:
            query = f"{user_interests} events in {location}"
        else:
            query = f"Events in {location}"
    cache = load_cache()
    now = time.time()
    cache_key = f"{location}:{query}:{hl}:{gl}"
    if cache_key in cache:
        cached = cache[cache_key]
        if now - cached['timestamp'] < CACHE_TTL:
            print(f"Using cached Google events for {cache_key}")
            return cached['events']
    # Not cached or expired, fetch from API
    print(f"Fetching new Google events from API for {cache_key}")
    params = {
        'engine': 'google_events',
        'q': query,
        'location': location,
        'hl': hl,
        'gl': gl,
        'api_key': api_key
    }
    url = 'https://serpapi.com/search.json'
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return []
    data = response.json()
    events = data.get('events_results', [])
    # Cache the result
    cache[cache_key] = {'timestamp': now, 'events': events}
    save_cache(cache)
    return events
