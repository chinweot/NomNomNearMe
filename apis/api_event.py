import os
import requests
from datetime import datetime, timezone
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model_text = genai.GenerativeModel("gemini-2.5-flash")

def get_coordinates(location):
    url = "https://nominatim.openstreetmap.org/search"
    params = {'q': location, 'format': 'json', 'limit': 1}
    headers = {'User-Agent': 'EventFinderApp/1.0'}
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    data = response.json()
    if not data:
        raise ValueError("Location not found.")
    return float(data[0]['lat']), float(data[0]['lon'])

def get_upcoming_events(lat, lon, token):
    url = "https://api.predicthq.com/v1/events/"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        'location': f'{lat},{lon};within:10km',
        'limit': 20,  # Only fetch 20 events
        'sort': 'start',
        'start.gte': datetime.now(timezone.utc).isoformat()
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get('results', [])

def format_events_for_prompt(events):
    lines = []
    for i, e in enumerate(events, start=1):
        try:
            dt = datetime.strptime(e['start'], '%Y-%m-%dT%H:%M:%SZ')
            dt_str = dt.strftime('%A, %B %d, %Y at %I:%M %p')
        except:
            dt_str = e['start']
        lat, lon = e['location']
        lines.append(
            f"{i}. Title: {e['title']}\n"
            f"   Date/Time: {dt_str}\n"
            f"   Location (lat,lon): {lat:.4f},{lon:.4f}\n"
        )
    return "\n".join(lines)

def build_genai_prompt(events_text, user_location):
    return f"""
You are given a list of upcoming events with raw data including event name, start date and time, and location coordinates. Your task is to:

1. Filter and include only events that are located in or very near **"{user_location}"** (in that city or  state).
2. For each event, try to estimate a **realistic price range in USD** based on the event type, location, and public listings. If the price is unknown, say "Price: Unknown".
3. Provide a concise, clear summary of each event.
4. Return only the **top 10 most relevant** and verified events.

Format your response as a JSON array of objects, where each object includes:

- "title": Verified event name.
- "datetime": Confirmed start date and time in a readable format.
- "location": Verified location (venue, city, or address).
- "price_range": Estimated ticket price or cost, like "$15–$30" or "Free" or "Price: Unknown".
- "summary": A short summary of the event.

Here is the raw event data:

{events_text}

Please ensure all data is accurate and location-based for: {user_location}.
"""

def genai_call(prompt: str) -> str:
    try:
        response = model_text.generate_content(prompt)
        return response.text
    except Exception as e:
        print("GenAI error:", e)
        return ""

def main():
    try:
        location = input("Enter your location (city or state): ").strip()
        token = "BQlg6IuBbo8zlPBeS42b-N850YHYXbcewIMKK5nH"  # Replace with your real token

        lat, lon = get_coordinates(location)
        print(f"\n🔍 Fetching events near {location}...\n")
        events = get_upcoming_events(lat, lon, token)

        if not events:
            print("No upcoming events found near your location.")
            return

        events_text = format_events_for_prompt(events)
        prompt = build_genai_prompt(events_text, location)

        print("🧠 Sending event data to GenAI for location filtering and price estimation...\n")
        genai_response = genai_call(prompt)

        print("🎉 Top 10 Events Near You:")
        print(genai_response)

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
