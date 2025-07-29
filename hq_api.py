import requests
from datetime import datetime, timezone
import time

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

def get_place_name(lat, lon):
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {'lat': lat, 'lon': lon, 'format': 'json'}
    headers = {'User-Agent': 'EventFinderApp/1.0'}
    try:
        resp = requests.get(url, params=params, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return data.get('address', {}).get('city', data.get('display_name'))
    except:
        return f"{lat:.4f}, {lon:.4f}"

def get_upcoming_events(lat, lon, token):
    url = "https://api.predicthq.com/v1/events/"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        'location': f'{lat},{lon};within:10km',
        'limit': 20,  # Fetch only 20 events
        'sort': 'start',
        'start.gte': datetime.now(timezone.utc).isoformat()
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get('results', [])

def format_events(events):
    formatted = []
    for event in events:
        lat, lon = event['location']
        place = get_place_name(lat, lon)
        time.sleep(1)  # Respect Nominatim rate limits
        try:
            dt = datetime.strptime(event['start'], '%Y-%m-%dT%H:%M:%SZ')
            dt_str = dt.strftime('%A, %B %d, %Y at %I:%M %p')
        except:
            dt_str = event['start']
        formatted.append({
            'title': event['title'],
            'location': place,
            'datetime': dt_str
        })
    return formatted

def main():
    try:
        location = input("Enter your location: ").strip()
        lat, lon = get_coordinates(location)
        location_name = get_place_name(lat, lon)  # Get readable searched location

        print(f"\n🔍 Looking for upcoming events near {location_name}...\n")

        token = "BQlg6IuBbo8zlPBeS42b-N850YHYXbcewIMKK5nH"  # Replace with your actual PredictHQ API token
        events = get_upcoming_events(lat, lon, token)

        if not events:
            print("No upcoming events found near your location.")
            return

        formatted_events = format_events(events)

        print(f"🎉 Upcoming events near {location_name}:\n")
        for e in formatted_events:
            print(f"✅ {e['title']}\n📍 {e['location']}\n🕒 {e['datetime']}\n")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
