import os
import praw
import json
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai

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

city_to_subreddit = {
    "nyc": "nyc", "new york": "nyc",
    "los angeles": "LosAngeles", "la": "LosAngeles",
    "chicago": "chicago", "austin": "Austin",
    "san francisco": "bayarea", "sf": "bayarea",
    "seattle": "Seattle", "houston": "houston",
    "boston": "boston", "Washington DC" : "dc", "maryland": "dmv"
}

def search_reddit_events(location, terms, reddit_client_id, reddit_client_secret, reddit_user_agent):

    try: 
        # Initialize Reddit API
        reddit = praw.Reddit(
            client_id=reddit_client_id,
            client_secret=reddit_client_secret,
            user_agent=reddit_user_agent
        )
    except Exception as e: 
        print(f"ERROR INITIALIZING REDDIT API: {e}")
        return []
    
    subreddit_name = city_to_subreddit.get(location.lower())
    if not subreddit_name:
        print(f" Sorry, no subreddit found for inputted city. Try a major city next time")
        return []
    
    try:
        reddit_subreddit_obj = reddit.subreddit(subreddit_name)
    except Exception as e:
        print(f"Error accessing Reddit subreddit '{subreddit_name}': {e}")
        return []
    
    keywords = "free food OR pizza OR snacks OR lunch OR bbq OR dinner OR admission OR parking"
    posts = []

    try: 
        for post in reddit_subreddit_obj.search(keywords, sort="new", limit=20):
            if "free" in post.title.lower():
                #readable_time = datetime.utcfromtimestamp(post.created_utc).strftime('%A, %B %d %Y at %I:%M %p UTC')
                posts.append({
                    "source" : "reddit",
                    "external_id": post.id,
                    "global_id": f"reddit_{post.id}",
                    "title": post.title.strip(),
                    "time": "TBD", #readable_time
                    "url": f"https://reddit.com{post.permalink}",
                    "location": subreddit_name
                })
    except Exception as e:
        print(f"Error searching Reddit for events in {subreddit_name}: {e}")
    return posts

