import os
import praw
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables (Google API key)
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize Gemini model (text only)
model_text = genai.GenerativeModel("gemini-2.5-flash")

def genai_call(prompt: str) -> str:
    try:
        response = model_text.generate_content(prompt)
        return response.text
    except Exception as e:
        print("GenAI error:", e)
        return "No response"

# Initialize Reddit API
reddit = praw.Reddit(
    client_id="_NVENxJfWxwYEcDIiDwM2w",
    client_secret="yBBXkr1SLRA--4ifIqC8LRC5w5j3cA",
    user_agent="free-food-event-finder"
)

# user_input needs to be modified 
user_input = input("Enter your city: ").strip().lower()

# Map cities to subreddits
city_to_subreddit = {
    "nyc": "nyc", "new york": "nyc",
    "los angeles": "LosAngeles", "la": "LosAngeles",
    "chicago": "chicago", "austin": "Austin",
    "san francisco": "bayarea", "sf": "bayarea",
    "seattle": "Seattle", "houston": "houston",
    "boston": "boston",
}

subreddit_name = city_to_subreddit.get(user_input)
if not subreddit_name:
    print(f" Sorry, no subreddit found for '{user_input}'. Try a major city next time")
    exit()

# Search for free events
keywords = "free food OR pizza OR snacks OR lunch OR bbq OR dinner OR admission OR parking"
subreddit = reddit.subreddit(subreddit_name)
posts = []

for post in subreddit.search(keywords, sort="new", limit=20):
    if "free" in post.title.lower():
        #readable_time = datetime.utcfromtimestamp(post.created_utc).strftime('%A, %B %d %Y at %I:%M %p UTC')
        posts.append({
            "title": post.title.strip(),
            "time": "TBD", #readable_time
            "url": f"https://reddit.com{post.permalink}",
            "location": subreddit_name
        })
if not posts:
    print(" No recent posts found about free events in that city.")
    exit()

prompt = (
    f"A user is looking for valuable upcoming **free events** in {user_input.title()}.\n"
    "Each event includes the title, time, and location. Based on value (free food, free entry, parking, giveaways, etc), "
    "rank and return the **top 3** most valuable events.\n\n"
    "Events:\n"
)

for i, p in enumerate(posts, 1):
    prompt += f"{i}. {p['title']} — {p['time']} — {p['location']}\n"

prompt += "\nList the top 3 in numbered format with 1-sentence reasons why each is valuable."

print("\n Top Free Events near you:\n")
ranking = genai_call(prompt)
print(ranking)
