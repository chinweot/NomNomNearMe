from apis.user_events import add_user_event


import random
from datetime import datetime, timedelta

major_cities = [
    ("New York", "America/New_York"),
    ("Los Angeles", "America/Los_Angeles"),
    ("Chicago", "America/Chicago"),
    ("Houston", "America/Chicago"),
    ("Phoenix", "America/Phoenix"),
    ("Philadelphia", "America/New_York"),
    ("San Antonio", "America/Chicago"),
    ("San Diego", "America/Los_Angeles"),
    ("Dallas", "America/Chicago"),
    ("San Jose", "America/Los_Angeles")
]

tags = ["food", "music", "sports", "comedy", "networking", "art", "education", "festival", "other"]
venues = [
    "Community Center", "City Park", "Downtown Plaza", "Tech Hub", "Art Gallery", "Public Library",
    "Rooftop Bar", "Local Cafe", "University Hall", "Amphitheater", "Convention Center", "Museum"
]
event_types = {
    "food": ["Pizza Night", "Taco Tuesday", "Food Truck Rally", "Vegan Potluck", "BBQ Bash"],
    "music": ["Jazz Night", "Rock Concert", "Open Mic", "Classical Recital", "DJ Dance Party"],
    "sports": ["Soccer Tournament", "Basketball Game", "5K Run", "Yoga in the Park", "Pickleball Meetup"],
    "comedy": ["Stand-Up Night", "Improv Show", "Comedy Jam", "Open Mic Comedy", "Laugh Fest"],
    "networking": ["Tech Mixer", "Startup Pitch", "Career Fair", "Women in Business", "Young Professionals Night"],
    "art": ["Art Walk", "Gallery Opening", "Craft Fair", "Photography Expo", "Sculpture Showcase"],
    "education": ["Coding Bootcamp", "Science Talk", "Book Club", "Language Exchange", "History Lecture"],
    "festival": ["Spring Festival", "Cultural Parade", "Film Fest", "Food & Wine Fest", "Street Fair"],
    "other": ["Board Game Night", "Trivia Night", "Charity Auction", "Pet Adoption", "Garden Tour"]
}
descriptions = {
    "food": "Enjoy delicious food and meet new friends!",
    "music": "Live music and great vibes await you.",
    "sports": "Get active and join the fun!",
    "comedy": "Laugh out loud with local comedians.",
    "networking": "Connect with professionals and expand your network.",
    "art": "Experience creativity and inspiration.",
    "education": "Learn something new at this free event.",
    "festival": "Celebrate with the community at this festival.",
    "other": "A unique event for everyone to enjoy."
}

sample_events = []
base_date = datetime(2025, 8, 1, 18, 0)
for i in range(100):
    city, timezone = major_cities[i % len(major_cities)]
    tag = random.choice(tags)
    event_title = f"{random.choice(event_types[tag])} in {city}"
    location = f"{random.choice(venues)}, {city}"
    event_time = (base_date + timedelta(days=i, hours=random.randint(0, 4))).strftime("%Y-%m-%d %H:%M")
    description = descriptions[tag]
    sample_events.append({
        "title": event_title,
        "location": location,
        "event_time": event_time,
        "timezone": timezone,
        "tag": tag,
        "description": description
    })


for event in sample_events:
    add_user_event(
        event["title"],
        event["location"],
        event["event_time"],
        event["timezone"],
        event.get("tag"),
        event.get("description")
    )

print("User events database populated with sample events.")
